import tkinter as tk

def setup_bindings(app):
    app.widgets['tree'].bind('<<TreeviewSelect>>', app.translation_handler.on_treeview_select)
    app.root.bind('<Configure>', app.translation_handler.adjust_treeview_column_widths)
    app.root.bind('<Control-c>', app.translation_handler.copy_selected_text)
    app.root.bind('<Control-v>', app.translation_handler.paste_to_text_edit)
    app.root.bind('<a>', app.translation_handler.on_key_press)
    app.root.bind('<A>', app.translation_handler.on_key_press)
    app.root.bind('<Control-Up>', app.translation_handler.move_to_nearest_failed_translation)
    app.root.bind('<Control-Down>', app.translation_handler.move_to_nearest_failed_translation)
    app.widgets['tree'].bind('<ButtonRelease-1>', app.translation_handler.on_tree_click)
    app.widgets['sheet_combo'].bind("<<ComboboxSelected>>", app.file_handler.on_sheet_select)
    app.widgets['target_lang_combo'].bind("<<ComboboxSelected>>", app.translation_handler.on_language_select)