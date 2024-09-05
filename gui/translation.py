import tkinter as tk
from tkinter import messagebox
import threading
import time

class TranslationHandler:
    def __init__(self, app):
        self.app = app

    def translate_selected_area(self):
        selected_items = self.app.widgets['tree'].selection()
        if not selected_items:
            messagebox.showwarning("경고", "번역할 항목을 선택해주세요.")
            return
        self.translate_items(selected_items)

    def translate_all(self):
        all_items = self.app.widgets['tree'].get_children()
        untranslated_items = [item for item in all_items if self.app.widgets['tree'].item(item, 'values')[4] == '번역']
        if not untranslated_items:
            messagebox.showinfo("알림", "모든 항목이 이미 번역되었습니다.")
            return
        self.translate_items(untranslated_items)

    def translate_items(self, items):
        self.app.translation_active = True
        is_single_item = len(items) == 1
        if not is_single_item:
            self.app.translation_window = self.app.file_handler.show_translation_window()
        self.app.file_handler.set_ui_state('disabled')

        def translation_thread():
            self.app.failed_translations = 0
            for item in items:
                if not self.app.translation_active:
                    break
                values = self.app.widgets['tree'].item(item, 'values')
                cut_scen_key, korean_text = values[0], values[2]
                try:
                    translated_text = self.app.translator.translate_item(cut_scen_key, korean_text, self.app.df, self.app.widgets['target_lang_var'].get(), self.app.character_info)
                    self.app.root.after(0, lambda i=item, t=translated_text: self.update_tree_item(i, t))
                    self.app.translated_items.add(cut_scen_key)
                    self.app.root.after(0, self.update_translated_count)
                    if not is_single_item:
                        time.sleep(1.5)
                except Exception as e:
                    self.app.logger.error(f"번역 중 오류 발생: {str(e)}")
                    self.app.root.after(0, lambda err=str(e): messagebox.showerror("오류", f"번역 중 오류가 발생했습니다: {err}\n\n자세한 내용은 로그를 확인해주세요."))

            if not is_single_item:
                self.app.root.after(0, self.app.file_handler.close_translation_window)
            self.app.root.after(0, lambda: self.app.file_handler.set_ui_state('normal'))
            self.app.root.after(0, self.update_text_edit)
            self.app.translation_active = False

        threading.Thread(target=translation_thread, daemon=True).start()

    def update_translated_count(self):
        count = len(self.app.translated_items)
        self.app.widgets['translated_count_label'].config(text=f"번역된 항목: {count}")

    def update_tree_item(self, item, translated_text):
        current_values = list(self.app.widgets['tree'].item(item, 'values'))
        if translated_text.startswith("번역 오류:"):
            if current_values[4] != '실패':
                self.app.failed_translations += 1
            current_values[3] = "번역 실패"
            current_values[4] = '실패'
            self.app.widgets['tree'].item(item, values=tuple(current_values), tags=('failed',))
        else:
            if current_values[4] == '실패':
                self.app.failed_translations = max(0, self.app.failed_translations - 1)
            current_values[3] = translated_text
            current_values[4] = '수정'
            self.app.widgets['tree'].item(item, values=tuple(current_values), tags=('normal',))
        self.app.widgets['tree'].selection_set(item)
        self.update_failed_count()

    def update_failed_count(self):
        self.app.widgets['failed_count_label'].config(text=f"번역 실패: {self.app.failed_translations}")

    def on_treeview_select(self, event):
        selected_items = self.app.widgets['tree'].selection()
        if selected_items:
            item = selected_items[0]
            values = self.app.widgets['tree'].item(item, 'values')
            if len(values) > 3:
                korean_text = values[2]
                translated_text = values[3]
                self.update_text_edit(korean_text, translated_text)
            else:
                self.update_text_edit()

    def update_text_edit(self, korean_text="", translated_text=""):
        self.app.widgets['korean_text_display'].config(state='normal')
        self.app.widgets['korean_text_display'].delete("1.0", tk.END)
        self.app.widgets['korean_text_display'].insert(tk.END, korean_text)
        self.app.widgets['korean_text_display'].config(state='disabled')

        self.app.widgets['text_edit'].delete("1.0", tk.END)
        self.app.widgets['text_edit'].insert(tk.END, translated_text)

    def on_language_select(self, event):
        if self.app.df is not None and self.app.current_sheet:
            self.app.file_handler.display_translation_items()

    def adjust_treeview_column_widths(self, event=None):
        window_width = self.app.root.winfo_width()
        total_width = sum([self.app.widgets['tree'].column(col)['width'] for col in self.app.widgets['tree']['columns']])
        
        if total_width == 0 or window_width == 0:
            default_width = 100
            for col in self.app.widgets['tree']['columns']:
                self.app.widgets['tree'].column(col, width=default_width)
            return

        if total_width < window_width:
            extra_space = window_width - total_width
            for col in self.app.widgets['tree']['columns']:
                current_width = self.app.widgets['tree'].column(col)['width']
                new_width = current_width + (current_width / total_width) * extra_space
                self.app.widgets['tree'].column(col, width=int(new_width))
        else:
            for col in self.app.widgets['tree']['columns']:
                current_width = self.app.widgets['tree'].column(col)['width']
                new_width = (current_width / total_width) * window_width
                self.app.widgets['tree'].column(col, width=int(new_width))

    def copy_selected_text(self, event=None):
        focused_widget = self.app.root.focus_get()
        
        if focused_widget == self.app.widgets['tree']:
            selected_items = self.app.widgets['tree'].selection()
            if selected_items:
                item = selected_items[0]
                values = self.app.widgets['tree'].item(item, 'values')
                text_to_copy = ' '.join(str(value) for value in values)
                self.app.root.clipboard_clear()
                self.app.root.clipboard_append(text_to_copy)
                self.app.logger.info("Treeview에서 선택된 텍스트가 클립보드에 복사되었습니다.")
        elif isinstance(focused_widget, tk.Text):
            selected_text = focused_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(selected_text)
            self.app.logger.info("Text 위젯에서 선택된 텍스트가 클립보드에 복사되었습니다.")
        else:
            self.app.logger.warning("복사할 텍스트를 선택하지 않았습니다.")

    def paste_to_text_edit(self, event=None):
        try:
            clipboard_content = self.app.root.clipboard_get()
            focused_widget = self.app.root.focus_get()
            
            if isinstance(focused_widget, tk.Text):
                focused_widget.insert(tk.INSERT, clipboard_content)
                self.app.logger.info("클립보드 내용을 Text 위젯에 붙여넣었습니다.")
            else:
                self.app.logger.warning("텍스트를 붙여넣을 수 있는 위젯이 선택되지 않았습니다.")
        except tk.TclError:
            self.app.logger.warning("클립보드가 비어있습니다.")
        except Exception as e:
            self.app.logger.error(f"텍스트 붙여넣기 중 오류 발생: {str(e)}")

    def on_key_press(self, event):
        if event.char == 'a' or event.char == 'A':
            self.apply_edit()

    def apply_edit(self):
        selected_item = self.app.widgets['tree'].selection()
        if selected_item:
            item = selected_item[0]
            edited_text = self.app.widgets['text_edit'].get("1.0", tk.END).strip()
            if edited_text:
                current_values = list(self.app.widgets['tree'].item(item, 'values'))
                current_values[3] = edited_text
                self.app.widgets['tree'].item(item, values=tuple(current_values))
                
                cut_scen_key = current_values[0]
                lang_column = self.app.file_handler.get_target_column()
                self.app.df.loc[self.app.df['m_CutScenKey'] == cut_scen_key, lang_column] = edited_text
                
                self.app.logger.info(f"텍스트 편집이 적용되었습니다: {cut_scen_key}")
                self.app.translated_items.add(cut_scen_key)
                self.update_translated_count()

    def on_tree_click(self, event):
        region = self.app.widgets['tree'].identify("region", event.x, event.y)
        if region == "cell":
            column = self.app.widgets['tree'].identify_column(event.x)
            item = self.app.widgets['tree'].focus()
            values = self.app.widgets['tree'].item(item, 'values')
            if values:
                if column == '#5':  # Action 열 클릭 시
                    self.translate_items([item])
                elif column == '#4':  # Translated 열 클릭 시
                    self.update_text_edit(values[2], values[3])  # 한국어와 번역된 텍스트 모두 업데이트

    def move_to_nearest_failed_translation(self, event):
        current_selection = self.app.widgets['tree'].selection()
        if not current_selection:
            return

        current_index = self.app.widgets['tree'].index(current_selection[0])
        all_items = self.app.widgets['tree'].get_children()
        direction = -1 if event.keysym == 'Up' else 1

        for i in range(1, len(all_items)):
            index = (current_index + i * direction) % len(all_items)
            item = all_items[index]
            if 'failed' in self.app.widgets['tree'].item(item, 'tags'):
                self.app.widgets['tree'].selection_set(item)
                self.app.widgets['tree'].see(item)
                self.on_treeview_select(None)
                break