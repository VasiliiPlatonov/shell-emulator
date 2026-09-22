"""Команды навигации по VFS: ls и cd."""

from result import CommandResult
from vfs import DEFAULT_HOME, VfsError, join_path, normalize, split_path

LS_FLAGS = "la"
MAX_CD_ARGS = 1
OPTION_PREFIX = "-"


def split_options(name, args, allowed):
    """Отделяет опции (``-la``) от операндов.

    :param name: имя команды для сообщения об ошибке.
    :param args: аргументы команды.
    :param allowed: строка допустимых букв опций.
    :return: пара (множество букв опций, список операндов).
    :raises VfsError: при неизвестной опции.
    """
    flags, operands = set(), []
    for arg in args:
        if arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX:
            for letter in arg[1:]:
                if letter not in allowed:
                    raise VfsError(f"{name}: неверная опция '-{letter}'")
                flags.add(letter)
        else:
            operands.append(arg)
    return flags, operands


def format_entry(name, node, long_format):
    """Строка вывода ls для одного элемента."""
    if not long_format:
        return name
    kind = "d" if node.is_dir else "-"
    mtime = node.mtime.strftime("%Y-%m-%d %H:%M")
    return f"{kind} {node.size:>8} {mtime} {name}"


def list_dir(node, flags):
    """Строки вывода ls для содержимого каталога."""
    long_format = "l" in flags
    lines = []
    if "a" in flags:
        lines.append(format_entry(".", node, long_format))
        lines.append(format_entry("..", node, long_format))
    for name in sorted(node.children):
        if name.startswith(".") and "a" not in flags:
            continue
        lines.append(format_entry(name, node.children[name], long_format))
    return lines


def cmd_ls(shell, args):
    """ls [-l] [-a] [путь...]: выводит содержимое каталогов VFS.

    ``-l`` — подробный формат (тип, размер, время изменения, имя),
    ``-a`` — показывать скрытые элементы, а также ``.`` и ``..``.
    """
    try:
        flags, paths = split_options("ls", args, LS_FLAGS)
    except VfsError as error:
        return CommandResult(error=str(error))
    paths = paths or ["."]
    blocks, errors = [], []
    for path in paths:
        node = shell.vfs.get(normalize(path, shell.cwd))
        if node is None:
            errors.append(f"ls: '{path}': нет такого файла или каталога")
        elif not node.is_dir:
            blocks.append([format_entry(path, node, "l" in flags)])
        else:
            lines = list_dir(node, flags)
            if len(paths) > 1:
                lines.insert(0, f"{path}:")
            blocks.append(lines)
    output = "\n\n".join("\n".join(block) for block in blocks)
    return CommandResult(output=output.strip("\n"), error="\n".join(errors))


def cmd_cd(shell, args):
    """cd [путь]: меняет текущий каталог; без аргумента — домашний."""
    if len(args) > MAX_CD_ARGS:
        return CommandResult(error="cd: слишком много аргументов")
    path = args[0] if args else DEFAULT_HOME
    parts = normalize(path, shell.cwd) if args else split_path(path)
    try:
        shell.vfs.get_dir(parts)
    except VfsError as error:
        return CommandResult(error=f"cd: {error}")
    shell.cwd = parts
    return CommandResult()


def cmd_pwd(shell, args):
    """pwd: выводит текущий каталог VFS."""
    if args:
        return CommandResult(error="pwd: команда не принимает аргументов")
    return CommandResult(output=join_path(shell.cwd))
