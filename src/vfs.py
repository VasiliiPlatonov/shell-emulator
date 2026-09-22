"""Виртуальная файловая система (VFS), хранящаяся в памяти.

VFS — дерево узлов: каталоги (VfsDir) и файлы (VfsFile). Пути
записываются в стиле UNIX: ``/home/user/notes.txt``.
"""

from datetime import datetime

SEPARATOR = "/"
CURRENT_DIR = "."
PARENT_DIR = ".."
DEFAULT_HOME = "/home/user"


def now():
    """Текущее время с точностью до секунды."""
    return datetime.now().replace(microsecond=0)


class VfsError(Exception):
    """Ошибка работы с VFS (нет пути, неверный тип узла и т. п.)."""


class VfsNode:
    """Базовый узел VFS.

    :ivar name: имя узла (у корня — пустая строка).
    :ivar mtime: время последнего изменения.
    """

    is_dir = False

    def __init__(self, name, mtime=None):
        """Создаёт узел с именем и временем изменения."""
        self.name = name
        self.mtime = mtime or now()


class VfsFile(VfsNode):
    """Файл VFS с двоичным содержимым."""

    def __init__(self, name, data=b"", mtime=None):
        """Создаёт файл; ``data`` — содержимое в байтах."""
        super().__init__(name, mtime)
        self.data = data

    @property
    def size(self):
        """Размер файла в байтах."""
        return len(self.data)


class VfsDir(VfsNode):
    """Каталог VFS: словарь дочерних узлов по имени."""

    is_dir = True

    def __init__(self, name, mtime=None):
        """Создаёт пустой каталог."""
        super().__init__(name, mtime)
        self.children = {}

    @property
    def size(self):
        """Размер каталога — число элементов в нём."""
        return len(self.children)


def split_path(path):
    """Разбивает путь на непустые части: ``/a//b/`` → ``['a', 'b']``."""
    return [part for part in path.split(SEPARATOR) if part]


def normalize(path, cwd=()):
    """Приводит путь к абсолютному списку частей без ``.`` и ``..``.

    :param path: абсолютный или относительный путь.
    :param cwd: текущий каталог как список частей.
    :return: список частей абсолютного пути.
    """
    parts = [] if path.startswith(SEPARATOR) else list(cwd)
    for part in split_path(path):
        if part == PARENT_DIR:
            if parts:
                parts.pop()
        elif part != CURRENT_DIR:
            parts.append(part)
    return parts


def join_path(parts):
    """Собирает абсолютный путь из частей: ``['a', 'b']`` → ``/a/b``."""
    return SEPARATOR + SEPARATOR.join(parts)


class Vfs:
    """Дерево VFS с операциями поиска и добавления узлов."""

    def __init__(self):
        """Создаёт VFS, содержащую только корневой каталог."""
        self.root = VfsDir("")

    @classmethod
    def default(cls):
        """VFS по умолчанию: пустой домашний каталог ``/home/user``."""
        vfs = cls()
        vfs.make_dirs(split_path(DEFAULT_HOME))
        return vfs

    def get(self, parts):
        """Возвращает узел по частям абсолютного пути или None."""
        node = self.root
        for part in parts:
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node

    def get_dir(self, parts):
        """Возвращает каталог по пути.

        :raises VfsError: если пути нет или это не каталог.
        """
        node = self.get(parts)
        if node is None:
            raise VfsError(f"{join_path(parts)}: нет такого файла "
                           "или каталога")
        if not node.is_dir:
            raise VfsError(f"{join_path(parts)}: это не каталог")
        return node

    def add(self, parts, node):
        """Добавляет узел по пути; родительский каталог должен существовать.

        :raises VfsError: если родителя нет или узел уже существует.
        """
        if not parts:
            raise VfsError("нельзя заменить корневой каталог")
        parent = self.get_dir(parts[:-1])
        if parts[-1] in parent.children:
            raise VfsError(f"{join_path(parts)}: уже существует")
        node.name = parts[-1]
        parent.children[node.name] = node
        return node

    def remove(self, parts):
        """Удаляет узел из родительского каталога и возвращает его."""
        parent = self.get_dir(parts[:-1])
        parent.mtime = now()
        return parent.children.pop(parts[-1])

    def check_move(self, src, dst):
        """Проверяет, что узел src можно переместить по пути dst.

        :raises VfsError: с описанием причины, если перемещение
            невозможно.
        """
        node = self.get(src)
        if node is None:
            raise VfsError(f"{join_path(src)}: нет такого файла "
                           "или каталога")
        if not src:
            raise VfsError("нельзя переместить корневой каталог")
        if dst == src:
            raise VfsError(f"{join_path(src)}: источник и назначение "
                           "совпадают")
        if node.is_dir and dst[:len(src)] == src:
            raise VfsError(f"нельзя переместить {join_path(src)} "
                           "в собственный подкаталог")
        self._check_target(node, dst)

    def _check_target(self, node, dst):
        """Проверяет путь назначения для перемещения узла node.

        :raises VfsError: если нет родителя назначения или по пути
            назначения лежит узел, который нельзя заменить.
        """
        self.get_dir(dst[:-1])
        target = self.get(dst)
        if target is None:
            return
        if target.is_dir:
            raise VfsError(f"{join_path(dst)}: нельзя перезаписать каталог")
        if node.is_dir:
            raise VfsError(f"{join_path(dst)}: нельзя заменить файл "
                           "каталогом")

    def move(self, src, dst):
        """Перемещает (переименовывает) узел; файл по dst заменяется."""
        self.check_move(src, dst)
        node = self.remove(src)
        parent = self.get_dir(dst[:-1])
        parent.children.pop(dst[-1], None)
        node.name = dst[-1]
        parent.children[node.name] = node
        parent.mtime = now()

    def make_dirs(self, parts):
        """Создаёт каталог вместе с недостающими родителями."""
        for depth in range(1, len(parts) + 1):
            if self.get(parts[:depth]) is None:
                self.add(parts[:depth], VfsDir(parts[depth - 1]))

    def walk(self):
        """Обходит все узлы, кроме корня: пары (части пути, узел)."""
        stack = [([], self.root)]
        while stack:
            parts, node = stack.pop()
            if parts:
                yield parts, node
            if node.is_dir:
                for name in sorted(node.children, reverse=True):
                    stack.append((parts + [name], node.children[name]))

    def count(self):
        """Возвращает пару (число каталогов, число файлов)."""
        dirs = files = 0
        for _, node in self.walk():
            if node.is_dir:
                dirs += 1
            else:
                files += 1
        return dirs, files
