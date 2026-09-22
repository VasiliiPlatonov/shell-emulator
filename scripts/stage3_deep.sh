#!/bin/sh
# VFS с вложенностью не менее 3 уровней
cd "$(dirname "$0")/.." || exit 1
mkdir -p tmp
cp vfs/deep.csv tmp/deep.csv
python3 src/main.py --vfs tmp/deep.csv --log logs/stage3_deep.xml \
    --script scripts/startup/stage3.txt
