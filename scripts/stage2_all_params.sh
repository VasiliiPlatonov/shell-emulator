#!/bin/sh
# Все параметры: VFS, лог и стартовый скрипт (остановка на ошибке)
cd "$(dirname "$0")/.." || exit 1
python3 src/main.py --vfs vfs/deep.csv --log logs/stage2.xml --script scripts/startup/stage2.txt
