"""Команды, изменяющие VFS в памяти: mv и touch.

Изменения не записываются в файл VFS.
"""

from fs_commands import split_options
from result import CommandResult
from vfs import VfsError, VfsFile, join_path, normalize, now

MIN_MV_ARGS = 2
SINGLE_SOURCE = 1
NO_FLAGS = ""


def touch_one(shell, path):
    """Создаёт пустой файл или обновляет время изменения узла."""
    parts = normalize(path, shell.cwd)
    node = shell.vfs.get(parts)
    if node is not None:
        node.mtime = now()
        return
    shell.vfs.get_dir(parts[:-1])
    shell.vfs.add(parts, VfsFile(parts[-1]))


def cmd_touch(shell, args):
    """touch файл...: создаёт пустые файлы или обновляет время изменения.

    Родительский каталог нового файла должен существовать.
    """
    try:
        _, paths = split_options("touch", args, NO_FLAGS)
    except VfsError as error:
        return CommandResult(error=str(error))
    if not paths:
        return CommandResult(error="touch: не указан файл")
    errors = []
    for path in paths:
        try:
            touch_one(shell, path)
        except VfsError as error:
            errors.append(f"touch: {error}")
    return CommandResult(error="\n".join(errors))


def move_target(shell, src, dst_parts):
    """Путь назначения: внутрь каталога dst или сам dst."""
    node = shell.vfs.get(dst_parts)
    if node is not None and node.is_dir:
        return dst_parts + normalize(src, shell.cwd)[-1:]
    return dst_parts


def fix_cwd(shell, src, dst):
    """Если текущий каталог был внутри перемещённого, меняет путь."""
    if shell.cwd[:len(src)] == src:
        shell.cwd = dst + shell.cwd[len(src):]


def cmd_mv(shell, args):
    """mv источник... назначение: перемещает или переименовывает.

    Если назначение — существующий каталог, источники переносятся
    в него. Иначе источник должен быть один, и он переименовывается;
    существующий файл назначения заменяется.
    """
    try:
        _, paths = split_options("mv", args, NO_FLAGS)
    except VfsError as error:
        return CommandResult(error=str(error))
    if len(paths) < MIN_MV_ARGS:
        return CommandResult(error="mv: нужно указать источник "
                                   "и назначение")
    *sources, dst = paths
    dst_parts = normalize(dst, shell.cwd)
    dst_node = shell.vfs.get(dst_parts)
    dst_is_dir = dst_node is not None and dst_node.is_dir
    if len(sources) > SINGLE_SOURCE and not dst_is_dir:
        return CommandResult(error=f"mv: {join_path(dst_parts)}: "
                                   "это не каталог")
    errors = []
    for src in sources:
        src_parts = normalize(src, shell.cwd)
        target = move_target(shell, src, dst_parts)
        try:
            shell.vfs.move(src_parts, target)
        except VfsError as error:
            errors.append(f"mv: {error}")
            continue
        fix_cwd(shell, src_parts, target)
    return CommandResult(error="\n".join(errors))
