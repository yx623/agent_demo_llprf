import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def test_init_db_script_creates_expected_tables(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    db_path = tmp_path / "init-db.sqlite3"
    env = os.environ.copy()
    env.update({
        "APP_ENV": "test",
        "LOG_LEVEL": "INFO",
        "OPENAI_API_KEY": "sk-demo-key",
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "OPENAI_MODEL": "gpt-5.4",
        "POSTGRES_DSN": f"sqlite+pysqlite:///{db_path}",
        "REDIS_URL": "redis://localhost:6379/0",
    })
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{repo_root}:{existing_pythonpath}" if existing_pythonpath else str(repo_root)
    )

    completed = subprocess.run(
        [sys.executable, "scripts/init_db.py"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr

    with sqlite3.connect(db_path) as connection:
        table_rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()

    table_names = [name for (name,) in table_rows]

    assert table_names == ["artifacts", "memory_items", "task_runs"]
