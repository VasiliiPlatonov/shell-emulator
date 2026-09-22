#!/bin/sh
# Справка по параметрам командной строки
cd "$(dirname "$0")/.." || exit 1
python3 src/main.py --help
