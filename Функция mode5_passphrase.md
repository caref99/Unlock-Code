def mode5_passphrase(self):
    print("\n" + "="*40)
    print("🗣️  РЕЖИМ 5: Генерация пасфраз")
    print("="*40)
    words_ru = ["река", "солнце", "гора", "лес", "ветер", "океан", "звезда", "луна", "книга", "город", "дом", "свет", "тень", "путь", "мечта", "утро"]
    words_en = ["river", "sun", "mountain", "forest", "wind", "ocean", "star", "moon", "book", "city", "home", "light", "shadow", "path", "dream", "morning"]
    print("Выберите язык:")
    print("1 - Русский")
    print("2 - Английский")
    lang_choice = input("Ваш выбор (1-2): ")
    words = words_ru if lang_choice == "1" else words_en
    word_count = self.get_int_input("Количество слов (3-6): ", 3, 6)
    add_numbers = input("Добавить числа? (y/n): ").lower() == 'y'
    add_caps = input("Добавить заглавные буквы? (y/n): ").lower() == 'y'
    separators = ["-", "_", ".", ""]
    passphrase_words = []
    for i in range(word_count):
        word = random.choice(words)
        if add_caps and random.choice([True, False]):
            word = word.capitalize()
        passphrase_words.append(word)
    separator = random.choice(separators)
    passphrase = separator.join(passphrase_words)
    if add_numbers:
        number = str(random.randint(10, 999))
        passphrase += random.choice([number, f"-{number}", f"_{number}"])
    strength = self.password_strength(passphrase)
    print(f"\n🎉 Ваша пасфраза: {passphrase}")
    print(f"📊 Сложность: {strength}")
    print(f"📏 Длина: {len(passphrase)} символов")
