"""Параметры командной строки эмулятора."""

import argparse
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Config:
    """Настройки запуска эмулятора.

    :ivar vfs_path: путь к физическому расположению VFS.
    :ivar log_path: путь к лог-файлу (XML).
    :ivar script_path: путь к стартовому скрипту.
    """

    vfs_path: Optional[str] = None
    log_path: Optional[str] = None
    script_path: Optional[str] = None

    def describe(self):
        """Возвращает строки отладочного вывода всех параметров."""
        return [
            "Параметры запуска:",
            f"  --vfs    = {self.vfs_path}",
            f"  --log    = {self.log_path}",
            f"  --script = {self.script_path}",
        ]


def build_arg_parser():
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell-emulator",
        description="Эмулятор оболочки UNIX-подобной ОС с GUI.")
    parser.add_argument("--vfs", dest="vfs_path", metavar="PATH",
                        help="путь к физическому расположению VFS")
    parser.add_argument("--log", dest="log_path", metavar="PATH",
                        help="путь к лог-файлу в формате XML")
    parser.add_argument("--script", dest="script_path", metavar="PATH",
                        help="путь к стартовому скрипту")
    return parser


def parse_args(argv: Optional[List[str]] = None):
    """Разбирает аргументы командной строки в объект Config.

    :param argv: список аргументов (по умолчанию ``sys.argv[1:]``).
    :return: объект Config.
    """
    namespace = build_arg_parser().parse_args(argv)
    return Config(namespace.vfs_path, namespace.log_path,
                  namespace.script_path)
