"""Тесты разбора параметров командной строки."""

import unittest

from config import parse_args
from helpers import make_shell
from shell import vfs_name_from_path


class ConfigTest(unittest.TestCase):
    """Проверка параметров --vfs, --log, --script."""

    def test_defaults(self):
        """Без параметров все пути пустые."""
        config = parse_args([])
        self.assertIsNone(config.vfs_path)
        self.assertIsNone(config.log_path)
        self.assertIsNone(config.script_path)

    def test_all_params(self):
        """Все параметры разбираются и попадают в отладочный вывод."""
        config = parse_args(["--vfs", "a.csv", "--log", "l.xml",
                             "--script", "s.txt"])
        self.assertEqual((config.vfs_path, config.log_path,
                          config.script_path), ("a.csv", "l.xml", "s.txt"))
        text = "\n".join(config.describe())
        for value in ("a.csv", "l.xml", "s.txt"):
            self.assertIn(value, text)

    def test_vfs_name(self):
        """Имя VFS берётся из имени файла без расширения."""
        self.assertEqual(vfs_name_from_path("data/my_vfs.csv"), "my_vfs")
        self.assertEqual(vfs_name_from_path(None), "vfs")
        shell = make_shell(vfs_path="x/deep.csv")
        self.assertEqual(shell.prompt, "deep:/home/user$ ")


if __name__ == "__main__":
    unittest.main()
