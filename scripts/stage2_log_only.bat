@echo off
rem Только лог: команды, введённые вручную, пишутся в XML
cd /d "%~dp0.."
chcp 65001 > nul
python src\main.py --log logs\stage2_manual.xml
