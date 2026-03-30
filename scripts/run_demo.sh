#!/usr/bin/env bash
set -euo pipefail

# 这个脚本只是一个很薄的包装层，目的是把教学演示命令固定成
# `bash scripts/run_demo.sh <subcommand>` 这种更容易记忆的形式。
python -m app.cli "$@"
