"""Загрузка и сохранение VFS в формате CSV.

Формат файла (UTF-8, разделитель — запятая)::

    path,type,mtime,data
    /home,dir,2026-09-01T10:00:00,
    /home/user/hello.txt,file,2026-09-01T10:00:00,SGVsbG8K

- ``path`` — полный путь от корня; так задаётся вложенность;
- ``type`` — ``dir`` или ``file``;
- ``mtime`` — время изменения в ISO 8601 (может быть пустым);
- ``data`` — содержимое файла в base64 (у каталогов пусто).

Порядок строк не важен: строки сортируются по глубине пути, поэтому
родитель всегда создаётся раньше потомков.
"""

import base64
import binascii
import csv
from datetime import datetime

from vfs import SEPARATOR, Vfs, VfsDir, VfsError, VfsFile, join_path, \
    split_path

FIELDS = ["path", "type", "mtime", "data"]
TYPE_DIR = "dir"
TYPE_FILE = "file"
FIRST_DATA_LINE = 2


def _parse_mtime(text):
    """Разбирает время изменения; пустая строка — текущее время."""
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError as error:
        raise VfsError(f"неверное время '{text}'") from error


def _make_node(row):
    """Создаёт узел VFS по строке CSV."""
    kind = row.get("type") or ""
    mtime = _parse_mtime(row.get("mtime") or "")
    data = row.get("data") or ""
    if kind == TYPE_DIR:
        if data:
            raise VfsError("у каталога не может быть данных")
        return VfsDir("", mtime)
    if kind == TYPE_FILE:
        try:
            content = base64.b64decode(data, validate=True)
        except binascii.Error as error:
            raise VfsError("неверные данные base64") from error
        return VfsFile("", content, mtime)
    raise VfsError(f"неизвестный тип '{kind}'")


def _read_rows(path):
    """Читает строки CSV вместе с номерами строк файла.

    :raises VfsError: если файл не читается или нет нужных столбцов.
    """
    try:
        with open(path, encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None or \
                    not set(FIELDS[:2]) <= set(reader.fieldnames):
                raise VfsError("нет заголовка path,type,mtime,data")
            return list(enumerate(reader, start=FIRST_DATA_LINE))
    except OSError as error:
        raise VfsError(f"не удалось открыть '{path}': "
                       f"{error.strerror}") from error


def load_csv(path):
    """Загружает VFS из CSV-файла.

    :raises VfsError: с номером строки при ошибке в данных.
    """
    rows = _read_rows(path)
    rows.sort(key=lambda item: len(split_path(item[1]["path"] or "")))
    vfs = Vfs()
    for line, row in rows:
        row_path = row["path"] or ""
        try:
            if not row_path.startswith(SEPARATOR):
                raise VfsError("путь должен начинаться с /")
            parts = split_path(row_path)
            node = _make_node(row)
            if parts:
                vfs.add(parts, node)
            elif node.is_dir:
                vfs.root.mtime = node.mtime
        except VfsError as error:
            raise VfsError(f"{path}, строка {line}: {error}") from error
    return vfs


def save_csv(vfs, path):
    """Сохраняет VFS в CSV-файл (перезаписывает его)."""
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS)
        for parts, node in vfs.walk():
            mtime = node.mtime.isoformat()
            if node.is_dir:
                writer.writerow([join_path(parts), TYPE_DIR, mtime, ""])
            else:
                data = base64.b64encode(node.data).decode("ascii")
                writer.writerow([join_path(parts), TYPE_FILE, mtime, data])
