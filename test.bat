@echo off
rem Запуск модульных тестов (Windows)
python -m unittest discover -s "%~dp0tests" -v
