#!/bin/sh
# Этап 5: обработка ошибок mv и touch; для каждой ошибки отдельное окно
cd "$(dirname "$0")/.." || exit 1
for name in touch_no_file touch_no_parent mv_no_args mv_missing \
        mv_into_itself mv_dir_over_file mv_many_to_file mv_no_parent; do
    python3 src/main.py --vfs vfs/deep.csv --log logs/stage5_errors.xml \
        --script "scripts/startup/errors/$name.txt"
done
