import subprocess
import sys
from pathlib import Path

from app.core.paths import get_repo_root_cached


def test_verify_env_script_accepts_example_contract():
    root = get_repo_root_cached()
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "verify_env.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Environment contract: OK" in result.stdout
