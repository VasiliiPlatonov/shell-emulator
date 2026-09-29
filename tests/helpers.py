"""Общие средства тестов: путь к исходникам, фабрики сеанса и каталогов."""

import os
import sys
import tempfile

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

ENV = {"HOME": "/home/user", "USER": "vasya"}


def make_shell(**kwargs):
    """Создаёт сеанс эмулятора с тестовым окружением.

    Импорт выполняется внутри функции, потому что каталог src
    добавляется в путь поиска модулей при загрузке этого модуля.

    :param kwargs: параметры Shell (vfs_path, log_path и другие).
    :return: объект Shell.
    """
    from shell import Shell
    kwargs.setdefault("env", ENV)
    kwargs.setdefault("user", "tester")
    return Shell(**kwargs)


def vfs_file(name):
    """Путь к тестовому файлу VFS из каталога vfs/."""
    return os.path.join(os.path.dirname(__file__), "..", "vfs", name)


def temp_dir(test_case):
    """Создаёт временный каталог и планирует его удаление после теста.

    :param test_case: текущий тест (для регистрации очистки).
    :return: путь к временному каталогу.
    """
    folder = tempfile.TemporaryDirectory()
    test_case.addCleanup(folder.cleanup)
    return folder.name
