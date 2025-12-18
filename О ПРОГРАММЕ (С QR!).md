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
