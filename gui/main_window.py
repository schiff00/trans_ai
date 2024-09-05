import tkinter as tk
import os
import sys

# 현재 파일의 디렉토리를 기준으로 상위 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_operations import FileHandler

class GameDialogueTranslator:
    def __init__(self, master):
        self.master = master
        self.master.title("Game Dialogue Translator")
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.master, text="Enter dialogue:")
        self.label.pack()

        self.text_entry = tk.Entry(self.master)
        self.text_entry.pack()

        self.translate_button = tk.Button(self.master, text="Translate", command=self.translate)
        self.translate_button.pack()

        self.result_label = tk.Label(self.master, text="")
        self.result_label.pack()

    def translate(self):
        dialogue = self.text_entry.get()
        translated_dialogue = self.simple_translate(dialogue)
        self.result_label.config(text=translated_dialogue)

    def simple_translate(self, text):
        # 간단한 번역 기능 (예시)
        return text[::-1]  # 텍스트를 뒤집어서 반환