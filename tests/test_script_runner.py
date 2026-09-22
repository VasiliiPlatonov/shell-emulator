"""Тесты выполнения стартового скрипта."""

import unittest

from helpers import ENV
from script_runner import ScriptError, read_script, run_script
from shell import Shell


class ScriptRunnerTest(unittest.TestCase):
    """Проверка вывода скрипта и остановки на первой ошибке."""

    def setUp(self):
        """Создаёт сеанс и буфер вывода."""
        self.shell = Shell(env=ENV, user="u")
        self.lines = []

    def write(self, text, is_error):
        """Сохраняет вывод скрипта."""
        self.lines.append((text, is_error))

    def test_echo_input_and_output(self):
        """На экран выводится и ввод, и вывод; комментарии пропускаются."""
        run_script(self.shell, ["# комментарий", "", "pwd"], self.write)
        self.assertEqual(self.lines, [
            ("vfs:/home/user$ pwd", False),
            ("/home/user", False),
        ])

    def test_stop_on_first_error(self):
        """После первой ошибки команды не выполняются."""
        run_script(self.shell, ["ls", "foo", "cd /"], self.write)
        texts = [text for text, _ in self.lines]
        self.assertIn("foo: команда не найдена", texts)
        self.assertIn("Скрипт остановлен: ошибка в строке 2", texts)
        self.assertNotIn("vfs:/home/user$ cd /", texts)
        self.assertEqual(self.shell.cwd, ["home", "user"])

    def test_exit(self):
        """exit в скрипте возвращает код выхода."""
        code = run_script(self.shell, ["exit 2", "ls"], self.write)
        self.assertEqual(code, 2)

    def test_missing_file(self):
        """Несуществующий скрипт — ScriptError."""
        with self.assertRaises(ScriptError):
            read_script("no/such/script.txt")


if __name__ == "__main__":
    unittest.main()
