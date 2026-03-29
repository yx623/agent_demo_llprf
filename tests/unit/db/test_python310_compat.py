import os
import shutil
import subprocess
import sysconfig
from pathlib import Path

import pytest


def test_run_status_imports_under_python310():
    python310 = shutil.which("python3.10")
    if python310 is None:
        pytest.skip("当前环境未安装 python3.10")

    repo_root = Path(__file__).resolve().parents[3]
    env = os.environ.copy()
    purelib = sysconfig.get_path("purelib")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{purelib}:{existing_pythonpath}" if existing_pythonpath else purelib

    completed = subprocess.run(
        [python310, "-c", "from app.db.models import RunStatus; print(RunStatus.RUNNING.value)"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "running"
