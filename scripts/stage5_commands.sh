#!/bin/sh
# Этап 5: все режимы mv и touch; изменения только в памяти
cd "$(dirname "$0")/.." || exit 1
python3 src/main.py --vfs vfs/deep.csv --log logs/stage5.xml \
    --script scripts/startup/stage5.txt
