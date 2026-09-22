"""Тесты команд эмулятора."""

import unittest

from helpers import ENV
from shell import Shell


class CommandsTest(unittest.TestCase):
    """Проверка общего разбора команд, exit и обработки ошибок."""

    def setUp(self):
        """Создаёт сеанс без журнала с тестовым окружением."""
        self.shell = Shell(env=ENV, user="tester")

    def run_line(self, line):
        """Выполняет строку в тестовом сеансе."""
        return self.shell.execute(line)

    def test_env_expansion(self):
        """Переменные окружения раскрываются перед вызовом команды."""
        self.assertEqual(self.run_line("cd $HOME").error, "")
        self.assertEqual(self.run_line("pwd").output, "/home/user")

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
