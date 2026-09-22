"""Журнал вызовов команд в формате XML.

Структура файла::

    <log>
      <event time="2026-09-22T10:00:00" user="vasya">
        <command>ls</command>
        <args><arg>-l</arg></args>
        <error>ls: неверная опция '-z'</error>
      </event>
    </log>

Элемент ``error`` пуст, если команда выполнилась без ошибок.
"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime


class XmlLogger:
    """Записывает события вызова команд в XML-файл.

    Если путь не задан, журнал не ведётся. Файл перезаписывается
    целиком после каждого события, поэтому всегда остаётся корректным
    XML-документом.
    """

    def __init__(self, path, user):
        """Открывает журнал; существующий корректный файл дополняется."""
        self.path = path
        self.user = user
        self.root = self._load()

    def _load(self):
        """Читает существующий журнал или создаёт новый корень."""
        if self.path and os.path.exists(self.path):
            try:
                root = ET.parse(self.path).getroot()
                if root.tag == "log":
                    return root
            except ET.ParseError:
                pass
        return ET.Element("log")

    def log(self, command, args, error=""):
        """Добавляет событие вызова команды и сохраняет файл.

        :param command: имя команды.
        :param args: список аргументов.
        :param error: сообщение об ошибке или пустая строка.
        """
        if not self.path:
            return
        event = ET.SubElement(self.root, "event", {
            "time": datetime.now().isoformat(timespec="seconds"),
            "user": self.user,
        })
        ET.SubElement(event, "command").text = command
        args_node = ET.SubElement(event, "args")
        for arg in args:
            ET.SubElement(args_node, "arg").text = arg
        ET.SubElement(event, "error").text = error
        self.save()

    def save(self):
        """Сохраняет журнал в файл с отступами.

        Каталог журнала создаётся, если его нет.
        """
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        tree = ET.ElementTree(self.root)
        ET.indent(tree)
        tree.write(self.path, encoding="utf-8", xml_declaration=True)
