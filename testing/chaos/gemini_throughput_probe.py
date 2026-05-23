from __future__ import annotations

import asyncio
import os

import google.generativeai as genai


async def generate(model_name: str, prompt: str) -> str:
    model = genai.GenerativeModel(model_name)
    response = await asyncio.to_thread(model.generate_content, prompt)
    return response.text


async def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Set GEMINI_API_KEY before running Gemini throughput probe")
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    concurrency = int(os.getenv("GEMINI_PROBE_CONCURRENCY", "5"))
    await asyncio.gather(*(generate(model_name, "Return a one sentence health check.") for _ in range(concurrency)))
    print(f"completed={concurrency} model={model_name}")


if __name__ == "__main__":
    asyncio.run(main())
