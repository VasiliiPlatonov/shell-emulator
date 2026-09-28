"""Тесты команд эмулятора."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from commands import execute  # noqa: E402

ENV = {"HOME": "/home/user"}


class CommandsTest(unittest.TestCase):
    """Проверка команд-заглушек, exit и обработки ошибок."""

    def test_ls_stub(self):
        """ls выводит имя и аргументы."""
        result = execute("ls -l $HOME", ENV)
        self.assertEqual(result.output, "ls: аргументы ['-l', '/home/user']")
        self.assertEqual(result.error, "")

    def test_ls_bad_option(self):
        """ls с неизвестной опцией — ошибка."""
        self.assertIn("неверная опция", execute("ls -z", ENV).error)

    def test_cd_stub(self):
        """cd выводит имя и аргументы."""
        self.assertEqual(execute("cd /tmp", ENV).output,
                         "cd: аргументы ['/tmp']")

    def test_cd_too_many(self):
        """cd с двумя аргументами — ошибка."""
        self.assertIn("слишком много", execute("cd a b", ENV).error)

    def test_unknown_command(self):
        """Неизвестная команда — ошибка."""
        self.assertEqual(execute("foo", ENV).error,
                         "foo: команда не найдена")

    def test_parse_error(self):
        """Незакрытая кавычка — ошибка разбора."""
        self.assertIn("ошибка разбора", execute("ls 'x", ENV).error)

    def test_empty_line(self):
        """Пустая строка ничего не делает."""
        result = execute("", ENV)
        self.assertEqual((result.output, result.error), ("", ""))

    def test_exit(self):
        """exit без аргументов — код 0, с числом — этот код."""
        self.assertEqual(execute("exit", ENV).exit_code, 0)
        self.assertEqual(execute("exit 3", ENV).exit_code, 3)

    def test_exit_bad_arg(self):
        """exit с нечисловым аргументом — ошибка, выхода нет."""
        result = execute("exit abc", ENV)
        self.assertIsNone(result.exit_code)
        self.assertIn("числовой", result.error)


if __name__ == "__main__":
    unittest.main()
