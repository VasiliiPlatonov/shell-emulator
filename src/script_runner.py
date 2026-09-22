"""Выполнение стартового скрипта эмулятора.

Скрипт — текстовый файл, одна команда в строке. Пустые строки и
строки, начинающиеся с ``#``, пропускаются. Выполнение прекращается
на первой ошибке.
"""

COMMENT_PREFIX = "#"


class ScriptError(Exception):
    """Ошибка чтения стартового скрипта."""


def read_script(path):
    """Читает строки скрипта.

    :raises ScriptError: если файл не удаётся прочитать.
    """
    try:
        with open(path, encoding="utf-8") as file:
            return file.read().splitlines()
    except OSError as error:
        raise ScriptError(
            f"не удалось прочитать скрипт '{path}': {error.strerror}"
        ) from error


def is_command_line(line):
    """Проверяет, что строка содержит команду, а не комментарий."""
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith(COMMENT_PREFIX)


def run_script(shell, lines, write):
    """Выполняет строки скрипта, имитируя диалог с пользователем.

    :param shell: объект Shell.
    :param lines: строки скрипта.
    :param write: функция вывода ``write(text, is_error)``.
    :return: код выхода, если скрипт вызвал exit, иначе None.
    """
    for number, line in enumerate(lines, start=1):
        if not is_command_line(line):
            continue
        write(shell.prompt + line, False)
        result = shell.execute(line)
        if result.output:
            write(result.output, False)
        if result.error:
            write(result.error, True)
            write(f"Скрипт остановлен: ошибка в строке {number}", True)
            return None
        if result.exit_code is not None:
            return result.exit_code
    return None
