import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import string
import json
import os
import datetime
import math
from collections import Counter

# Проверка QR-кода
QR_AVAILABLE = False
try:
    import qrcode
    from PIL import Image, ImageTk
    QR_AVAILABLE = True
except ImportError:
    pass

# ============================================================================================
# ЯДРО: Менеджер и движок
# ============================================================================================

class PasswordManager:
    def __init__(self, storage_file="passwords_secure.json"):
        self.storage_file = storage_file
        self.passwords = self.load_passwords()

    def load_passwords(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_password(self, service, login, password, notes=""):
        try:
            self.passwords[service] = {
                'login': login,
                'password': password,
                'notes': notes,
                'created': datetime.datetime.now().isoformat(),
                'strength': self._calculate_strength(password),
                'last_used': datetime.datetime.now().isoformat()
            }
            self._save_to_file()
            return True
        except Exception as e:
            return False

    def get_password(self, service):
        if service in self.passwords:
            self.passwords[service]['last_used'] = datetime.datetime.now().isoformat()
            self._save_to_file()
        return self.passwords.get(service)

    def list_services(self):
        return sorted(self.passwords.keys())

    def _calculate_strength(self, password):
        score = 0
        if len(password) >= 12: score += 2
        elif len(password) >= 8: score += 1
        if any(c in string.ascii_lowercase for c in password): score += 1
        if any(c in string.ascii_uppercase for c in password): score += 1
        if any(c in string.digits for c in password): score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 1
        return min(score, 5)

    def _save_to_file(self):
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.passwords, f, ensure_ascii=False, indent=2)
        except:
            pass


class PasswordEngine:
    def __init__(self):
        self.lower = string.ascii_lowercase
        self.upper = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.pm = PasswordManager()

    def generate(self, length=12, include_symbols=True):
        pool = self.lower + self.upper + self.digits
        if include_symbols:
            pool += self.symbols
        pwd = [
            random.choice(self.lower),
            random.choice(self.upper),
            random.choice(self.digits)
        ]
        if include_symbols:
            pwd.append(random.choice(self.symbols))
        while len(pwd) < length:
            pwd.append(random.choice(pool))
        random.shuffle(pwd)
        return ''.join(pwd[:length])

    def strength_score(self, pwd):
        score = 0
        if len(pwd) >= 12: score += 2
        elif len(pwd) >= 8: score += 1
        if any(c in self.lower for c in pwd): score += 1
        if any(c in self.upper for c in pwd): score += 1
        if any(c in self.digits for c in pwd): score += 1
        if any(c in self.symbols for c in pwd): score += 1
        return min(score, 5)

    def strength_text(self, score):
        return ["Очень слабый", "Слабый", "Средний", "Хороший", "Отличный", "Идеальный"][score]

    def strength_color(self, score):
        return ["#ff4444", "#ff9933", "#ffcc00", "#66bb66", "#22cc22", "#00aa00"][score]

    def entropy(self, pwd):
        if not pwd: return 0
        char_set = len(set(pwd))
        return round(len(pwd) * math.log2(char_set), 2)

    def analyze_password(self, pwd):
        if not pwd:
            return "❌ Пароль не может быть пустым"
        lines = []
        lines.append(f"🔐 Пароль: {'*' * len(pwd)}")
        lines.append(f"📏 Длина: {len(pwd)}")
        score = self.strength_score(pwd)
        lines.append(f"💪 Сложность: {self.strength_text(score)}")
        lines.append(f"🎲 Энтропия: {self.entropy(pwd)} бит")
        lines.append("\n📋 Содержит:")
        lines.append(f"  - Строчные: {'✅' if any(c in self.lower for c in pwd) else '❌'}")
        lines.append(f"  - Заглавные: {'✅' if any(c in self.upper for c in pwd) else '❌'}")
        lines.append(f"  - Цифры: {'✅' if any(c in self.digits for c in pwd) else '❌'}")
        lines.append(f"  - Символы: {'✅' if any(c in self.symbols for c in pwd) else '❌'}")
        return "\n".join(lines)

# ============================================================================================
# GUI
# ============================================================================================

class VaultPassApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔑 UnlockCode")
        # Полноэкранный режим без рамки
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        # Выход по Esc
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())

        self.engine = PasswordEngine()
        self.dark_mode = True
        self.setup_theme()
        self.show_main_menu()

    def exit_fullscreen(self):
        self.root.destroy()

    def setup_theme(self):
        self.colors = {
            'bg': '#1e1e2e' if self.dark_mode else '#f8f9fa',
            'fg': '#e0e0ff' if self.dark_mode else '#212529',
            'accent': '#8a7cfb',
            'card': '#2d2d3f' if self.dark_mode else '#ffffff',
            'input_bg': '#3a3a4f' if self.dark_mode else '#f0f0f4',
            'border': '#44475a' if self.dark_mode else '#d0d0d6',
            'error': '#f44336'
        }
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TFrame", background=self.colors['bg'])
        style.configure("TLabel", background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure("TButton", background=self.colors['accent'], foreground='white', font=('Segoe UI', 10, 'bold'))
        style.map("TButton", background=[('active', '#7a6cf0')])
        style.configure("TEntry", fieldbackground=self.colors['input_bg'], foreground=self.colors['fg'])
        style.configure("TCheckbutton", background=self.colors['bg'], foreground=self.colors['fg'])
        self.root.configure(bg=self.colors['bg'])

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.setup_theme()
        if hasattr(self, '_current_build_func'):
            self._current_build_func()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_window()
        self._current_build_func = self._build_main_menu
        self._build_main_menu()

    def _build_main_menu(self):
        top_frame = ttk.Frame(self.root, style="TFrame")
        top_frame.pack(fill=tk.X, padx=40, pady=20)
        title = ttk.Label(top_frame, text="🔑 UnlockCode", font=("Segoe UI", 28, "bold"),
                         foreground=self.colors['accent'])
        title.pack(side=tk.LEFT)
        theme_btn = tk.Button(top_frame, text="🌓", command=self.toggle_theme,
                             bg=self.colors['card'], fg=self.colors['fg'],
                             relief="flat", cursor="hand2")
        theme_btn.pack(side=tk.RIGHT)
        subtitle = ttk.Label(self.root, text="Надёжное управление паролями", font=("Segoe UI", 12))
        subtitle.pack(pady=(0, 30))
        modes_frame = ttk.Frame(self.root, style="TFrame")
        modes_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        modes = [
            ("🎲 Генератор", self.show_generator),
            ("🔍 Анализ", self.show_analyzer),
            ("💾 Менеджер", self.show_vault),
            ("🔄 Преобразовать", self.show_transformer),
            ("🧠 Тренировка", self.show_trainer),
            ("📊 Статистика", self.show_stats),
            ("📤 Экспорт", self.show_export),
            ("ℹ️ О программе", self.show_about)
        ]
        for i, (text, cmd) in enumerate(modes):
            row, col = divmod(i, 2)
            card = self.create_card(modes_frame, text, cmd)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        for i in range(4): modes_frame.rowconfigure(i, weight=1)
        for i in range(2): modes_frame.columnconfigure(i, weight=1)

    def create_card(self, parent, text, command):
        card = tk.Canvas(parent, bg=self.colors['card'], width=240, height=120,
                        highlightthickness=1, highlightbackground=self.colors['border'])
        card.bind("<Button-1>", lambda e: command())
        card.bind("<Enter>", lambda e: card.configure(bg="#3a3a4f" if self.dark_mode else "#f0f0f8"))
        card.bind("<Leave>", lambda e: card.configure(bg=self.colors['card']))
        card.create_text(120, 60, text=text, font=("Segoe UI", 12, "bold"), fill=self.colors['fg'])
        card.configure(cursor="hand2")
        return card

    # ------------------ ГЕНЕРАТОР ------------------
    def show_generator(self):
        self.clear_window()
        self._current_build_func = self._build_generator
        self._build_generator()

    def _build_generator(self):
        self.create_header("🎲 Генератор паролей", self.show_main_menu)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)
        length_frame = ttk.Frame(main, style="TFrame")
        length_frame.pack(fill=tk.X, pady=10)
        ttk.Label(length_frame, text="Длина пароля:", font=("Segoe UI", 11)).pack(side=tk.LEFT)
        self.gen_length = tk.IntVar(value=12)
        length_spin = tk.Spinbox(length_frame, from_=8, to=64, textvariable=self.gen_length,
                                bg=self.colors['input_bg'], fg=self.colors['fg'], width=5)
        length_spin.pack(side=tk.LEFT, padx=10)
        self.gen_symbols = tk.BooleanVar(value=True)
        sym_check = ttk.Checkbutton(main, text="Использовать спецсимволы", variable=self.gen_symbols)
        sym_check.pack(pady=10)
        gen_btn = tk.Button(main, text="Сгенерировать 🔁", command=self.do_generate,
                           bg=self.colors['accent'], fg='white', font=("Segoe UI", 11, "bold"),
                           relief="flat", cursor="hand2", padx=20, pady=8)
        gen_btn.pack(pady=20)
        self.gen_result = tk.StringVar()
        result_frame = ttk.Frame(main, style="TFrame")
        result_frame.pack(fill=tk.X, pady=10)
        result_entry = ttk.Entry(result_frame, textvariable=self.gen_result, font=("Consolas", 12))
        result_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.gen_show_btn = tk.Button(result_frame, text="👁️", command=self.toggle_gen_visibility,
                                     bg=self.colors['card'], fg=self.colors['fg'], relief="flat", width=4)
        self.gen_show_btn.pack(side=tk.RIGHT, padx=(5,0))
        self.gen_strength = tk.Canvas(main, height=12, bg=self.colors['input_bg'], highlightthickness=0)
        self.gen_strength.pack(fill=tk.X, pady=10)
        self.update_strength(self.gen_strength, "")
        action_frame = ttk.Frame(main, style="TFrame")
        action_frame.pack(pady=20)
        tk.Button(action_frame, text="📋 Копировать", command=self.copy_gen_result,
                 bg=self.colors['card'], fg=self.colors['fg'], relief="flat", padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="💾 Сохранить", command=self.save_gen_password,
                 bg=self.colors['accent'], fg='white', relief="flat", padx=15, pady=5).pack(side=tk.LEFT, padx=5)

    def do_generate(self):
        pwd = self.engine.generate(self.gen_length.get(), self.gen_symbols.get())
        self.gen_result.set(pwd)
        self.update_strength(self.gen_strength, pwd)

    def toggle_gen_visibility(self):
        current = self.gen_show_btn.cget("text")
        if current == "👁️":
            self.gen_show_btn.config(text="🙈")
        else:
            self.gen_show_btn.config(text="👁️")

    def copy_gen_result(self):
        pwd = self.gen_result.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Скопировано", "Пароль скопирован!")

    def save_gen_password(self):
        pwd = self.gen_result.get()
        if not pwd:
            messagebox.showwarning("Ошибка", "Сначала сгенерируйте пароль!")
            return
        self.save_password_dialog(pwd)

    # ------------------ АНАЛИЗ ------------------
    def show_analyzer(self):
        self.clear_window()
        self._current_build_func = self._build_analyzer
        self._build_analyzer()

    def _build_analyzer(self):
        self.create_header("🔍 Анализ пароля", self.show_main_menu)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)
        ttk.Label(main, text="Введите пароль для анализа:", font=("Segoe UI", 11)).pack(pady=5)
        self.analyze_input = tk.StringVar()
        analyze_entry = ttk.Entry(main, textvariable=self.analyze_input, font=("Consolas", 12), show='*')
        analyze_entry.pack(fill=tk.X, ipady=5, pady=10)
        self.analyze_show_btn = tk.Button(main, text="👁️", command=self.toggle_analyze_visibility,
                                         bg=self.colors['card'], fg=self.colors['fg'], relief="flat", width=6)
        self.analyze_show_btn.pack(pady=5)
        analyze_btn = tk.Button(main, text="Проанализировать", command=self.do_analyze,
                               bg=self.colors['accent'], fg='white', relief="flat", padx=20, pady=6)
        analyze_btn.pack(pady=15)
        self.analyze_output = scrolledtext.ScrolledText(main, height=10, font=("Consolas", 10),
                                                      bg=self.colors['input_bg'], fg=self.colors['fg'],
                                                      state='disabled')
        self.analyze_output.pack(fill=tk.BOTH, expand=True, pady=10)

    def toggle_analyze_visibility(self):
        entry = self.root.nametowidget(self.analyze_output.winfo_parent()).winfo_children()[1]
        current = self.analyze_show_btn.cget("text")
        if current == "👁️":
            entry.configure(show='')
            self.analyze_show_btn.config(text="🙈")
        else:
            entry.configure(show='*')
            self.analyze_show_btn.config(text="👁️")

    def do_analyze(self):
        pwd = self.analyze_input.get()
        result = self.engine.analyze_password(pwd)
        self.analyze_output.config(state='normal')
        self.analyze_output.delete(1.0, tk.END)
        self.analyze_output.insert(tk.END, result)
        self.analyze_output.config(state='disabled')

    # ------------------ МЕНЕДЖЕР ------------------
    def show_vault(self):
        self.clear_window()
        self._current_build_func = self._build_vault
        self._build_vault()

    def _build_vault(self):
        self.create_header("💾 Менеджер паролей", self.show_main_menu)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)
        btn_frame = ttk.Frame(main, style="TFrame")
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="➕ Добавить", command=self.add_password_form,
                 bg=self.colors['accent'], fg='white', relief="flat", padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 Обновить", command=self.load_vault_list,
                 bg=self.colors['card'], fg=self.colors['fg'], relief="flat", padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        list_frame = ttk.Frame(main, style="TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.vault_listbox = tk.Listbox(list_frame, font=("Segoe UI", 11),
                                       bg=self.colors['input_bg'], fg=self.colors['fg'],
                                       selectbackground=self.colors['accent'], relief="flat")
        self.vault_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.vault_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vault_listbox.config(yscrollcommand=scrollbar.set)
        self.vault_listbox.bind('<<ListboxSelect>>', self.show_vault_details)
        self.vault_detail = scrolledtext.ScrolledText(main, height=8, font=("Consolas", 10),
                                                    bg=self.colors['input_bg'], fg=self.colors['fg'],
                                                    state='disabled')
        self.vault_detail.pack(fill=tk.X, pady=10)
        self.load_vault_list()

    def load_vault_list(self):
        self.vault_listbox.delete(0, tk.END)
        for service in self.engine.pm.list_services():
            self.vault_listbox.insert(tk.END, service)

    def show_vault_details(self, event):
        selection = self.vault_listbox.curselection()
        if not selection: return
        service = self.vault_listbox.get(selection[0])
        data = self.engine.pm.get_password(service)
        if data:
            details = f"Сервис: {service}\n"
            details += f"Логин: {data['login']}\n"
            details += f"Пароль: {data['password']}\n"
            details += f"Заметки: {data.get('notes', '–')}\n"
            details += f"Создан: {data['created'][:10]}\n"
            details += f"Сложность: {data['strength']}"
            self.vault_detail.config(state='normal')
            self.vault_detail.delete(1.0, tk.END)
            self.vault_detail.insert(tk.END, details)
            self.vault_detail.config(state='disabled')

    def add_password_form(self):
        self.clear_window()
        self._current_build_func = self._build_add_form
        self._build_add_form()

    def _build_add_form(self):
        self.create_header("➕ Добавить пароль", self.show_vault)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        fields = [("Название сервиса", "service"), ("Логин / Email", "login"), ("Пароль", "password"), ("Заметки", "notes")]
        self.vault_vars = {}
        for label_text, key in fields:
            frame = ttk.Frame(main, style="TFrame")
            frame.pack(fill=tk.X, pady=8)
            ttk.Label(frame, text=label_text + ":", font=("Segoe UI", 11)).pack(anchor=tk.W)
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var, font=("Consolas", 11))
            if key == "password":
                entry.configure(show='*')
            entry.pack(fill=tk.X, ipady=4)
            self.vault_vars[key] = var
        btn_frame = ttk.Frame(main, style="TFrame")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="💾 Сохранить", command=self.save_new_password,
                 bg=self.colors['accent'], fg='white', relief="flat", padx=20, pady=6).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="◀️ Отмена", command=self.show_vault,
                 bg=self.colors['card'], fg=self.colors['fg'], relief="flat", padx=20, pady=6).pack(side=tk.LEFT)

    def save_new_password(self):
        service = self.vault_vars['service'].get().strip()
        login = self.vault_vars['login'].get().strip()
        password = self.vault_vars['password'].get()
        notes = self.vault_vars['notes'].get().strip()
        if not service or not login or not password:
            messagebox.showwarning("Ошибка", "Заполните все обязательные поля!")
            return
        if self.engine.pm.save_password(service, login, password, notes):
            messagebox.showinfo("Успех", "Пароль сохранён!")
            self.show_vault()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить пароль.")

    # ------------------ ПРЕОБРАЗОВАТЕЛЬ ------------------
    def show_transformer(self):
        self.clear_window()
        self._current_build_func = self._build_transformer
        self._build_transformer()

    def _build_transformer(self):
        self.create_header("🔄 Преобразование паролей", self.show_main_menu)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)
        ttk.Label(main, text="Введите пароль:", font=("Segoe UI", 11)).pack(pady=5)
        self.trans_input = tk.StringVar()
        trans_entry = ttk.Entry(main, textvariable=self.trans_input, font=("Consolas", 12))
        trans_entry.pack(fill=tk.X, ipady=5, pady=10)
        trans_frame = ttk.Frame(main, style="TFrame")
        trans_frame.pack(pady=15)
        transforms = [
            ("Leet", self.leet_transform),
            ("Регистр", self.altcase_transform),
            ("Обратить", self.reverse_transform),
            ("Суффикс", self.suffix_transform),
            ("ВЕРХНИЙ", self.upper_transform),
            ("нижний", self.lower_transform)
        ]
        for text, cmd in transforms:
            btn = tk.Button(trans_frame, text=text, command=cmd,
                           bg=self.colors['card'], fg=self.colors['fg'], relief="flat", padx=10, pady=5)
            btn.pack(side=tk.LEFT, padx=5)
        ttk.Label(main, text="Результат:", font=("Segoe UI", 11)).pack(pady=(20,5))
        self.trans_result = tk.StringVar()
        result_entry = ttk.Entry(main, textvariable=self.trans_result, font=("Consolas", 12))
        result_entry.pack(fill=tk.X, ipady=5, pady=10)
        self.trans_strength = tk.Canvas(main, height=12, bg=self.colors['input_bg'], highlightthickness=0)
        self.trans_strength.pack(fill=tk.X, pady=10)
        self.update_strength(self.trans_strength, "")

    def leet_transform(self):
        s = self.trans_input.get()
        res = s.replace('e','3').replace('a','@').replace('i','1').replace('o','0').replace('s','$')
        res = res.replace('E','3').replace('A','@').replace('I','1').replace('O','0').replace('S','$')
        self.trans_result.set(res)
        self.update_strength(self.trans_strength, res)

    def altcase_transform(self):
        s = self.trans_input.get()
        res = ''.join(c.upper() if i%2==0 else c.lower() for i, c in enumerate(s))
        self.trans_result.set(res)
        self.update_strength(self.trans_strength, res)

    def reverse_transform(self):
        s = self.trans_input.get()
        res = s[::-1]
        self.trans_result.set(res)
        self.update_strength(self.trans_strength, res)

    def suffix_transform(self):
        s = self.trans_input.get()
        res = s + str(random.randint(10,99)) + "!"
        self.trans_result.set(res)
        self.update_strength(self.trans_strength, res)

    def upper_transform(self):
        s = self.trans_input.get()
        res = s.upper()
        self.trans_result.set(res)
        self.update_strength(self.trans_strength, res)

    def lower_transform(self):
        s = self.trans_input.get()
        res = s.lower()
        self.trans_result.set(res)
        self.update_strength(self.trans_strength, res)

    # ------------------ ТРЕНИРОВКА ПАМЯТИ ------------------
    def show_trainer(self):
        self.clear_window()
        self._current_build_func = self._build_trainer
        self._build_trainer()

    def _build_trainer(self):
        self.create_header("🧠 Тренировка памяти", self.show_main_menu)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)
        levels = [("Легкий (6)", 6), ("Средний (8)", 8), ("Сложный (10)", 10), ("Эксперт (12)", 12)]
        for text, length in levels:
            btn = tk.Button(main, text=text, command=lambda l=length: self.start_memory_game(l),
                           bg=self.colors['card'], fg=self.colors['fg'], relief="flat", padx=20, pady=8)
            btn.pack(pady=8, fill=tk.X)

    def start_memory_game(self, length):
        pwd = self.engine.generate(length, include_symbols=True)
        self.clear_window()
        self._current_build_func = lambda: self._build_memory_game(pwd, length)
        self._build_memory_game(pwd, length)

    def _build_memory_game(self, pwd, length):
        self.create_header("🧠 Запомните пароль", self.show_trainer)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        pwd_label = ttk.Label(main, text=pwd, font=("Consolas", 18, "bold"),
                             foreground=self.colors['accent'])
        pwd_label.pack(pady=20)
        info = ttk.Label(main, text=f"Запомните его! Длина: {length} символов", font=("Segoe UI", 11))
        info.pack(pady=10)
        proceed_btn = tk.Button(main, text="Проверить память →", command=lambda: self.show_guess_screen(pwd),
                               bg=self.colors['accent'], fg='white', relief="flat", padx=20, pady=8)
        proceed_btn.pack(pady=30)

    def show_guess_screen(self, correct):
        self.clear_window()
        self._current_build_func = lambda: self._build_guess_screen(correct)
        self._build_guess_screen(correct)

    def _build_guess_screen(self, correct):
        self.create_header("🧠 Введите пароль", self.show_trainer)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        ttk.Label(main, text="Введите запомненный пароль:", font=("Segoe UI", 12)).pack(pady=10)
        self.guess_var = tk.StringVar()
        guess_entry = ttk.Entry(main, textvariable=self.guess_var, font=("Consolas", 14))
        guess_entry.pack(fill=tk.X, ipady=8, pady=20)
        check_btn = tk.Button(main, text="Проверить ✅", command=lambda: self.check_memory_guess(correct),
                             bg=self.colors['accent'], fg='white', relief="flat", padx=20, pady=8)
        check_btn.pack(pady=20)

    def check_memory_guess(self, correct):
        guess = self.guess_var.get()
        if guess == correct:
            messagebox.showinfo("🎉 Успех!", "Правильно! Отличная память!")
        else:
            messagebox.showerror("💔 Ошибка", f"Неверно.\nПравильный пароль: {correct}")
        self.show_trainer()

    # ------------------ СТАТИСТИКА ------------------
    def show_stats(self):
        self.clear_window()
        self._current_build_func = self._build_stats
        self._build_stats()

    def _build_stats(self):
        self.create_header("📊 Статистика", self.show_main_menu)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        stats_text = scrolledtext.ScrolledText(main, font=("Segoe UI", 11),
                                              bg=self.colors['input_bg'], fg=self.colors['fg'],
                                              state='disabled')
        stats_text.pack(fill=tk.BOTH, expand=True)
        services = self.engine.pm.list_services()
        total = len(services)
        output = "🔒 Статистика UnlockCode\n\n"
        output += f"Количество сохранённых паролей: {total}\n\n"
        if total > 0:
            strengths = {"Очень слабый":0, "Слабый":0, "Средний":0, "Хороший":0, "Отличный":0, "Идеальный":0}
            for svc in services:
                data = self.engine.pm.get_password(svc)
                s = data.get('strength', 'Средний')
                if s in strengths:
                    strengths[s] += 1
            output += "Распределение по сложности:\n"
            for level, count in strengths.items():
                if count > 0:
                    output += f"  • {level}: {count}\n"
            from collections import defaultdict
            months = defaultdict(int)
            for svc in services:
                data = self.engine.pm.get_password(svc)
                created = data.get('created', '')[:7]
                months[created] += 1
            if months:
                output += "\nПароли по месяцам:\n"
                for month, cnt in sorted(months.items()):
                    output += f"  • {month}: {cnt}\n"
        stats_text.config(state='normal')
        stats_text.delete(1.0, tk.END)
        stats_text.insert(tk.END, output)
        stats_text.config(state='disabled')

    # ------------------ ЭКСПОРТ ------------------
    def show_export(self):
        self.clear_window()
        self._current_build_func = self._build_export
        self._build_export()

    def _build_export(self):
        self.create_header("📤 Экспорт данных", self.show_main_menu)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        info = ttk.Label(main, text="Выберите, что экспортировать:", font=("Segoe UI", 12))
        info.pack(pady=10)
        btn_frame = ttk.Frame(main, style="TFrame")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="💾 Все пароли", command=self.export_all_passwords,
                 bg=self.colors['accent'], fg='white', relief="flat", padx=20, pady=8).pack(pady=8, fill=tk.X)
        tk.Button(btn_frame, text="📋 Только список сервисов", command=self.export_service_list,
                 bg=self.colors['card'], fg=self.colors['fg'], relief="flat", padx=20, pady=8).pack(pady=8, fill=tk.X)
        self.export_output = scrolledtext.ScrolledText(main, height=6, font=("Consolas", 10),
                                                      bg=self.colors['input_bg'], fg=self.colors['fg'],
                                                      state='disabled')
        self.export_output.pack(fill=tk.BOTH, expand=True, pady=20)

    def export_all_passwords(self):
        services = self.engine.pm.list_services()
        if not services:
            self.show_export_message("Нет данных для экспорта")
            return
        filename = f"unlockcode_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("UNLOCKCODE — ЭКСПОРТ ПАРОЛЕЙ\n")
                f.write(f"Дата: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                for svc in services:
                    data = self.engine.pm.get_password(svc)
                    f.write(f"Сервис: {svc}\n")
                    f.write(f"Логин: {data['login']}\n")
                    f.write(f"Пароль: {data['password']}\n")
                    f.write(f"Заметки: {data.get('notes', '–')}\n")
                    f.write(f"Создан: {data['created'][:10]}\n")
                    f.write("-"*30 + "\n\n")
            self.show_export_message(f"✅ Экспорт завершён!\nФайл: {filename}")
        except Exception as e:
            self.show_export_message(f"❌ Ошибка экспорта:\n{str(e)}")

    def export_service_list(self):
        services = self.engine.pm.list_services()
        if not services:
            self.show_export_message("Нет сервисов для экспорта")
            return
        filename = f"unlockcode_services_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Список сервисов из UnlockCode\n")
                f.write(f"Дата: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write("="*30 + "\n")
                for svc in services:
                    f.write(svc + "\n")
            self.show_export_message(f"✅ Список сохранён!\nФайл: {filename}")
        except Exception as e:
            self.show_export_message(f"❌ Ошибка:\n{str(e)}")

    def show_export_message(self, msg):
        self.export_output.config(state='normal')
        self.export_output.delete(1.0, tk.END)
        self.export_output.insert(tk.END, msg)
        self.export_output.config(state='disabled')

    # ------------------ О ПРОГРАММЕ (С QR!) ------------------
    def show_about(self):
        self.clear_window()
        self._current_build_func = self._build_about
        self._build_about()

    def _build_about(self):
        self.create_header("ℹ️ О программе", self.show_main_menu)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        info = (
            "🔑 UnlockCode — Современный парольный менеджер\n\n"
            "Версия: 1.0\n"
            "Год: 2025\n\n"
            "Следите за обновлениями и телеграм-ботом:\n"
            "Авторы: @carefr99 @Erale_pwr"
        )
        ttk.Label(main, text=info, font=("Segoe UI", 11), justify=tk.LEFT).pack(anchor=tk.W)
        link = "https://t.me/bestpswrdgen_bot"
        link_label = ttk.Label(main, text=link, font=("Consolas", 11, "underline"), foreground="#4da6ff", cursor="hand2")
        link_label.pack(pady=5)
        # QR-код
        qr_frame = ttk.Frame(main, style="TFrame")
        qr_frame.pack(pady=20)
        if QR_AVAILABLE:
            try:
                qr = qrcode.QRCode(box_size=4, border=2)
                qr.add_data(link)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img = img.resize((200, 200), Image.LANCZOS)
                self.qr_photo = ImageTk.PhotoImage(img)
                qr_label = tk.Label(qr_frame, image=self.qr_photo, bg=self.colors['card'])
                qr_label.pack()
            except Exception as e:
                ttk.Label(qr_frame, text=f"Ошибка генерации QR: {e}", foreground=self.colors['error']).pack()
        else:
            ttk.Label(qr_frame, text="Установите qrcode[pil] для QR-кода", foreground="#ff9966").pack()
            ttk.Label(qr_frame, text="(pip install qrcode[pil])", font=("Consolas", 9)).pack()
        about_text = scrolledtext.ScrolledText(main, height=6, font=("Segoe UI", 10),
                                              bg=self.colors['input_bg'], fg=self.colors['fg'], state='disabled')
        about_text.pack(fill=tk.BOTH, expand=True, pady=(20,0))
        about_text.config(state='normal')
        about_text.insert(tk.END, "Особенности:\n • Генерация надёжных паролей\n • Анализ сложности\n • Безопасное локальное хранение\n • Тёмная/светлая тема\n • Экспорт в файл")
        about_text.config(state='disabled')

    # ------------------ ВСПОМОГАТЕЛЬНЫЕ ------------------
    def create_header(self, title, back_command):
        header = ttk.Frame(self.root, style="TFrame")
        header.pack(fill=tk.X, padx=40, pady=20)
        back_btn = tk.Button(header, text="◀️ Назад", command=back_command,
                            bg=self.colors['card'], fg=self.colors['fg'], relief="flat", cursor="hand2")
        back_btn.pack(side=tk.LEFT)
        ttk.Label(header, text=title, font=("Segoe UI", 18, "bold")).pack(side=tk.LEFT, padx=20)

    def update_strength(self, canvas, pwd):
        canvas.delete("all")
        score = self.engine.strength_score(pwd) if pwd else 0
        color = self.engine.strength_color(score)
        width = canvas.winfo_width() or 400
        canvas.create_rectangle(0, 0, width, 12, fill="#333344" if self.dark_mode else "#e0e0e8", outline="")
        canvas.create_rectangle(0, 0, width * (score+1) / 6, 12, fill=color, outline="")
        text = self.engine.strength_text(score) if pwd else "Введите пароль"
        canvas.create_text(width//2, 6, text=text, fill="white", font=("Segoe UI", 8))

    def save_password_dialog(self, pwd):
        self.clear_window()
        self._current_build_func = lambda: self._build_save_dialog(pwd)
        self._build_save_dialog(pwd)

    def _build_save_dialog(self, pwd):
        self.create_header("💾 Сохранить пароль", self.show_generator)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        fields = [("Сервис", "service"), ("Логин", "login"), ("Заметки", "notes")]
        self.save_vars = {}
        for label, key in fields:
            frame = ttk.Frame(main, style="TFrame")
            frame.pack(fill=tk.X, pady=8)
            ttk.Label(frame, text=label + ":", font=("Segoe UI", 11)).pack(anchor=tk.W)
            var = tk.StringVar()
            ttk.Entry(frame, textvariable=var, font=("Consolas", 11)).pack(fill=tk.X, ipady=4)
            self.save_vars[key] = var
        frame = ttk.Frame(main, style="TFrame")
        frame.pack(fill=tk.X, pady=8)
        ttk.Label(frame, text="Пароль:", font=("Segoe UI", 11)).pack(anchor=tk.W)
        pwd_display = ttk.Entry(frame, font=("Consolas", 11))
        pwd_display.insert(0, pwd)
        pwd_display.configure(state='readonly')
        pwd_display.pack(fill=tk.X, ipady=4)
        btn_frame = ttk.Frame(main, style="TFrame")
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="💾 Сохранить", command=lambda: self.final_save(pwd),
                 bg=self.colors['accent'], fg='white', relief="flat", padx=20, pady=6).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="◀️ Отмена", command=self.show_generator,
                 bg=self.colors['card'], fg=self.colors['fg'], relief="flat", padx=20, pady=6).pack(side=tk.LEFT)

    def final_save(self, pwd):
        service = self.save_vars['service'].get().strip()
        login = self.save_vars['login'].get().strip()
        notes = self.save_vars['notes'].get().strip()
        if not service or not login:
            messagebox.showwarning("Ошибка", "Заполните сервис и логин!")
            return
        if self.engine.pm.save_password(service, login, pwd, notes):
            messagebox.showinfo("Успех", "Пароль сохранён в менеджере!")
            self.show_generator()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить!")

# ============================================================================================
# ЗАПУСК
# ============================================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = VaultPassApp(root)
    root.mainloop()
