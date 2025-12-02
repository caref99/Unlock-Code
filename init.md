def __init__(self, storage_file="passwords.json"):
    self.storage_file = storage_file
    self.passwords = self.load_passwords()
