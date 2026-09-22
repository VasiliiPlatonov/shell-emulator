"""Команды эмулятора оболочки.

Каждая команда — функция ``cmd_<имя>(shell, args)``, возвращающая
объект CommandResult. Команды регистрируются в словаре COMMANDS.
"""

from result import CommandResult
from vfs_commands import cmd_vfs_init

MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1
LS_OPTIONS = {"-l", "-a", "-la", "-al"}


def format_stub(name, args):
    """Формирует вывод команды-заглушки: имя и аргументы."""
    quoted = ", ".join(f"'{arg}'" for arg in args)
    return f"{name}: аргументы [{quoted}]"


def cmd_ls(_shell, args):
    """Заглушка ls: проверяет опции и выводит имя и аргументы."""
    for arg in args:
        if arg.startswith("-") and arg not in LS_OPTIONS:
            return CommandResult(error=f"ls: неверная опция '{arg}'")
    return CommandResult(output=format_stub("ls", args))


def cmd_cd(_shell, args):
    """Заглушка cd: допускает не более одного аргумента."""
    if len(args) > MAX_CD_ARGS:
        return CommandResult(error="cd: слишком много аргументов")
    return CommandResult(output=format_stub("cd", args))


def cmd_exit(_shell, args):
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
    "vfs-init": cmd_vfs_init,
}
