#!/bin/sh
# VFS с несколькими файлами, включая двоичный (base64)
cd "$(dirname "$0")/.." || exit 1
mkdir -p tmp
cp vfs/several_files.csv tmp/several_files.csv
python3 src/main.py --vfs tmp/several_files.csv --log logs/stage3_several_files.xml \
    --script scripts/startup/stage3.txt
