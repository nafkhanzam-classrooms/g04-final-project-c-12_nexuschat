from cryptography.fernet import Fernet

KEY = b'Tc4urxrwHRbbEpR0N3cQX7Q5h1WS0traYllFPOS-0Rg='

cipher = Fernet(KEY)

def encrypt_message(text: str) -> str:
    encrypted = cipher.encrypt(text.encode())
    return encrypted.decode()

def decrypt_message(text: str) -> str:
    decrypted = cipher.decrypt(text.encode())
    return decrypted.decode()

