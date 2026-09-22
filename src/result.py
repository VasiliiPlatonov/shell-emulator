"""Результат выполнения команды эмулятора."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CommandResult:
    """Результат выполнения команды.

    :ivar output: текст для вывода пользователю.
    :ivar error: текст ошибки или пустая строка.
    :ivar exit_code: код завершения, если запрошен выход, иначе None.
    """

    output: str = ""
    error: str = ""
    exit_code: Optional[int] = None
