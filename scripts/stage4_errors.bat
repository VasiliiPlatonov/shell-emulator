@echo off
rem Этап 4: обработка ошибок; для каждой ошибки открывается отдельное окно
cd /d "%~dp0.."
chcp 65001 > nul
set ERRORS=ls_bad_option ls_missing cd_not_dir cd_missing cd_many_args
set ERRORS=%ERRORS% wc_no_file wc_directory wc_bad_option
set ERRORS=%ERRORS% cal_bad_month cal_bad_year cal_many_args
for %%n in (%ERRORS%) do (
    python src\main.py --vfs vfs\deep.csv --log logs\stage4_errors.xml --script scripts\startup\errors\%%n.txt
)
