import subprocess
import sys
from pathlib import Path


def test_verify_env_script_accepts_example_contract():
    root = Path(__file__).resolve().parents[4]
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "verify_env.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Environment contract: OK" in result.stdout
