#!/bin/sh
# Минимальная VFS (только корень). VFS копируется в tmp, т.к. vfs-init её перезаписывает
cd "$(dirname "$0")/.." || exit 1
mkdir -p tmp
cp vfs/minimal.csv tmp/minimal.csv
python3 src/main.py --vfs tmp/minimal.csv --log logs/stage3_minimal.xml \
    --script scripts/startup/stage3.txt
