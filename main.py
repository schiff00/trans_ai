import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import logging
import sys
import google.generativeai as genai
import pandas as pd
import threading
import os

class GameDialogueTranslator(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("AI 번역기 by studiobside")
        self.center_window(1200, 800)
        self.pack(fill=tk.BOTH, expand=True)
        self.log_text = None
        self.create_log_window()
        self.load_api_key()
        self.setup_gemini()
        self.system_prompt = ""
        self.create_widgets()
        self.bind_buttons()
        self.excel_data = None

    def load_api_key(self):
        try:
            with open('api_key.txt', 'r') as file:
                self.api_key = file.read().strip()
        except FileNotFoundError:
            self.log_message("API 키 파일을 찾을 수 없습니다.")
            self.api_key = None

    def setup_gemini(self):
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.log_message("Gemini API가 성공적으로 연결되었습니다.")
                
                # 언어를 명시적으로 지정하여 'Hello world!' 메시지 전송
                response = self.model.generate_content("Respond in Korean: Hello world!")
                self.log_message(f"Gemini의 응답: {response.text}")
            except Exception as e:
                self.log_message(f"Gemini API 연결 중 오류 발생: {str(e)}")
        else:
            self.log_message("API 키가 없어 Gemini를 설정할 수 없습니다.")

    def center_window(self, width, height):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # 전체 상단 프레임
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # 왼쪽 프레임 (엑셀 로드 버튼들을 위한)
        left_frame = tk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 오른쪽 프레임 (시스템 프롬프트 설정과 프롬프트 보내기 버튼을 위한)
        right_frame = tk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 대사 엑셀 로드 프레임
        dialogue_frame = tk.Frame(left_frame)
        dialogue_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.load_excel_button = tk.Button(dialogue_frame, text="대사 엑셀 로드", width=20)
        self.load_excel_button.pack(side=tk.LEFT, padx=5)
        self.loaded_file_label = tk.Label(dialogue_frame, text="로드된 파일: 없음", anchor="w")
        self.loaded_file_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 캐릭터 시트 로드 프레임
        character_frame = tk.Frame(left_frame)
        character_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.load_character_sheet_button = tk.Button(character_frame, text="캐릭터 시트 로드", width=20)
        self.load_character_sheet_button.pack(side=tk.LEFT, padx=5)
        self.loaded_character_label = tk.Label(character_frame, text="로드된 파일: 없음", anchor="w")
        self.loaded_character_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 글로서리 엑셀 로드 프레임
        glossary_frame = tk.Frame(left_frame)
        glossary_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.load_glossary_button = tk.Button(glossary_frame, text="글로서리 엑셀 로드", width=20)
        self.load_glossary_button.pack(side=tk.LEFT, padx=5)
        self.loaded_glossary_label = tk.Label(glossary_frame, text="로드된 파일: 없음", anchor="w")
        self.loaded_glossary_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 시스템 프롬프트 설정 버튼
        self.set_system_prompt_button = tk.Button(right_frame, text="시스템 프롬프트 설정")
        self.set_system_prompt_button.pack(side=tk.TOP, padx=5, pady=5)

        # 프롬프트 보내기 버튼
        self.send_prompt_button = tk.Button(right_frame, text="프롬프트 보내기")
        self.send_prompt_button.pack(side=tk.TOP, padx=5, pady=5)

        # 대사 엑셀의 시트 선택 콤보
        self.sheet_select_combo = ttk.Combobox(left_frame, values=["시트1", "시트2", "시트3"])
        self.sheet_select_combo.pack(side=tk.TOP, padx=5, pady=5)
        self.sheet_select_combo.set("시트 선택")  # 기본값 설정
        self.sheet_select_combo.bind("<<ComboboxSelected>>", self.on_sheet_selected)

        # 번역 버튼 프레임
        translate_button_frame = tk.Frame(self)
        translate_button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # 선택 번역하기 버튼
        self.translate_selected_button = tk.Button(translate_button_frame, text="선택 번역하기")
        self.translate_selected_button.pack(side=tk.RIGHT, padx=5)

        # 전체 번역하기 버튼
        self.translate_all_button = tk.Button(translate_button_frame, text="전체 번역하기")
        self.translate_all_button.pack(side=tk.RIGHT, padx=5)

        # 트리뷰 리스트
        self.tree = ttk.Treeview(self, columns=("A", "B", "C"), show='headings')
        self.tree.heading("A", text="Column A")
        self.tree.heading("B", text="Column B")
        self.tree.heading("C", text="Column C")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 대사 창 프레임
        dialogue_frame = tk.Frame(self)
        dialogue_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # 원본 대사 창
        self.original_dialogue = tk.Text(dialogue_frame, height=3)
        self.original_dialogue.pack(fill=tk.X, pady=5)

        # 번역된 대사 창
        self.translated_dialogue = tk.Text(dialogue_frame, height=3)
        self.translated_dialogue.pack(fill=tk.X, pady=5)

        # 엑셀로 저장하기 버튼
        self.save_to_excel_button = tk.Button(self, text="엑셀로 저장하기")
        self.save_to_excel_button.pack(side=tk.BOTTOM, pady=10)

    def on_sheet_selected(self, event):
        selected_sheet = self.sheet_select_combo.get()
        self.log_message(f"선택된 시트: {selected_sheet}")

    def bind_buttons(self):
        self.load_excel_button.config(command=self.on_load_excel)
        self.load_character_sheet_button.config(command=self.on_load_character_sheet)
        self.load_glossary_button.config(command=self.on_load_glossary)
        self.translate_selected_button.config(command=self.on_translate_selected)
        self.translate_all_button.config(command=self.on_translate_all)
        self.save_to_excel_button.config(command=self.on_save_to_excel)
        self.set_system_prompt_button.config(command=self.set_system_prompt)
        self.send_prompt_button.config(command=self.get_user_prompt)

    def on_load_excel(self):
        self.load_file("대사 엑셀", self.load_excel_button, self.loaded_file_label)

    def on_load_character_sheet(self):
        self.load_file("캐릭터 시트", self.load_character_sheet_button, self.loaded_character_label)

    def on_load_glossary(self):
        self.load_file("글로서리 엑셀", self.load_glossary_button, self.loaded_glossary_label)

    def load_file(self, file_type, button, label):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            self.log_message(f"{file_type} 로드 중...")
            button.config(state=tk.DISABLED)
            file_name = os.path.basename(file_path)
            label.config(text=f"로드된 파일: {file_name}")
            threading.Thread(target=self.load_excel_async, args=(file_path, file_type, button), daemon=True).start()
        else:
            self.log_message("파일 선택이 취소되었습니다.")

    def load_excel_async(self, file_path, file_type, button):
        try:
            # 엑셀 파일 로드
            self.excel_data = pd.read_excel(file_path, sheet_name=None)
            
            # 시트 이름 가져오기
            sheet_names = list(self.excel_data.keys())
            
            # GUI 업데이트는 메인 스레드에서 실행
            self.master.after(0, self.update_gui_after_load, sheet_names, file_path, file_type)
        except Exception as e:
            self.master.after(0, self.log_message, f"{file_type} 로드 중 오류 발생: {str(e)}")
        finally:
            self.master.after(0, lambda: button.config(state=tk.NORMAL))

    def update_gui_after_load(self, sheet_names, file_path, file_type):
        # 콤보박스 업데이트
        self.sheet_select_combo['values'] = sheet_names
        if sheet_names:
            self.sheet_select_combo.set(sheet_names[0])
        
        self.log_message(f"{file_type}이(가) 성공적으로 로드되었습니다: {file_path}")
        self.log_message(f"사용 가능한 시트: {', '.join(sheet_names)}")

    def on_translate_selected(self):
        self.log_message("선택 번역하기 버튼이 클릭되었습니다.")

    def on_translate_all(self):
        self.log_message("전체 번역하기 버튼이 클릭되었습니다.")

    def on_save_to_excel(self):
        self.log_message("엑셀로 저장하기 버튼이 클릭되었습니다.")

    def set_system_prompt(self):
        prompt = """당신은 번역 전문가 입니다. 일본 애니메이션풍 서브컬쳐 모바일게임에 등장하는 캐릭터의 대사를 내가 요청한 각국의 언어로 번역합니다. 지켜야할 것들은 이렇습니다.
1.게임에 사용되는 고유명사가 바뀌지 않게 조심하세요.
2.캐릭터 대사 번역시 내가 보내주는 화자의 정보 이름,나이,성별, 성격,말투,기타 대사 번역시 요구사항, 이전 대화내용들을 참고하여 현지인이 들어도 어색하지 않도록 번역해주세요.
3.인물간의 인칭 대명사가 바뀌지 않도록 해주세요."""
        
        self.system_prompt = prompt
        self.log_message("시스템 프롬프트가 설정되었습니다.")
        self.log_message("설정된 시스템 프롬프트:")
        self.log_message(prompt)

        try:
            response = self.model.generate_content(prompt)
            self.log_message("API의 응답:")
            self.log_message(response.text)
        except Exception as e:
            self.log_message(f"시스템 프롬프트 전송 중 오류 발생: {str(e)}")

    def get_user_prompt(self):
        prompt = simpledialog.askstring("입력", "Gemini에게 보낼 메시지를 입력하세요:")
        if prompt:
            self.send_user_prompt(prompt)

    def send_user_prompt(self, prompt):
        try:
            full_prompt = f"{self.system_prompt}\n\n사용자 입력: {prompt}"
            response = self.model.generate_content(full_prompt)
            self.log_message(f"사용자 입력: {prompt}")
            self.log_message(f"Gemini의 응답: {response.text}")
        except Exception as e:
            self.log_message(f"사용자 프롬프트 전송 중 오류 발생: {str(e)}")

    def create_log_window(self):
        self.log_window = tk.Toplevel(self.master)
        self.log_window.title("로그 창")
        self.log_window.geometry("600x200")

        # 로그 창을 화면 오른쪽 위에 배치
        screen_width = self.master.winfo_screenwidth()
        x = screen_width - 600  # 로그 창의 너비를 뺀 값
        self.log_window.geometry(f"600x200+{x}+0")

        # 로그 창 프레임
        log_frame = tk.Frame(self.log_window)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 로그 창
        self.log_text = tk.Text(log_frame, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def log_message(self, message):
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.config(state=tk.DISABLED)
            self.log_text.see(tk.END)
        else:
            print(message)  # 로그 창이 없을 경우 콘솔에 출력

if __name__ == "__main__":
    root = tk.Tk()
    root.title("AI 번역기 by studiobside")
    app = GameDialogueTranslator(master=root)

    root.mainloop()