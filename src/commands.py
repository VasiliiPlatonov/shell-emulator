"""Команды эмулятора оболочки.

На этапе 1 команды ``ls`` и ``cd`` являются заглушками: они выводят
своё имя и аргументы. Команда ``exit`` завершает работу эмулятора.
"""

from dataclasses import dataclass
from typing import Optional

from shell_parser import ParseError, parse

MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1
LS_OPTIONS = {"-l", "-a", "-la", "-al"}


@dataclass
class CommandResult:
    """Результат выполнения команды.

    :ivar output: текст для вывода пользователю.
    :ivar error: текст ошибки или пустая строка.
    :ivar exit_code: код завершения, если запрошен выход, иначе None.
    """

    output: str = ""
    error: str = ""
    exit_code: Optional[int] = None


def format_stub(name, args):
    """Формирует вывод команды-заглушки: имя и аргументы."""
    quoted = ", ".join(f"'{arg}'" for arg in args)
    return f"{name}: аргументы [{quoted}]"


def cmd_ls(args):
    """Заглушка ls: проверяет опции и выводит имя и аргументы."""
    for arg in args:
        if arg.startswith("-") and arg not in LS_OPTIONS:
            return CommandResult(error=f"ls: неверная опция '{arg}'")
    return CommandResult(output=format_stub("ls", args))


def cmd_cd(args):
    """Заглушка cd: допускает не более одного аргумента."""
    if len(args) > MAX_CD_ARGS:
        return CommandResult(error="cd: слишком много аргументов")
    return CommandResult(output=format_stub("cd", args))


def cmd_exit(args):
    """Команда exit [код]: запрашивает завершение эмулятора."""
    if len(args) > MAX_EXIT_ARGS:
        return CommandResult(error="exit: слишком много аргументов")
    if not args:
        return CommandResult(exit_code=0)
    try:
        return CommandResult(exit_code=int(args[0]))
    except ValueError:
        return CommandResult(
            error=f"exit: требуется числовой аргумент: {args[0]}")


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute(line, env=None):
    """Разбирает строку и выполняет команду.

    :param line: строка, введённая пользователем.
    :param env: переменные окружения (для тестов).
    :return: объект CommandResult.
    """
    try:
        words = parse(line, env)
    except ParseError as error:
        return CommandResult(error=f"ошибка разбора: {error}")
    if not words:
        return CommandResult()
    name, args = words[0], words[1:]
    handler = COMMANDS.get(name)
    if handler is None:
        return CommandResult(error=f"{name}: команда не найдена")
    return handler(args)
