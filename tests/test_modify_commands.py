"""Тесты команд mv и touch на тестовой VFS deep.csv."""

import os
import unittest

from helpers import ENV
from shell import Shell
from vfs import split_path
from vfs_csv import load_csv

DEEP = os.path.join(os.path.dirname(__file__), "..", "vfs", "deep.csv")


class ModifyTest(unittest.TestCase):
    """Общая подготовка: VFS deep.csv, текущий каталог /home/user."""

    def setUp(self):
        """Загружает VFS."""
        self.shell = Shell(vfs_path=DEEP, env=ENV, user="u")

    def run_line(self, line):
        """Выполняет строку в тестовом сеансе."""
        return self.shell.execute(line)

    def exists(self, path):
        """Проверяет, что путь есть в VFS."""
        return self.shell.vfs.get(split_path(path)) is not None


class TouchTest(ModifyTest):
    """Проверка touch."""

    def test_create(self):
        """touch создаёт пустые файлы."""
        self.assertEqual(self.run_line("touch a.txt docs/b.txt").error, "")
        self.assertEqual(self.shell.vfs.get(
            split_path("/home/user/a.txt")).data, b"")
        self.assertTrue(self.exists("/home/user/docs/b.txt"))

    def test_update_mtime(self):
        """touch существующего файла обновляет время, не содержимое."""
        node = self.shell.vfs.get(split_path("/home/user/hello.txt"))
        old = node.mtime
        self.run_line("touch hello.txt")
        self.assertGreater(node.mtime, old)
        self.assertEqual(node.data, b"Hello, world!\n")

    def test_errors(self):
        """Нет родителя, нет аргументов, неверная опция."""
        self.assertIn("нет такого", self.run_line("touch no/x.txt").error)
        self.assertIn("не указан", self.run_line("touch").error)
        self.assertIn("неверная опция", self.run_line("touch -r x").error)

    def test_file_not_changed(self):
        """Изменения только в памяти: файл VFS не меняется."""
        self.run_line("touch new.txt")
        self.assertIsNone(load_csv(DEEP).get(split_path(
            "/home/user/new.txt")))


class MvTest(ModifyTest):
    """Проверка mv."""

    def test_rename(self):
        """Переименование файла."""
        self.run_line("mv hello.txt hi.txt")
        self.assertFalse(self.exists("/home/user/hello.txt"))
        self.assertTrue(self.exists("/home/user/hi.txt"))

    def test_into_dir(self):
        """Перенос нескольких файлов в каталог."""
        self.run_line("touch a b")
        self.assertEqual(self.run_line("mv a b /tmp").error, "")
        self.assertTrue(self.exists("/tmp/a"))
        self.assertTrue(self.exists("/tmp/b"))

    def test_move_dir(self):
        """Перенос каталога вместе с содержимым."""
        self.run_line("mv docs /tmp/documents")
        self.assertTrue(self.exists("/tmp/documents/archive/2025/old.txt"))

    def test_replace_file(self):
        """Существующий файл назначения заменяется."""
        self.run_line("mv hello.txt /etc/hostname")
        node = self.shell.vfs.get(split_path("/etc/hostname"))
        self.assertEqual(node.data, b"Hello, world!\n")

    def test_cwd_follows(self):
        """Текущий каталог внутри перемещённого каталога обновляется."""
        self.run_line("cd docs/archive")
        self.run_line("mv /home/user/docs /tmp/d")
        self.assertEqual(self.run_line("pwd").output, "/tmp/d/archive")

    def test_errors(self):
        """Ошибки mv; VFS при этом не меняется."""
        cases = {
            "mv": "источник и назначение",
            "mv nope x": "нет такого",
            "mv docs docs/archive": "собственный подкаталог",
            "mv hello.txt docs/x/y": "нет такого",
            "mv docs /etc/hostname": "заменить файл каталогом",
            "mv hello.txt hello.txt": "совпадают",
            "mv hello.txt docs/archive/2025/old.txt /tmp/x": "не каталог",
            "mv -f a b": "неверная опция",
            "mv / /tmp": "корневой",
        }
        for line, message in cases.items():
            with self.subTest(line=line):
                self.assertIn(message, self.run_line(line).error)
        self.assertTrue(self.exists("/home/user/hello.txt"))
        self.assertTrue(self.exists("/home/user/docs/archive"))

    def test_overwrite_dir(self):
        """Нельзя заменить каталог файлом с тем же именем."""
        self.run_line("touch archive")
        error = self.run_line("mv archive docs").error
        self.assertIn("нельзя перезаписать каталог", error)
        self.assertTrue(self.shell.vfs.get(
            split_path("/home/user/docs/archive")).is_dir)


if __name__ == "__main__":
    unittest.main()
