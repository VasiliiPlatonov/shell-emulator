#!/bin/sh
# Этап 4: обработка ошибок; для каждой ошибки открывается отдельное окно
cd "$(dirname "$0")/.." || exit 1
for name in ls_bad_option ls_missing cd_not_dir cd_missing cd_many_args \
        wc_no_file wc_directory wc_bad_option \
        cal_bad_month cal_bad_year cal_many_args; do
    python3 src/main.py --vfs vfs/deep.csv --log logs/stage4_errors.xml \
        --script "scripts/startup/errors/$name.txt"
done
