import tkinter as tk
from tkinter import ttk

def create_widgets(app):
    widgets = {}
    widgets.update(create_top_frame(app))
    widgets.update(create_treeview(app))
    widgets.update(create_text_edit_frame(app))
    widgets.update(create_button_frame(app))
    widgets.update(create_labels(app))
    return widgets

def create_top_frame(app):
    top_frame = ttk.Frame(app.root)
    top_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

    select_file_button = ttk.Button(top_frame, text="엑셀 파일 선택", command=app.file_handler.select_file)
    select_file_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

    load_character_info_button = ttk.Button(top_frame, text="캐릭터 정보 파일 로드", command=app.file_handler.load_character_info)
    load_character_info_button.grid(row=0, column=1, padx=(0, 10), sticky="ew")

    ttk.Label(top_frame, text="시트:").grid(row=0, column=2, padx=(10, 5), sticky="w")
    sheet_var = tk.StringVar()
    sheet_combo = ttk.Combobox(top_frame, textvariable=sheet_var, state="disabled", width=15)
    sheet_combo.grid(row=0, column=3, padx=(0, 10), sticky="ew")

    ttk.Label(top_frame, text="번역 언어:").grid(row=0, column=4, padx=(10, 5), sticky="w")
    target_lang_var = tk.StringVar()
    target_lang_combo = ttk.Combobox(top_frame, textvariable=target_lang_var, 
                                     values=["일본어", "영어", "대만어", "태국어", "베트남어", "중국어", "독일어", "프랑스어"], state="disabled", width=15)
    target_lang_combo.grid(row=0, column=5, padx=(0, 10), sticky="ew")

    file_label = ttk.Label(top_frame, text="선택된 파일: 없음")
    file_label.grid(row=1, column=0, columnspan=6, padx=10, pady=10, sticky="w")

    return {
        'select_file_button': select_file_button,
        'load_character_info_button': load_character_info_button,
        'sheet_combo': sheet_combo,
        'sheet_var': sheet_var,
        'target_lang_combo': target_lang_combo,
        'target_lang_var': target_lang_var,
        'file_label': file_label
    }

def create_treeview(app):
    translation_frame = ttk.Frame(app.root)
    translation_frame.grid(row=2, column=0, columnspan=6, padx=10, pady=10, sticky="nsew")

    style = ttk.Style()
    style.configure("Treeview", font=('TkDefaultFont', 12))
    style.configure("Treeview.Heading", font=('TkDefaultFont', 12, 'bold'))
    style.configure("Treeview", rowheight=25)

    tree_frame = ttk.Frame(translation_frame)
    tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(tree_frame, columns=('CutScenKey', 'Speaker', 'Korean', 'Translated', 'Action'), show='headings', height=20)
    tree.heading('CutScenKey', text='CutScenKey')
    tree.heading('Speaker', text='화자')
    tree.heading('Korean', text='한국어 텍스트')
    tree.heading('Translated', text='번역된 텍스트')
    tree.heading('Action', text='동작')
    
    tree.column('CutScenKey', width=100, anchor='center')
    tree.column('Speaker', width=100)
    tree.column('Korean', width=400)
    tree.column('Translated', width=400)
    tree.column('Action', width=80, anchor='center')
    
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    return {'tree': tree, 'scrollbar': scrollbar}

def create_text_edit_frame(app):
    text_edit_frame = ttk.Frame(app.root)
    text_edit_frame.grid(row=3, column=0, columnspan=6, padx=10, pady=5, sticky="ew")

    korean_text_label = ttk.Label(text_edit_frame, text="한국어 원본:")
    korean_text_label.pack(side=tk.TOP, anchor=tk.W)
    korean_text_display = tk.Text(text_edit_frame, wrap=tk.WORD, height=3, state='disabled')
    korean_text_display.pack(side=tk.TOP, fill=tk.X, expand=True, pady=(0, 5))

    translated_text_label = ttk.Label(text_edit_frame, text="번역된 텍스트:")
    translated_text_label.pack(side=tk.TOP, anchor=tk.W)
    text_edit = tk.Text(text_edit_frame, wrap=tk.WORD, height=3)
    text_edit.pack(side=tk.LEFT, fill=tk.X, expand=True)

    apply_button = ttk.Button(text_edit_frame, text="적용하기", command=app.translation_handler.apply_edit)
    apply_button.pack(side=tk.LEFT, padx=5)

    return {
        'korean_text_display': korean_text_display,
        'text_edit': text_edit,
        'apply_button': apply_button
    }

def create_button_frame(app):
    button_frame = ttk.Frame(app.root)
    button_frame.grid(row=0, column=3, padx=10, pady=10, sticky="ne")

    translate_selected_button = ttk.Button(button_frame, text="선택한 영역 번역하기", command=app.translation_handler.translate_selected_area, state="disabled")
    translate_selected_button.pack(side=tk.TOP, pady=5)

    translate_all_button = ttk.Button(button_frame, text="전체 번역하기", command=app.translation_handler.translate_all, state="disabled")
    translate_all_button.pack(side=tk.TOP, pady=5)

    save_button_frame = ttk.Frame(app.root)
    save_button_frame.grid(row=4, column=5, pady=10, sticky="e")

    save_text_button = ttk.Button(save_button_frame, text="텍스트로 저장", command=app.file_handler.save_as_text_file, state="disabled")
    save_text_button.pack(side=tk.LEFT, padx=5)

    save_excel_button = ttk.Button(save_button_frame, text="엑셀로 저장", command=app.file_handler.save_as_excel_file, state="disabled")
    save_excel_button.pack(side=tk.LEFT, padx=5)

    return {
        'translate_selected_button': translate_selected_button,
        'translate_all_button': translate_all_button,
        'save_text_button': save_text_button,
        'save_excel_button': save_excel_button
    }

def create_labels(app):
    translated_count_label = tk.Label(app.root, text="번역된 항목: 0")
    translated_count_label.grid(row=5, column=0, columnspan=6, pady=5, sticky="w")

    failed_count_label = tk.Label(app.root, text="번역 실패: 0")
    failed_count_label.grid(row=5, column=1, columnspan=6, pady=5, sticky="w")

    return {
        'translated_count_label': translated_count_label,
        'failed_count_label': failed_count_label
    }