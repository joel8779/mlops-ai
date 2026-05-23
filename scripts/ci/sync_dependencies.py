from __future__ import annotations

import re
from pathlib import Path


PINNED = re.compile(r"^[A-Za-z0-9_.-]+(\[[A-Za-z0-9_,.-]+\])?==[^#\s]+")
ALLOWED_PREFIXES = ("#", "-r ", "--")


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith(ALLOWED_PREFIXES):
            continue
        if not PINNED.match(line):
            errors.append(f"{path}:{line_number}: dependency must be pinned with == ({line})")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    files = [root / "apps/api/requirements.txt", root / "apps/api/requirements-dev.txt"]
    errors = [error for path in files for error in validate_file(path)]
    if errors:
        print("Dependency sync validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Dependency sync validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
