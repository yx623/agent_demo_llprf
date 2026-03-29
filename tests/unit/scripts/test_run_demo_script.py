from pathlib import Path


def test_run_demo_script_exists_and_has_shebang():
    script = Path("scripts/run_demo.sh")

    assert script.exists()
    assert script.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash")
