"""Команды wc и cal."""

import calendar
from datetime import date

from fs_commands import split_options
from result import CommandResult
from vfs import VfsError, normalize

WC_FLAGS = "lwc"
MIN_MONTH, MAX_MONTH = 1, 12
MIN_YEAR, MAX_YEAR = 1, 9999
YEAR_ONLY_ARGS = 1
MONTH_YEAR_ARGS = 2
WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MONTHS = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]


def count_data(data):
    """Считает строки (символы ``\\n``), слова и байты."""
    return {"l": data.count(b"\n"), "w": len(data.split()),
            "c": len(data)}


def format_counts(counts, flags, name):
    """Строка вывода wc в порядке строки, слова, байты."""
    columns = [f"{counts[flag]:>7}" for flag in WC_FLAGS if flag in flags]
    return " ".join(columns + [name]).rstrip()


def read_file(shell, path):
    """Возвращает содержимое файла VFS.

    :raises VfsError: если файла нет или это каталог.
    """
    node = shell.vfs.get(normalize(path, shell.cwd))
    if node is None:
        raise VfsError(f"wc: {path}: нет такого файла или каталога")
    if node.is_dir:
        raise VfsError(f"wc: {path}: это каталог")
    return node.data


def cmd_wc(shell, args):
    """wc [-l] [-w] [-c] файл...: число строк, слов и байт в файлах.

    Без опций выводятся все три числа. Для нескольких файлов
    добавляется строка ``итого``.
    """
    try:
        flags, paths = split_options("wc", args, WC_FLAGS)
    except VfsError as error:
        return CommandResult(error=str(error))
    if not paths:
        return CommandResult(error="wc: не указан файл")
    flags = flags or set(WC_FLAGS)
    lines, errors = [], []
    total = {flag: 0 for flag in WC_FLAGS}
    for path in paths:
        try:
            counts = count_data(read_file(shell, path))
        except VfsError as error:
            errors.append(str(error))
            continue
        for flag in WC_FLAGS:
            total[flag] += counts[flag]
        lines.append(format_counts(counts, flags, path))
    if len(paths) > 1:
        lines.append(format_counts(total, flags, "итого"))
    return CommandResult(output="\n".join(lines), error="\n".join(errors))


class RussianCalendar(calendar.TextCalendar):
    """Текстовый календарь с неделей с понедельника и русскими названиями."""

    def formatweekday(self, day, width):
        """Сокращённое название дня недели."""
        return WEEKDAYS[day][:width].center(width)

    def formatmonthname(self, theyear, themonth, width, withyear=True):
        """Название месяца (с годом или без), выровненное по центру."""
        name = MONTHS[themonth]
        if withyear:
            name = f"{name} {theyear}"
        return name.center(width)


def parse_number(text, low, high, what):
    """Разбирает целое число в диапазоне [low, high].

    :raises ValueError: с понятным сообщением при ошибке.
    """
    try:
        value = int(text)
    except ValueError as error:
        raise ValueError(f"cal: неверный {what}: {text}") from error
    if not low <= value <= high:
        raise ValueError(f"cal: {what} вне диапазона {low}..{high}: "
                         f"{text}")
    return value


def cmd_cal(_shell, args, today=None):
    """cal [[месяц] год]: выводит календарь.

    Без аргументов — текущий месяц, с одним — весь год,
    с двумя — указанный месяц указанного года.
    """
    today = today or date.today()
    cal = RussianCalendar(firstweekday=calendar.MONDAY)
    try:
        if not args:
            text = cal.formatmonth(today.year, today.month)
        elif len(args) == YEAR_ONLY_ARGS:
            year = parse_number(args[0], MIN_YEAR, MAX_YEAR, "год")
            text = cal.formatyear(year)
        elif len(args) == MONTH_YEAR_ARGS:
            month = parse_number(args[0], MIN_MONTH, MAX_MONTH, "месяц")
            year = parse_number(args[1], MIN_YEAR, MAX_YEAR, "год")
            text = cal.formatmonth(year, month)
        else:
            return CommandResult(error="cal: слишком много аргументов")
    except ValueError as error:
        return CommandResult(error=str(error))
    return CommandResult(output=text.rstrip())
