#!/bin/sh
# Запуск без параметров: все значения по умолчанию
cd "$(dirname "$0")/.." || exit 1
python3 src/main.py 
