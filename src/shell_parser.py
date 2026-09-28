"""Парсер командной строки эмулятора.

Разбивает строку на слова с учётом кавычек и раскрывает переменные
окружения реальной ОС в формате ``$NAME`` и ``${NAME}``.
"""

import os
import re

VAR_PATTERN = re.compile(r"\$(\w+)|\$\{(\w+)\}")
SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'


class ParseError(Exception):
    """Ошибка разбора командной строки (например, незакрытая кавычка)."""


def expand_vars(text, env=None):
    """Раскрывает переменные окружения в строке.

    Неизвестная переменная заменяется пустой строкой, как в sh.
    Знак ``$`` без имени переменной остаётся без изменений.

    :param text: исходная строка.
    :param env: словарь переменных (по умолчанию ``os.environ``).
    :return: строка с подставленными значениями.
    """
    if env is None:
        env = os.environ

    def replace(match):
        name = match.group(1) or match.group(2)
        return env.get(name, "")

    return VAR_PATTERN.sub(replace, text)


def _read_quoted(line, start, quote):
    """Читает содержимое кавычек, начиная с позиции после открывающей.

    :return: пара (содержимое, позиция после закрывающей кавычки).
    :raises ParseError: если закрывающая кавычка не найдена.
    """
    end = line.find(quote, start)
    if end < 0:
        raise ParseError(f"незакрытая кавычка {quote}")
    return line[start:end], end + 1


def _read_plain(line, start):
    """Читает фрагмент слова без кавычек до пробела или кавычки.

    :return: пара (фрагмент, позиция после фрагмента).
    """
    end = start
    while end < len(line) and not line[end].isspace() \
            and line[end] not in (SINGLE_QUOTE, DOUBLE_QUOTE):
        end += 1
    return line[start:end], end


def _read_word(line, pos, env):
    """Читает одно слово, склеивая фрагменты в кавычках и без них.

    :return: тройка (слово, были ли кавычки, позиция после слова).
    """
    word = ""
    quoted = False
    while pos < len(line) and not line[pos].isspace():
        char = line[pos]
        if char == SINGLE_QUOTE:
            part, pos = _read_quoted(line, pos + 1, char)
        elif char == DOUBLE_QUOTE:
            part, pos = _read_quoted(line, pos + 1, char)
            part = expand_vars(part, env)
        else:
            part, pos = _read_plain(line, pos)
            part = expand_vars(part, env)
        quoted = quoted or char in (SINGLE_QUOTE, DOUBLE_QUOTE)
        word += part
    return word, quoted, pos


def parse(line, env=None):
    """Разбивает строку на список слов с раскрытием переменных.

    Внутри одинарных кавычек переменные не раскрываются, внутри
    двойных и вне кавычек — раскрываются. Соседние фрагменты без
    пробела между ними склеиваются в одно слово. Слово, ставшее
    пустым после раскрытия переменных вне кавычек, отбрасывается (как в sh).

    :param line: введённая пользователем строка.
    :param env: словарь переменных окружения (для тестов).
    :return: список слов; пустой список для пустой строки.
    :raises ParseError: при незакрытой кавычке.
    """
    words = []
    pos = 0
    while pos < len(line):
        if line[pos].isspace():
            pos += 1
            continue
        word, quoted, pos = _read_word(line, pos, env)
        if word or quoted:
            words.append(word)
    return words
