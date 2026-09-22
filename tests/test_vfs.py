"""Тесты VFS: пути, дерево, загрузка и сохранение CSV, vfs-init."""

import os
import shutil
import tempfile
import unittest

from helpers import ENV
from shell import Shell
from vfs import Vfs, VfsError, VfsFile, join_path, normalize, split_path
from vfs_csv import load_csv, save_csv

VFS_DIR = os.path.join(os.path.dirname(__file__), "..", "vfs")


def vfs_file(name):
    """Путь к тестовому файлу VFS из каталога vfs/."""
    return os.path.join(VFS_DIR, name)


class PathTest(unittest.TestCase):
    """Проверка работы с путями."""

    def test_normalize(self):
        """Относительные пути, . и .. приводятся к абсолютным."""
        self.assertEqual(normalize("docs/../x/.", ["home"]), ["home", "x"])
        self.assertEqual(normalize("/a//b/"), ["a", "b"])
        self.assertEqual(normalize("../../..", ["a"]), [])

    def test_join(self):
        """Части пути собираются в строку."""
        self.assertEqual(join_path(["a", "b"]), "/a/b")
        self.assertEqual(join_path([]), "/")


class VfsTreeTest(unittest.TestCase):
    """Проверка операций с деревом."""

    def test_default(self):
        """VFS по умолчанию содержит /home/user."""
        vfs = Vfs.default()
        self.assertTrue(vfs.get(["home", "user"]).is_dir)
        self.assertEqual(vfs.count(), (2, 0))

    def test_add_errors(self):
        """Нельзя добавить узел без родителя или повторно."""
        vfs = Vfs()
        with self.assertRaises(VfsError):
            vfs.add(split_path("/no/file"), VfsFile("file"))
        vfs.add(["f"], VfsFile("f"))
        with self.assertRaises(VfsError):
            vfs.add(["f"], VfsFile("f"))


class CsvTest(unittest.TestCase):
    """Проверка загрузки тестовых VFS и обработки ошибок."""

    def test_minimal(self):
        """Минимальная VFS — только корень."""
        self.assertEqual(load_csv(vfs_file("minimal.csv")).count(), (0, 0))

    def test_several_files(self):
        """Несколько файлов, включая двоичный."""
        vfs = load_csv(vfs_file("several_files.csv"))
        self.assertEqual(vfs.count(), (0, 4))
        self.assertEqual(vfs.get(["data.bin"]).data,
                         bytes([0, 1, 2, 255, 254, 10, 128]))

    def test_deep(self):
        """Не менее трёх уровней вложенности."""
        vfs = load_csv(vfs_file("deep.csv"))
        node = vfs.get(split_path("/home/user/docs/archive/2025/old.txt"))
        self.assertEqual(node.data, b"old file\n")

    def test_broken(self):
        """Ошибки в CSV сообщаются с номером строки."""
        for name in ("no_parent", "bad_type", "bad_base64", "no_header"):
            with self.subTest(name=name), self.assertRaises(VfsError):
                load_csv(vfs_file(f"broken/{name}.csv"))
        with self.assertRaisesRegex(VfsError, "строка 3"):
            load_csv(vfs_file("broken/no_parent.csv"))

    def test_missing_file(self):
        """Несуществующий файл — VfsError."""
        with self.assertRaises(VfsError):
            load_csv(vfs_file("nope.csv"))

    def test_round_trip(self):
        """Сохранённая VFS загружается обратно без потерь."""
        vfs = load_csv(vfs_file("deep.csv"))
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "copy.csv")
            save_csv(vfs, path)
            copy = load_csv(path)
        self.assertEqual([join_path(p) for p, _ in vfs.walk()],
                         [join_path(p) for p, _ in copy.walk()])


class VfsInitTest(unittest.TestCase):
    """Проверка команды vfs-init."""

    def setUp(self):
        """Копирует deep.csv во временный каталог."""
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "deep.csv")
        shutil.copy(vfs_file("deep.csv"), self.path)

    def tearDown(self):
        """Удаляет временный каталог."""
        self.tmp.cleanup()

    def test_loaded_on_start(self):
        """VFS загружается при запуске, имя берётся из файла."""
        shell = Shell(vfs_path=self.path, env=ENV, user="u")
        self.assertEqual(shell.vfs.count(), (8, 7))
        self.assertEqual(shell.vfs_name, "deep")

    def test_bad_vfs_falls_back(self):
        """При ошибке загрузки используется VFS по умолчанию."""
        shell = Shell(vfs_path=vfs_file("broken/bad_type.csv"), env=ENV)
        self.assertTrue(shell.messages[0][1])
        self.assertEqual(shell.vfs.count(), (2, 0))

    def test_vfs_init(self):
        """vfs-init заменяет VFS в памяти и перезаписывает файл."""
        shell = Shell(vfs_path=self.path, env=ENV, user="u")
        result = shell.execute("vfs-init")
        self.assertEqual(result.error, "")
        self.assertEqual(shell.vfs.count(), (2, 0))
        self.assertEqual(load_csv(self.path).count(), (2, 0))

    def test_vfs_init_args(self):
        """vfs-init с аргументами — ошибка, VFS не меняется."""
        shell = Shell(vfs_path=self.path, env=ENV, user="u")
        self.assertIn("аргумент", shell.execute("vfs-init x").error)
        self.assertEqual(shell.vfs.count(), (8, 7))


if __name__ == "__main__":
    unittest.main()
