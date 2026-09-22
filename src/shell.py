"""Ядро эмулятора: состояние сеанса и выполнение команд."""

import getpass
import os

from commands import COMMANDS, CommandResult
from shell_parser import ParseError, parse
from xml_logger import XmlLogger

DEFAULT_VFS_NAME = "vfs"


def vfs_name_from_path(path):
    """Возвращает имя VFS: имя файла без расширения или имя по умолчанию."""
    if not path:
        return DEFAULT_VFS_NAME
    base = os.path.basename(os.path.normpath(path))
    return os.path.splitext(base)[0] or DEFAULT_VFS_NAME


class Shell:
    """Сеанс эмулятора: разбирает строки, вызывает команды, ведёт лог.

    :ivar env: переменные окружения для раскрытия ``$NAME``.
    :ivar user: имя пользователя реальной ОС.
    :ivar logger: журнал вызовов команд.
    :ivar vfs_name: имя текущей VFS.
    """

    def __init__(self, vfs_path=None, log_path=None, env=None, user=None):
        """Создаёт сеанс.

        :param vfs_path: путь к VFS; имя файла становится именем VFS.
        :param log_path: путь к XML-журналу (None — без журнала).
        :param env: переменные окружения (по умолчанию ``os.environ``).
        :param user: имя пользователя (по умолчанию из ОС).
        """
        self.env = os.environ if env is None else env
        self.user = user or getpass.getuser()
        self.logger = XmlLogger(log_path, self.user)
        self.vfs_path = vfs_path
        self.vfs_name = vfs_name_from_path(vfs_path)

    @property
    def prompt(self):
        """Приглашение к вводу."""
        return f"{self.vfs_name}$ "

    def execute(self, line):
        """Разбирает строку, выполняет команду и пишет событие в лог.

        :param line: строка, введённая пользователем.
        :return: объект CommandResult.
        """
        try:
            words = parse(line, self.env)
        except ParseError as error:
            result = CommandResult(error=f"ошибка разбора: {error}")
            self.logger.log(line, [], result.error)
            return result
        if not words:
            return CommandResult()
        name, args = words[0], words[1:]
        handler = COMMANDS.get(name)
        if handler is None:
            result = CommandResult(error=f"{name}: команда не найдена")
        else:
            result = handler(self, args)
        self.logger.log(name, args, result.error)
        return result
