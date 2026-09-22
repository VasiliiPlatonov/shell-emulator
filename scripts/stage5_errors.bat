@echo off
rem Этап 5: обработка ошибок mv и touch; для каждой ошибки отдельное окно
cd /d "%~dp0.."
chcp 65001 > nul
set ERRORS=touch_no_file touch_no_parent mv_no_args mv_missing
set ERRORS=%ERRORS% mv_into_itself mv_dir_over_file mv_many_to_file mv_no_parent
for %%n in (%ERRORS%) do (
    python src\main.py --vfs vfs\deep.csv --log logs\stage5_errors.xml --script scripts\startup\errors\%%n.txt
)
