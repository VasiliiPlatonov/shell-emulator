#!/bin/sh
# Ошибки загрузки VFS: для каждого файла открывается окно с сообщением
cd "$(dirname "$0")/.." || exit 1
for name in no_parent bad_type bad_base64 no_header; do
    python3 src/main.py --vfs "vfs/broken/$name.csv"
done
python3 src/main.py --vfs vfs/no_such_file.csv
