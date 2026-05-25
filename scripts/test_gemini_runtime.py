"""Validate Gemini runtime in isolation from the FastAPI backend.

This script intentionally avoids importing the application, embeddings, OCR,
torch, or worker modules. It validates only the Gemini SDK layer and the stable
protobuf/gRPC runtime pins.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from importlib import metadata
from pathlib import Path
from typing import Any

from packaging import version
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"


def load_env_file() -> None:
    """Load a minimal .env file without introducing a dotenv dependency."""
    if not ENV_FILE.exists():
        return

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def assert_dependency(name: str, requirement: str) -> str:
    """Validate a simple >=,< requirement."""
    installed = metadata.version(name)
    parsed = version.parse(installed)
    for part in requirement.split(","):
        part = part.strip()
        if part.startswith(">=") and parsed < version.parse(part[2:]):
            raise RuntimeError(f"{name}=={installed} violates {requirement}")
        if part.startswith("<") and parsed >= version.parse(part[1:]):
            raise RuntimeError(f"{name}=={installed} violates {requirement}")
    return installed


def validate_dependency_layer() -> dict[str, str]:
    """Validate Gemini and protobuf/gRPC package compatibility."""
    versions = {
        "protobuf": assert_dependency("protobuf", ">=6.31.1,<7.0.0"),
        "grpcio": assert_dependency("grpcio", ">=1.76.0,<2.0.0"),
        "grpcio-tools": assert_dependency("grpcio-tools", ">=1.76.0,<2.0.0"),
        "grpcio-status": assert_dependency("grpcio-status", ">=1.76.0,<2.0.0"),
        "google-genai": assert_dependency("google-genai", ">=2.6.0,<3.0.0"),
    }

    for legacy_name in ("google-generativeai", "google-ai-generativelanguage"):
        try:
            versions[legacy_name] = metadata.version(legacy_name)
        except metadata.PackageNotFoundError:
            continue
        raise RuntimeError(f"{legacy_name}=={versions[legacy_name]} is legacy and should not be installed")

    return versions


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
)
async def generate_structured_response(api_key: str, model: str, prompt: str) -> dict[str, Any]:
    """Call Gemini through the modern async HTTP SDK with structured output."""
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(api_version="v1beta"),
    )
    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=256,
                response_mime_type="application/json",
                response_json_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "summary": {"type": "string"},
                    },
                    "required": ["status", "summary"],
                },
            ),
        )
        text = response.text or "{}"
        return json.loads(text)
    finally:
        await client.aio.aclose()


async def main() -> int:
    parser = argparse.ArgumentParser(description="Validate isolated Gemini runtime.")
    parser.add_argument("--dependency-only", action="store_true", help="Validate package compatibility without calling Gemini.")
    parser.add_argument("--model", default=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    parser.add_argument(
        "--prompt",
        default="Return JSON with status='ok' and a short summary of this runtime validation.",
    )
    args = parser.parse_args()

    load_env_file()
    versions = validate_dependency_layer()
    print(json.dumps({"dependency_layer": versions}, indent=2, sort_keys=True))

    if args.dependency_only:
        return 0

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY to run the Gemini request validation")

    result = await generate_structured_response(api_key=api_key, model=args.model, prompt=args.prompt)
    print(json.dumps({"gemini_response": result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
