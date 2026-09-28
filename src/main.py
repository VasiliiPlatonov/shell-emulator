"""Графический интерфейс эмулятора оболочки (Tkinter)."""

import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from commands import execute

VFS_NAME = "vfs"
PROMPT = "$ "
FONT = ("Consolas", 11)


class EmulatorApp:
    """Окно эмулятора: поле вывода и строка ввода команд."""

    def __init__(self, root, vfs_name=VFS_NAME):
        """Создаёт виджеты окна; заголовок содержит имя VFS."""
        self.root = root
        self.root.title(f"Эмулятор оболочки — {vfs_name}")
        self.history = []
        self.history_pos = 0
        self.output = ScrolledText(root, font=FONT, state="disabled",
                                   bg="black", fg="white", height=24)
        self.output.tag_config("error", foreground="red")
        self.output.pack(fill="both", expand=True)
        frame = tk.Frame(root)
        frame.pack(fill="x")
        tk.Label(frame, text=f"{vfs_name}{PROMPT}", font=FONT).pack(
            side="left")
        self.entry = tk.Entry(frame, font=FONT)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Up>", lambda event: self.scroll_history(-1))
        self.entry.bind("<Down>", lambda event: self.scroll_history(1))
        self.entry.focus_set()
        self.vfs_name = vfs_name

    def write(self, text, tag=None):
        """Добавляет строку текста в поле вывода."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n", tag)
        self.output.configure(state="disabled")
        self.output.see("end")

    def on_enter(self, _event=None):
        """Обрабатывает нажатие Enter: выполняет введённую команду."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(f"{self.vfs_name}{PROMPT}{line}")
        if line.strip():
            self.history.append(line)
        self.history_pos = len(self.history)
        result = execute(line)
        if result.output:
            self.write(result.output)
        if result.error:
            self.write(result.error, "error")
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


def main():
    """Точка входа: запускает окно эмулятора."""
    root = tk.Tk()
    EmulatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
