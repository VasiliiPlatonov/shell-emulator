"""Тесты XML-журнала."""

import os
import unittest
from functools import cached_property
from xml.etree import ElementTree as element_tree

from helpers import make_shell, temp_dir


class LoggerTest(unittest.TestCase):
    """Проверка записи событий вызова команд."""

    @cached_property
    def path(self):
        """Путь к журналу во временном каталоге теста."""
        return os.path.join(temp_dir(self), "log.xml")

    def test_events(self):
        """Каждый вызов команды пишется с пользователем и ошибкой."""
        shell = make_shell(log_path=self.path, user="vasya")
        shell.execute("ls -l")
        shell.execute("foo bar")
        events = element_tree.parse(self.path).getroot().findall("event")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].get("user"), "vasya")
        self.assertEqual(events[0].findtext("command"), "ls")
        self.assertEqual([a.text for a in events[0].iter("arg")], ["-l"])
        self.assertFalse(events[0].findtext("error"))
        self.assertIn("не найдена", events[1].findtext("error"))

    def test_append(self):
        """Новый сеанс дополняет существующий журнал."""
        make_shell(log_path=self.path).execute("ls")
        make_shell(log_path=self.path).execute("cd")
        events = element_tree.parse(self.path).getroot().findall("event")
        self.assertEqual(len(events), 2)

    def test_no_log(self):
        """Без пути журнал не создаётся."""
        make_shell().execute("ls")
        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
