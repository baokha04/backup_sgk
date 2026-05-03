from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import binascii

IV_LENGTH = 8

def _get_padded_key(key: str) -> bytes:
    key_bytes = key.encode('utf-8')
    padded_key = bytearray(24)
    length = min(len(key_bytes), 24)
    padded_key[:length] = key_bytes[:length]
    return bytes(padded_key)

def encrypt(text: str, key: str) -> str:
    padded_key = _get_padded_key(key)
    iv = get_random_bytes(IV_LENGTH)
    cipher = DES3.new(padded_key, DES3.MODE_CBC, iv)
    padded_text = pad(text.encode('utf-8'), DES3.block_size)
    encrypted_bytes = cipher.encrypt(padded_text)
    
    iv_hex = binascii.hexlify(iv).decode('utf-8')
    encrypted_hex = binascii.hexlify(encrypted_bytes).decode('utf-8')
    
    return f"{iv_hex}:{encrypted_hex}"

def decrypt(encrypted_data: str, key: str) -> str:
    parts = encrypted_data.split(':')
    if len(parts) != 2:
        raise ValueError('Invalid encrypted data format')
        
    iv_hex, encrypted_hex = parts
    padded_key = _get_padded_key(key)
    
    iv = binascii.unhexlify(iv_hex)
    encrypted_bytes = binascii.unhexlify(encrypted_hex)
    
    cipher = DES3.new(padded_key, DES3.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(encrypted_bytes)
    
    decrypted_bytes = unpad(decrypted_padded, DES3.block_size)
    return decrypted_bytes.decode('utf-8')

if __name__ == "__main__":
    key = "mysecretkey"
    text = "hello world"
    encrypted = encrypt(text, key)
    print("Encrypted:", encrypted)
    decrypted = decrypt(encrypted, key)
    print("Decrypted:", decrypted)
    assert text == decrypted
