def smart_password_recovery(self, pattern, char_set, max_results=10):
    unknown_positions = [i for i, char in enumerate(pattern) if char == '?']
    if not unknown_positions:
        return [pattern] if all(c in char_set for c in pattern) else []
    valid_passwords = []
    max_attempts = 10000
    for attempt in range(max_attempts):
        candidate = list(pattern)
        for pos in unknown_positions:
            candidate[pos] = random.choice(char_set)
        password = ''.join(candidate)
        if all(c in char_set for c in password) and password not in valid_passwords:
            valid_passwords.append(password)
            if len(valid_passwords) >= max_results:
                break
    return valid_passwords
