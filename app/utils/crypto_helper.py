from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import binascii

ALGORITHM = 'des-ede3-cbc'
IV_LENGTH = 8 # 3DES IV size is 8 bytes

def _get_padded_key(key: str) -> bytes:
    """Key must be 24 bytes for 3DES"""
    key_bytes = key.encode('utf-8')
    padded_key = bytearray(24)
    length = min(len(key_bytes), 24)
    padded_key[:length] = key_bytes[:length]
    return bytes(padded_key)

def encrypt(text: str, key: str) -> str:
    """
    Encrypts text using Triple DES (des-ede3-cbc)
    :param text: The plain text to encrypt
    :param key: The encryption key (will be padded/truncated to 24 bytes)
    :return: Encrypted text in "iv:ciphertext" hex format
    """
    padded_key = _get_padded_key(key)
    iv = get_random_bytes(IV_LENGTH)
    cipher = DES3.new(padded_key, DES3.MODE_CBC, iv)
    padded_text = pad(text.encode('utf-8'), DES3.block_size)
    encrypted_bytes = cipher.encrypt(padded_text)
    
    iv_hex = binascii.hexlify(iv).decode('utf-8')
    encrypted_hex = binascii.hexlify(encrypted_bytes).decode('utf-8')
    
    return f"{iv_hex}:{encrypted_hex}"

def decrypt(encrypted_data: str, key: str) -> str:
    """
    Decrypts text using Triple DES (des-ede3-cbc)
    :param encrypted_data: The encrypted data in "iv:ciphertext" hex format
    :param key: The encryption key (will be padded/truncated to 24 bytes)
    :return: Decrypted plain text
    """
    parts = encrypted_data.split(':')
    if len(parts) != 2:
        raise ValueError('Invalid encrypted data format')
        
    iv_hex, encrypted_hex = parts
    
    if not iv_hex or not encrypted_hex:
        raise ValueError('Invalid encrypted data format')
        
    padded_key = _get_padded_key(key)
    
    iv = binascii.unhexlify(iv_hex)
    encrypted_bytes = binascii.unhexlify(encrypted_hex)
    
    cipher = DES3.new(padded_key, DES3.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(encrypted_bytes)
    
    decrypted_bytes = unpad(decrypted_padded, DES3.block_size)
    return decrypted_bytes.decode('utf-8')
