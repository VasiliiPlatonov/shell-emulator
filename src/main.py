"""Графический интерфейс эмулятора оболочки (Tkinter)."""

import sys
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from config import parse_args
from script_runner import ScriptError, read_script, run_script
from shell import Shell

FONT = ("Consolas", 11)
SCRIPT_DELAY_MS = 100


class EmulatorApp:
    """Окно эмулятора: поле вывода и строка ввода команд."""

    def __init__(self, root, shell):
        """Создаёт виджеты окна; заголовок содержит имя VFS."""
        self.root = root
        self.shell = shell
        self.history = []
        self.history_pos = 0
        self.output = ScrolledText(root, font=FONT, state="disabled",
                                   bg="black", fg="white", height=24)
        self.output.tag_config("error", foreground="red")
        self.output.tag_config("debug", foreground="gray")
        self.output.pack(fill="both", expand=True)
        frame = tk.Frame(root)
        frame.pack(fill="x")
        self.prompt_label = tk.Label(frame, font=FONT)
        self.prompt_label.pack(side="left")
        self.entry = tk.Entry(frame, font=FONT)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Up>", lambda event: self.scroll_history(-1))
        self.entry.bind("<Down>", lambda event: self.scroll_history(1))
        self.entry.focus_set()
        self.refresh()

    def refresh(self):
        """Обновляет заголовок окна и приглашение (имя VFS)."""
        self.root.title(f"Эмулятор оболочки — {self.shell.vfs_name}")
        self.prompt_label.configure(text=self.shell.prompt)

    def write(self, text, tag=None):
        """Добавляет строку текста в поле вывода."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n", tag)
        self.output.configure(state="disabled")
        self.output.see("end")

    def write_result(self, text, is_error):
        """Вывод для скрипта: ошибки выделяются цветом."""
        self.write(text, "error" if is_error else None)
        self.refresh()

    def on_enter(self, _event=None):
        """Обрабатывает нажатие Enter: выполняет введённую команду."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(self.shell.prompt + line)
        if line.strip():
            self.history.append(line)
        self.history_pos = len(self.history)
        result = self.shell.execute(line)
        if result.output:
            self.write(result.output)
        if result.error:
            self.write(result.error, "error")
        self.refresh()
        if result.exit_code is not None:
            self.root.destroy()

    def scroll_history(self, step):
        """Листает историю команд стрелками вверх/вниз."""
        new_pos = self.history_pos + step
        if not 0 <= new_pos <= len(self.history):
            return
        self.history_pos = new_pos
        self.entry.delete(0, "end")
        if new_pos < len(self.history):
            self.entry.insert(0, self.history[new_pos])

    def run_startup_script(self, path):
        """Выполняет стартовый скрипт; exit в скрипте закрывает окно."""
        try:
            lines = read_script(path)
        except ScriptError as error:
            self.write(str(error), "error")
            return
        if run_script(self.shell, lines, self.write_result) is not None:
            self.root.destroy()


def main(argv=None):
    """Точка входа: разбирает параметры и запускает окно."""
    config = parse_args(argv)
    for line in config.describe():
        print(line)
    shell = Shell(vfs_path=config.vfs_path, log_path=config.log_path)
    root = tk.Tk()
    app = EmulatorApp(root, shell)
    for line in config.describe():
        app.write(line, "debug")
    for line, is_error in shell.messages:
        print(line)
        app.write(line, "error" if is_error else "debug")
    if config.script_path:
        root.after(SCRIPT_DELAY_MS, app.run_startup_script,
                   config.script_path)
    root.mainloop()


if __name__ == "__main__":
    main(sys.argv[1:])
