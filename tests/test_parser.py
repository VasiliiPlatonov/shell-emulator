"""Тесты парсера командной строки."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from shell_parser import ParseError, expand_vars, parse  # noqa: E402

ENV = {"HOME": "/home/user", "USER": "vasya"}


class ExpandVarsTest(unittest.TestCase):
    """Проверка раскрытия переменных окружения."""

    def test_simple(self):
        """$NAME заменяется значением."""
        self.assertEqual(expand_vars("$HOME/docs", ENV), "/home/user/docs")

    def test_braces(self):
        """${NAME} заменяется значением."""
        self.assertEqual(expand_vars("${USER}_x", ENV), "vasya_x")

    def test_unknown(self):
        """Неизвестная переменная становится пустой строкой."""
        self.assertEqual(expand_vars("a$NOPE", ENV), "a")

    def test_lone_dollar(self):
        """Одиночный $ не меняется."""
        self.assertEqual(expand_vars("5$", ENV), "5$")


class ParseTest(unittest.TestCase):
    """Проверка разбиения строки на слова."""

    def test_empty(self):
        """Пустая строка даёт пустой список."""
        self.assertEqual(parse("   ", ENV), [])

    def test_words(self):
        """Слова разделяются пробелами."""
        self.assertEqual(parse("ls  -l  /tmp", ENV), ["ls", "-l", "/tmp"])

    def test_expand(self):
        """Переменные раскрываются вне кавычек."""
        self.assertEqual(parse("cd $HOME", ENV), ["cd", "/home/user"])

    def test_double_quotes(self):
        """В двойных кавычках переменные раскрываются, пробелы сохраняются."""
        self.assertEqual(parse('ls "$USER dir"', ENV), ["ls", "vasya dir"])

    def test_single_quotes(self):
        """В одинарных кавычках переменные не раскрываются."""
        self.assertEqual(parse("ls '$HOME'", ENV), ["ls", "$HOME"])

    def test_glue(self):
        """Соседние фрагменты склеиваются в одно слово."""
        self.assertEqual(parse("a\"b c\"'d'", ENV), ["ab cd"])

    def test_empty_expansion_dropped(self):
        """Пустая переменная вне кавычек не создаёт слово."""
        self.assertEqual(parse("ls $NOPE x", ENV), ["ls", "x"])

    def test_empty_quotes_kept(self):
        """Пустые кавычки дают пустое слово."""
        self.assertEqual(parse('ls "$NOPE"', ENV), ["ls", ""])

    def test_unclosed_quote(self):
        """Незакрытая кавычка вызывает ParseError."""
        with self.assertRaises(ParseError):
            parse('ls "abc', ENV)


if __name__ == "__main__":
    unittest.main()
