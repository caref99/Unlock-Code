def password_strength(self, password):
    score = 0
    if len(password) >= 16: score += 2
    elif len(password) >= 12: score += 2
    elif len(password) >= 8: score += 1
    if any(c in "abcdefghijklmnopqrstuvwxyz" for c in password): score += 1
    if any(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in password): score += 1
    if any(c in "0123456789" for c in password): score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 1
    strength_emojis = {0: "❌ Очень слабый", 1: "🔴 Слабый", 2: "🟡 Средний", 3: "🟢 Хороший", 4: "💪 Отличный", 5: "🔐 Идеальный"}
    return strength_emojis.get(score, "❓ Неизвестно")
