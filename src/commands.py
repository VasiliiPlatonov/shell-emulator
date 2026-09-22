"""Команды эмулятора оболочки.

Каждая команда — функция ``cmd_<имя>(shell, args)``, возвращающая
объект CommandResult. Команды регистрируются в словаре COMMANDS.
"""

from fs_commands import cmd_cd, cmd_ls, cmd_pwd
from result import CommandResult
from text_commands import cmd_cal, cmd_wc
from vfs_commands import cmd_vfs_init

MAX_EXIT_ARGS = 1


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
    "pwd": cmd_pwd,
    "wc": cmd_wc,
    "cal": cmd_cal,
    "exit": cmd_exit,
    "vfs-init": cmd_vfs_init,
}
