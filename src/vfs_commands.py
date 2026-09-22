"""Служебные команды для работы с VFS."""

from result import CommandResult
from vfs import Vfs
from vfs_csv import save_csv


def cmd_vfs_init(shell, args):
    """vfs-init: заменяет текущую VFS на VFS по умолчанию.

    Физическое представление VFS (файл --vfs) тоже очищается:
    в него записывается VFS по умолчанию.
    """
    if args:
        return CommandResult(error="vfs-init: команда не принимает "
                                   "аргументов")
    shell.set_vfs(Vfs.default())
    if not shell.vfs_path:
        return CommandResult(output="VFS заменена на VFS по умолчанию")
    try:
        save_csv(shell.vfs, shell.vfs_path)
    except OSError as error:
        return CommandResult(error=f"vfs-init: не удалось записать "
                                   f"'{shell.vfs_path}': {error.strerror}")
    return CommandResult(output="VFS заменена на VFS по умолчанию, "
                                f"файл {shell.vfs_path} перезаписан")
