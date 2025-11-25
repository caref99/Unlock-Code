def generate_advanced_password(self, length, use_lowercase=True, use_uppercase=True, use_digits=True, use_symbols=True, exclude_similar=True):
    characters = ""
    char_sets = []
    if use_lowercase: 
        characters += "abcdefghijklmnopqrstuvwxyz"
        char_sets.append("abcdefghijklmnopqrstuvwxyz")
    if use_uppercase: 
        characters += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        char_sets.append("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    if use_digits: 
        characters += "0123456789"
        char_sets.append("0123456789")
    if use_symbols: 
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        char_sets.append("!@#$%^&*()_+-=[]{}|;:,.<>?")
    if not characters:
        return "❌ Нужно выбрать хотя бы один тип символов"
    if exclude_similar:
        similar_chars = "1lIoO0"
        characters = ''.join(c for c in characters if c not in similar_chars)
        char_sets = [''.join(c for c in char_set if c not in similar_chars) for char_set in char_sets if char_set]
    password_chars = []
    for char_set in char_sets:
        if char_set:
            password_chars.append(random.choice(char_set))
    while len(password_chars) < length:
        password_chars.append(random.choice(characters))
    random.shuffle(password_chars)
    password = ''.join(password_chars[:length])
    return password
