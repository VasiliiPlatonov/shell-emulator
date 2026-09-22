#!/bin/sh
# Скрипт с exit: окно закроется само
cd "$(dirname "$0")/.." || exit 1
python3 src/main.py --script scripts/startup/exit.txt
