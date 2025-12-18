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
