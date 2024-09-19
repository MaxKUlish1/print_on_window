import tempfile, base64, zlib, asyncio, threading, time
import tkinter as tk

_, ICON_PATH = tempfile.mkstemp()
with open(ICON_PATH, "wb") as icon_file:
    icon_file.write(zlib.decompress(base64.b64decode("eJxjYGAEQgEBBiDJwZDBysAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc=")))
 
MAX_HISTORY = 100
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600

class ScrollingText(tk.Text):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg='black', fg='white', insertbackground='white')
        self.history = []

    def append(self, text):
        self.insert(tk.END, text + '\n')
        self.history.append(text)
        if len(self.history) > MAX_HISTORY:
            self.history.pop(0)
        self.see(tk.END)  # Прокручиваем до конца

class TkinterPrinter:
    windows = {}
    lock = threading.Lock()  # Для синхронизации

    @classmethod
    def print_tkinter(cls, unique_id, data_to_print):
        # Используем блокировку для потокобезопасности
        with cls.lock:
            if unique_id not in cls.windows:
                # Создаем новое окно в отдельном потоке
                thread = threading.Thread(target=cls.create_window, args=(unique_id,))
                thread.start()

        # Теперь можно безопасно добавить текст в виджет
        asyncio.run(cls.add_text_to_window(unique_id, data_to_print))

    @classmethod
    def create_window(cls, unique_id):
        # Создаем окно
        window = tk.Tk()
        window.title(f"{unique_id}")
        window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        window.iconbitmap(default=ICON_PATH)
        window.attributes("-alpha", 0.8)
        
        text_widget = ScrollingText(window, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH)

        # Сохраняем ссылку на окно и текстовый виджет
        with cls.lock:
            cls.windows[unique_id] = (window, text_widget)

        # Обрабатываем закрытие окна
        window.protocol("WM_DELETE_WINDOW", lambda: cls.close_window(unique_id))

        # Запускаем главный цикл этого окна
        window.mainloop()

    @classmethod
    async def add_text_to_window(cls, unique_id, text):
        # Ждем, пока окно будет создано
        while unique_id not in cls.windows:
            await asyncio.sleep(0.1)  # Ожидание

        # Добавляем текст
        with cls.lock:
            _, text_widget = cls.windows[unique_id]
            text_widget.append(text)

    @classmethod
    def close_window(cls, unique_id):
        with cls.lock:
            if unique_id in cls.windows:
                window, _ = cls.windows.pop(unique_id)
                window.destroy()

# Пример использования:
if __name__ == "__main__":
    unique_str = "Окно_1"
    TkinterPrinter.print_tkinter(unique_str, "Текст.")
    time.sleep(1)
    TkinterPrinter.close_window(unique_str)
