#!/bin/sh
# Этап 4: все режимы ls, cd, wc, cal на многоуровневой VFS
cd "$(dirname "$0")/.." || exit 1
python3 src/main.py --vfs vfs/deep.csv --log logs/stage4.xml \
    --script scripts/startup/stage4.txt
