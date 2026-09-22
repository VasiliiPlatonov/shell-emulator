#!/bin/sh
# Только лог: команды, введённые вручную, пишутся в XML
cd "$(dirname "$0")/.." || exit 1
python3 src/main.py --log logs/stage2_manual.xml
