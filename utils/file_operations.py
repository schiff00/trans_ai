import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import pandas as pd

class FileHandler:
    def __init__(self, app):
        self.app = app

    def select_file(self):
        self.app.excel_file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if self.app.excel_file:
            self.show_loading_window("엑셀 파일 로딩 중...")
            self.set_ui_state('disabled')
            threading.Thread(target=self.load_excel_sheets, daemon=True).start()

    def load_excel_sheets(self):
        try:
            with self.app.lock:
                self.app.logger.info("엑셀 파일 로딩을 시작합니다.")
                sheet_names = self.app.excel_handler.get_sheet_names(self.app.excel_file)
                self.app.root.after(0, self.update_ui_after_loading, sheet_names)
                self.app.logger.info(f"엑셀 파일 로딩이 완료되었습니다: {self.app.excel_file}")
        except Exception as e:
            self.app.logger.error(f"엑셀 파일을 불러오는 중 오류가 발생했습니다: {str(e)}")
            self.app.root.after(0, lambda: messagebox.showerror("오류", f"엑셀 파일을 불러오는 중 오류가 발생했습니다: {str(e)}"))
        finally:
            self.app.root.after(0, self.close_loading_window)
            self.app.root.after(0, lambda: self.set_ui_state('normal'))

    def update_ui_after_loading(self, sheet_names):
        self.app.widgets['sheet_combo']['values'] = sheet_names
        self.app.widgets['sheet_combo']['state'] = 'readonly'
        self.app.widgets['target_lang_combo']['state'] = 'readonly'
        self.app.widgets['file_label'].config(text=f"선택된 파일: {os.path.basename(self.app.excel_file)}")
        self.app.widgets['translate_selected_button']['state'] = 'normal'
        self.app.widgets['translate_all_button']['state'] = 'normal'

    def on_sheet_select(self, event):
        self.show_loading_window("시트 로딩 중...")
        self.set_ui_state('disabled')
        threading.Thread(target=self.load_sheet, daemon=True).start()

    def load_sheet(self):
        sheet_name = self.app.widgets['sheet_var'].get()
        try:
            with self.app.lock:
                self.app.logger.info(f"시트 {sheet_name} 로딩을 시작합니다.")
                self.app.df = self.app.excel_handler.load_sheet(self.app.excel_file, sheet_name)
                self.app.current_sheet = sheet_name
                self.app.root.after(0, self.display_translation_items)
                self.app.logger.info(f"시트 {sheet_name} 로딩이 완료되었습니다.")
        except Exception as e:
            self.app.logger.error(f"시트를 불러오는 중 오류가 발생했습니다: {str(e)}")
            self.app.root.after(0, lambda: messagebox.showerror("오류", f"시트를 불러오는 중 오류가 발생했습니다: {str(e)}"))
        finally:
            self.app.root.after(0, self.close_loading_window)
            self.app.root.after(0, lambda: self.set_ui_state('normal'))

    def display_translation_items(self):
        self.app.widgets['tree'].delete(*self.app.widgets['tree'].get_children())
        required_columns = ["m_CutScenKey", "m_CharStr", "m_Talk_KOREA"]
        
        if not all(col in self.app.df.columns for col in required_columns):
            missing_columns = [col for col in required_columns if col not in self.app.df.columns]
            self.app.logger.error(f"필요한 열({', '.join(missing_columns)})을 찾을 수 없습니다.")
            messagebox.showerror("오류", f"필요한 열({', '.join(missing_columns)})을 찾을 수 없습니다.")
            return

        target_lang = self.app.widgets['target_lang_var'].get()
        lang_column = self.get_target_column()

        for index, row in self.app.df.iterrows():
            cut_scen_key = row["m_CutScenKey"]
            speaker = row["m_CharStr"]
            korean_text = row["m_Talk_KOREA"]
            translated_text = row.get(lang_column, "") if lang_column in self.app.df.columns else ""
            action = '번역' if pd.isna(translated_text) or translated_text.strip() == "" else '수정'
            
            if pd.notna(korean_text):
                self.app.widgets['tree'].insert('', 'end', values=(cut_scen_key, speaker, korean_text, translated_text, action))

        self.app.widgets['save_text_button']['state'] = 'normal'
        self.app.widgets['save_excel_button']['state'] = 'normal'

    def get_target_column(self):
        target_lang = self.app.widgets['target_lang_var'].get()
        return f"m_Talk_{self.app.translator.get_lang_code(target_lang)}"

    def save_as_text_file(self):
        self.app.excel_handler.save_as_text_file(self.app.excel_file, self.app.df, self.get_target_column())

    def save_as_excel_file(self):
        if self.app.excel_file is None or self.app.df is None:
            self.app.logger.warning("저장할 엑셀 파일이 없습니다.")
            messagebox.showwarning("경고", "저장할 엑셀 파일이 없습니다.")
            return

        def save_thread():
            try:
                self.app.root.after(0, lambda: self.show_progress_window("저장 중", "엑셀 파일을 저장하는 중입니다..."))
                new_file_name = self.app.excel_handler.save_as_excel_file(
                    self.app.excel_file, self.app.df, self.app.current_sheet, 
                    self.get_target_column(), self.app.translated_items
                )
                self.app.root.after(0, self.close_progress_window)
                self.app.root.after(0, lambda: messagebox.showinfo("성공", f"번역된 내용이 엑셀 파일에 저장되었습니다: {new_file_name}"))
                self.app.translated_items.clear()
                self.app.root.after(0, self.app.translation_handler.update_translated_count)
                self.app.root.after(0, lambda: self.reload_current_sheet(new_file_name))
            except Exception as e:
                self.app.logger.error(f"엑셀 파일을 저장하는데 오류가 발생했습니다: {str(e)}")
                self.app.root.after(0, self.close_progress_window)
                self.app.root.after(0, lambda: messagebox.showerror("오류", f"엑셀 파일을 저장하는데 오류가 발생했습니다: {str(e)}"))

        threading.Thread(target=save_thread, daemon=True).start()

    def reload_current_sheet(self, file_name):
        try:
            self.show_loading_window("시트 다시 로딩 중...")
            self.set_ui_state('disabled')
            self.app.excel_file = file_name
            self.app.df = self.app.excel_handler.load_sheet(self.app.excel_file, self.app.current_sheet)
            self.display_translation_items()
            self.app.logger.info(f"시트 '{self.app.current_sheet}'를 다시 로드했습니다.")
            self.close_loading_window()
            self.set_ui_state('normal')
        except Exception as e:
            self.app.logger.error(f"시트를 다시 로드하는 중 오류가 발생했습니다: {str(e)}")
            self.close_loading_window()
            self.set_ui_state('normal')
            messagebox.showerror("오류", f"시트를 다시 로드하는 중 오류가 발생했습니다: {str(e)}")

    def load_character_info(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            try:
                with self.app.lock:
                    self.app.character_info.load_from_file(file_path)
                    self.app.character_info_loaded = True
                    self.app.logger.info(f"캐릭터 정보 파일이 로드되었습니다: {file_path}")
                    messagebox.showinfo("성공", "캐릭터 정보 파일이 성공적으로 로드되었습니다.")
            except Exception as e:
                self.app.logger.error(f"캐릭터 정보 파일 로드 중 오류 발생: {str(e)}")
                messagebox.showerror("오류", f"캐릭터 정보 파일을 로드하는 중 오류가 발생했습니다: {str(e)}")

    def show_loading_window(self, message):
        self.app.loading_window = tk.Toplevel(self.app.root)
        self.app.loading_window.title("로딩 중")
        self.app.loading_window.geometry("300x100")
        self.app.loading_window.attributes('-topmost', 'true')

        tk.Label(self.app.loading_window, text=message).pack(pady=10)
        self.app.loading_bar = tk.ttk.Progressbar(self.app.loading_window, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
        self.app.loading_bar.pack(pady=10)
        self.app.loading_bar.start()

    def close_loading_window(self):
        if self.app.loading_window:
            self.app.loading_window.destroy()
            self.app.loading_window = None

    def set_ui_state(self, state):
        self.app.widgets['select_file_button']['state'] = state
        self.app.widgets['load_character_info_button']['state'] = state
        self.app.widgets['sheet_combo']['state'] = state
        self.app.widgets['target_lang_combo']['state'] = state
        self.app.widgets['translate_selected_button']['state'] = state
        self.app.widgets['translate_all_button']['state'] = state
        self.app.widgets['save_text_button']['state'] = state
        self.app.widgets['save_excel_button']['state'] = state
        self.app.widgets['apply_button']['state'] = state

    def show_translation_window(self):
        translation_window = tk.Toplevel(self.app.root)
        translation_window.title("자동 번역 진행 중")
        translation_window.geometry("300x150")
        translation_window.attributes('-topmost', 'true')

        tk.Label(translation_window, text="번역 진행중...", font=('TkDefaultFont', 12, 'bold')).pack(pady=20)

        stop_button = tk.ttk.Button(translation_window, text="자동 번역 멈추기", command=self.app.translation_handler.stop_translation)
        stop_button.pack(pady=10)

        translation_window.protocol("WM_DELETE_WINDOW", self.app.translation_handler.stop_translation)
        return translation_window

    def close_translation_window(self):
        if self.app.translation_window:
            self.app.translation_window.destroy()
            self.app.translation_window = None

    def show_progress_window(self, title, message):
        self.app.progress_window = tk.Toplevel(self.app.root)
        self.app.progress_window.title(title)
        self.app.progress_window.geometry("300x100")
        self.app.progress_window.attributes('-topmost', 'true')

        tk.Label(self.app.progress_window, text=message).pack(pady=10)
        self.app.progress_bar = tk.ttk.Progressbar(self.app.progress_window, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
        self.app.progress_bar.pack(pady=10)
        self.app.progress_bar.start()

    def close_progress_window(self):
        if hasattr(self.app, 'progress_window') and self.app.progress_window:
            self.app.progress_window.destroy()
            self.app.progress_window = None