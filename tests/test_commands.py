"""Тесты команд эмулятора."""

import unittest

from helpers import ENV
from shell import Shell


class CommandsTest(unittest.TestCase):
    """Проверка команд-заглушек, exit и обработки ошибок."""

    def setUp(self):
        """Создаёт сеанс без журнала с тестовым окружением."""
        self.shell = Shell(env=ENV, user="tester")

    def run_line(self, line):
        """Выполняет строку в тестовом сеансе."""
        return self.shell.execute(line)

    def test_ls_stub(self):
        """ls выводит имя и аргументы."""
        result = self.run_line("ls -l $HOME")
        self.assertEqual(result.output, "ls: аргументы ['-l', '/home/user']")
        self.assertEqual(result.error, "")

    def test_ls_bad_option(self):
        """ls с неизвестной опцией — ошибка."""
        self.assertIn("неверная опция", self.run_line("ls -z").error)

    def test_cd_stub(self):
        """cd выводит имя и аргументы."""
        self.assertEqual(self.run_line("cd /tmp").output,
                         "cd: аргументы ['/tmp']")

    def test_cd_too_many(self):
        """cd с двумя аргументами — ошибка."""
        self.assertIn("слишком много", self.run_line("cd a b").error)

    def test_unknown_command(self):
        """Неизвестная команда — ошибка."""
        self.assertEqual(self.run_line("foo").error,
                         "foo: команда не найдена")

    def test_parse_error(self):
        """Незакрытая кавычка — ошибка разбора."""
        self.assertIn("ошибка разбора", self.run_line("ls 'x").error)

    def test_empty_line(self):
        """Пустая строка ничего не делает."""
        result = self.run_line("")
        self.assertEqual((result.output, result.error), ("", ""))

    def test_exit(self):
        """exit без аргументов — код 0, с числом — этот код."""
        self.assertEqual(self.run_line("exit").exit_code, 0)
        self.assertEqual(self.run_line("exit 3").exit_code, 3)

    def test_exit_bad_arg(self):
        """exit с нечисловым аргументом — ошибка, выхода нет."""
        result = self.run_line("exit abc")
        self.assertIsNone(result.exit_code)
        self.assertIn("числовой", result.error)


if __name__ == "__main__":
    unittest.main()
