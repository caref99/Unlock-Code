def get_int_input(self, prompt, min_val=None, max_val=None):
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"❌ Число не может быть меньше {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"❌ Число не может быть больше {max_val}")
                continue
            return value
        except ValueError:
            print("❌ Пожалуйста, введите целое число")
