"""Тесты команд wc и cal."""

import os
import unittest
from datetime import date

from helpers import ENV
from shell import Shell
from text_commands import cmd_cal

SEVERAL = os.path.join(os.path.dirname(__file__), "..", "vfs",
                       "several_files.csv")


class WcTest(unittest.TestCase):
    """Проверка wc на VFS several_files.csv."""

    def setUp(self):
        """Загружает VFS; текущий каталог — корень."""
        self.shell = Shell(vfs_path=SEVERAL, env=ENV, user="u")

    def run_line(self, line):
        """Выполняет строку в тестовом сеансе."""
        return self.shell.execute(line)

    def test_all_counts(self):
        """Без опций: строки, слова, байты."""
        self.assertEqual(self.run_line("wc notes.txt").output.split(),
                         ["3", "6", "28", "notes.txt"])

    def test_options(self):
        """-l и -w выводят только выбранные числа."""
        self.assertEqual(self.run_line("wc -l notes.txt").output.split(),
                         ["3", "notes.txt"])
        self.assertEqual(self.run_line("wc -wc /notes.txt").output.split(),
                         ["6", "28", "/notes.txt"])

    def test_binary_empty_and_utf8(self):
        """Байты считаются по содержимому, а не по символам."""
        self.assertEqual(self.run_line("wc -c data.bin").output.split(),
                         ["7", "data.bin"])
        self.assertEqual(self.run_line("wc empty.txt").output.split(),
                         ["0", "0", "0", "empty.txt"])
        self.assertEqual(self.run_line("wc -c readme.txt").output.split(),
                         ["19", "readme.txt"])

    def test_total(self):
        """Для нескольких файлов выводится итог."""
        lines = self.run_line("wc -l notes.txt empty.txt").output
        self.assertEqual(lines.split("\n")[-1].split(), ["3", "итого"])

    def test_errors(self):
        """Нет файла, нет аргументов, неверная опция."""
        self.assertIn("нет такого", self.run_line("wc nope").error)
        self.assertIn("не указан", self.run_line("wc").error)
        self.assertIn("неверная опция", self.run_line("wc -x a").error)

    def test_directory(self):
        """wc для каталога — ошибка."""
        shell = Shell(env=ENV, user="u")
        self.assertIn("это каталог", shell.execute("wc /home").error)


class CalTest(unittest.TestCase):
    """Проверка cal."""

    def test_month_year(self):
        """cal 9 2026: сентябрь 2026 начинается со вторника."""
        lines = cmd_cal(None, ["9", "2026"]).output.split("\n")
        self.assertEqual(lines[0].strip(), "Сентябрь 2026")
        self.assertEqual(lines[1], "Пн Вт Ср Чт Пт Сб Вс")
        self.assertEqual(lines[2], "    1  2  3  4  5  6")

    def test_current_month(self):
        """Без аргументов — текущий месяц."""
        output = cmd_cal(None, [], today=date(2024, 2, 10)).output
        self.assertIn("Февраль 2024", output)
        self.assertIn("28", output)

    def test_year(self):
        """С одним аргументом — все 12 месяцев года."""
        output = cmd_cal(None, ["2026"]).output
        self.assertIn("2026", output.split("\n")[0])
        for name in ("Январь", "Декабрь"):
            self.assertIn(name, output)

    def test_errors(self):
        """Неверный месяц, год, лишние аргументы."""
        self.assertIn("вне диапазона", cmd_cal(None, ["13", "2026"]).error)
        self.assertIn("неверный год", cmd_cal(None, ["abc"]).error)
        self.assertIn("слишком много", cmd_cal(None, ["1", "2", "3"]).error)


if __name__ == "__main__":
    unittest.main()
