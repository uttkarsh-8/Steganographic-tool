import os
import base64
from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key(password: str, salt: bytes) -> bytes:

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_message(message: str, password: str) -> bytes:

    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(message.encode())

    return salt + token

def decrypt_message(encrypted_data: bytes, password: str) -> str:

    salt = encrypted_data[:16]
    token = encrypted_data[16:]
    key = derive_key(password, salt)
    f = Fernet(key)
    decrypted = f.decrypt(token)
    return decrypted.decode()

def to_bits(data: bytes) -> str:

    return ''.join(format(byte, '08b') for byte in data)

def from_bits(bits: str) -> bytes:

    byte_list = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return bytes(int(b, 2) for b in byte_list)


def hide_message_in_image(image_path: str, output_path: str, message: str, password: str):
 
    encrypted_data = encrypt_message(message, password)
    
    data_len = len(encrypted_data)
    len_bits = format(data_len, '032b')
    
    data_bits = len_bits + to_bits(encrypted_data)
    
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    pixels = list(image.getdata())
    
    total_channels = len(pixels) * 3  
    if len(data_bits) > total_channels:
        print("Error: The image is too small to hold this message.")
        return

    new_pixels = []
    bit_idx = 0
    for pixel in pixels:
        r, g, b = pixel
        if bit_idx < len(data_bits):
            r = (r & ~1) | int(data_bits[bit_idx])
            bit_idx += 1
        if bit_idx < len(data_bits):
            g = (g & ~1) | int(data_bits[bit_idx])
            bit_idx += 1
        if bit_idx < len(data_bits):
            b = (b & ~1) | int(data_bits[bit_idx])
            bit_idx += 1
        new_pixels.append((r, g, b))
    
    new_image = Image.new("RGB", image.size)
    new_image.putdata(new_pixels)
    new_image.save(output_path)
    print(f"Message hidden in {output_path}")

def extract_message_from_image(image_path: str, password: str):

    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    pixels = list(image.getdata())
    
    bits = ""
    for pixel in pixels:
        for channel in pixel:
            bits += str(channel & 1)
    
    data_len_bits = bits[:32]
    data_len = int(data_len_bits, 2)
    
    total_data_bits = data_len * 8
    encrypted_data_bits = bits[32:32+total_data_bits]
    encrypted_data = from_bits(encrypted_data_bits)
    
    try:
        message = decrypt_message(encrypted_data, password)
        print("Hidden message:", message)
    except Exception as e:
        print("Failed to decrypt the message. Incorrect password or corrupted data.")
        print("Error:", e)


def main():
    print("Steganography Tool")
    print("1. Hide a message in an image")
    print("2. Extract a message from an image")
    choice = input("Select an option (1 or 2): ").strip()
    
    if choice == '1':
        image_path = input("Enter path to the input PNG image: ").strip()
        output_path = input("Enter path for the output (stego) image: ").strip()
        message = input("Enter the message to hide: ")
        password = input("Enter the password: ")
        hide_message_in_image(image_path, output_path, message, password)
    elif choice == '2':
        image_path = input("Enter path to the image with a hidden message: ").strip()
        password = input("Enter the password: ")
        extract_message_from_image(image_path, password)
    else:
        print("Invalid option selected.")

if __name__ == "__main__":
    main()
