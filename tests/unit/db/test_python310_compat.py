import os
import subprocess
import sysconfig
from pathlib import Path


def test_run_status_imports_under_python310():
    repo_root = Path(__file__).resolve().parents[3]
    env = os.environ.copy()
    purelib = sysconfig.get_path("purelib")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{purelib}:{existing_pythonpath}" if existing_pythonpath else purelib

    completed = subprocess.run(
        ["python3.10", "-c", "from app.db.models import RunStatus; print(RunStatus.RUNNING.value)"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "running"
