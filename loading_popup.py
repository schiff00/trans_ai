import tkinter as tk
from tkinter import ttk

class LoadingPopup(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("로딩 중")
        self.geometry("300x100")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # 팝업 창을 화면 중앙에 위치
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # 로딩 메시지
        self.label = ttk.Label(self, text="파일 로드 중...", font=("Helvetica", 12))
        self.label.pack(pady=20)

        # 프로그레스 바
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.start()

    def close(self):
        self.progress.stop()
        self.destroy()
