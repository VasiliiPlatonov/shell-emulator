#!/bin/sh
# Запуск эмулятора оболочки (Linux/macOS)
cd "$(dirname "$0")" && python3 src/main.py "$@"
