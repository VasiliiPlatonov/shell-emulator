#!/bin/sh
# Несуществующий скрипт: ошибка в окне
cd "$(dirname "$0")/.." || exit 1
python3 src/main.py --script scripts/startup/missing.txt
