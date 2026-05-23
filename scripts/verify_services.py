from __future__ import annotations

import argparse
import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def tcp_check(name: str, host: str, port: int, timeout: float = 3.0) -> tuple[str, bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return name, True, f"{host}:{port}"
    except OSError as exc:
        return name, False, f"{host}:{port} ({exc})"


def http_check(name: str, url: str, timeout: float = 5.0) -> tuple[str, bool, str]:
    try:
        request = Request(url, headers={"User-Agent": "resume-intelligence-env-check"})
        with urlopen(request, timeout=timeout) as response:
            return name, 200 <= response.status < 500, f"{url} -> HTTP {response.status}"
    except Exception as exc:
        return name, False, f"{url} ({exc})"


def host_port_from_url(value: str, default_port: int) -> tuple[str, int]:
    parsed = urlparse(value.replace("+asyncpg", "").replace("+psycopg", ""))
    return parsed.hostname or "localhost", parsed.port or default_port


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify local infrastructure services.")
    parser.add_argument("--include-external", action="store_true", help="Also check external provider APIs such as Gemini.")
    args = parser.parse_args()

    env = {**parse_env(ROOT / ".env.example"), **parse_env(ROOT / ".env"), **os.environ}
    db_host, db_port = host_port_from_url(env["DATABASE_URL"], 5432)
    redis_host, redis_port = host_port_from_url(env["REDIS_URL"], 6379)
    neo4j_host, neo4j_port = host_port_from_url(env["NEO4J_URI"], 7687)

    checks = [
        tcp_check("postgres", db_host, db_port),
        tcp_check("redis", redis_host, redis_port),
        http_check("qdrant", env["QDRANT_URL"].rstrip("/") + "/healthz"),
        http_check("minio", env["S3_ENDPOINT_URL"].rstrip("/") + "/minio/health/live"),
        http_check("mlflow", env["MLFLOW_TRACKING_URI"].rstrip("/") + "/health"),
        tcp_check("neo4j", neo4j_host, neo4j_port),
    ]
    if args.include_external:
        checks.append(http_check("gemini", "https://generativelanguage.googleapis.com/$discovery/rest?version=v1beta"))

    failed = False
    for name, ok, detail in checks:
        status = "OK" if ok else "FAIL"
        print(f"{status:4} {name:10} {detail}")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
