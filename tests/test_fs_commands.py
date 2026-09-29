"""Тесты команд ls, cd, pwd на тестовой VFS deep.csv."""

import unittest
from functools import cached_property

from helpers import make_shell, vfs_file


class FsCommandsTest(unittest.TestCase):
    """Проверка навигации по VFS."""

    @cached_property
    def shell(self):
        """Сеанс с загруженной VFS deep.csv; каталог — /home/user."""
        return make_shell(vfs_path=vfs_file("deep.csv"))

    def run_line(self, line):
        """Выполняет строку в тестовом сеансе."""
        return self.shell.execute(line)

    def test_ls_cwd(self):
        """ls без аргументов: текущий каталог, скрытые не видны."""
        self.assertEqual(self.run_line("ls").output.split("\n"),
                         ["docs", "hello.txt", "pictures"])

    def test_ls_all(self):
        """ls -a показывает . .. и скрытые файлы."""
        output = self.run_line("ls -a").output.split("\n")
        self.assertEqual(output[:3], [".", "..", ".profile"])

    def test_ls_long(self):
        """ls -l: тип, размер, время, имя."""
        line = self.run_line("ls -l docs").output.split("\n")[0]
        self.assertTrue(line.startswith("d "))
        self.assertTrue(line.endswith(" archive"))
        self.assertIn("2026-09-01 10:00", line)

    def test_ls_combined_flags(self):
        """Опции можно объединять: -la."""
        self.assertEqual(self.run_line("ls -la /tmp").error, "")

    def test_ls_file_and_many(self):
        """ls для файла выводит его имя; для нескольких — заголовки."""
        self.assertEqual(self.run_line("ls hello.txt").output, "hello.txt")
        output = self.run_line("ls /etc /tmp").output
        self.assertEqual(output, "/etc:\nhostname\n\n/tmp:")

    def test_ls_errors(self):
        """Неизвестная опция и несуществующий путь — ошибки."""
        self.assertIn("неверная опция '-z'", self.run_line("ls -z").error)
        result = self.run_line("ls nope docs")
        self.assertIn("нет такого файла", result.error)
        self.assertIn("archive", result.output)

    def test_cd_relative_and_parent(self):
        """cd по относительному пути и через .."""
        self.run_line("cd docs/archive/2025")
        self.assertEqual(self.run_line("pwd").output,
                         "/home/user/docs/archive/2025")
        self.run_line("cd ../../..")
        self.assertEqual(self.run_line("pwd").output, "/home/user")

    def test_cd_absolute_and_home(self):
        """cd / и cd без аргумента (домой)."""
        self.run_line("cd /")
        self.assertEqual(self.shell.cwd, [])
        self.run_line("cd")
        self.assertEqual(self.shell.cwd, ["home", "user"])

    def test_cd_errors(self):
        """cd в файл, в несуществующий путь, с двумя аргументами."""
        self.assertIn("не каталог", self.run_line("cd hello.txt").error)
        self.assertIn("нет такого", self.run_line("cd nope").error)
        self.assertIn("слишком много", self.run_line("cd a b").error)
        self.assertEqual(self.shell.cwd, ["home", "user"])

    def test_prompt_shows_cwd(self):
        """Приглашение содержит имя VFS и текущий каталог."""
        self.run_line("cd /etc")
        self.assertEqual(self.shell.prompt, "deep:/etc$ ")


if __name__ == "__main__":
    unittest.main()
