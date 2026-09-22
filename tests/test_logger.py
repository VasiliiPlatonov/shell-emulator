"""Тесты XML-журнала."""

import os
import tempfile
import unittest
import xml.etree.ElementTree as ET

from helpers import ENV
from shell import Shell


class LoggerTest(unittest.TestCase):
    """Проверка записи событий вызова команд."""

    def setUp(self):
        """Создаёт временный каталог для журнала."""
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "log.xml")

    def tearDown(self):
        """Удаляет временный каталог."""
        self.tmp.cleanup()

    def test_events(self):
        """Каждый вызов команды пишется с пользователем и ошибкой."""
        shell = Shell(log_path=self.path, env=ENV, user="vasya")
        shell.execute("ls -l")
        shell.execute("foo bar")
        events = ET.parse(self.path).getroot().findall("event")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].get("user"), "vasya")
        self.assertEqual(events[0].findtext("command"), "ls")
        self.assertEqual([a.text for a in events[0].iter("arg")], ["-l"])
        self.assertFalse(events[0].findtext("error"))
        self.assertIn("не найдена", events[1].findtext("error"))

    def test_append(self):
        """Новый сеанс дополняет существующий журнал."""
        Shell(log_path=self.path, env=ENV, user="u").execute("ls")
        Shell(log_path=self.path, env=ENV, user="u").execute("cd")
        events = ET.parse(self.path).getroot().findall("event")
        self.assertEqual(len(events), 2)

    def test_no_log(self):
        """Без пути журнал не создаётся."""
        Shell(env=ENV, user="u").execute("ls")
        self.assertFalse(os.path.exists(self.path))


if __name__ == "__main__":
    unittest.main()
