import os
import io
import base64
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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
    return salt + token  # Prepend salt

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


def hide_message_in_image_obj(image: Image.Image, message: str, password: str) -> Image.Image:

    encrypted_data = encrypt_message(message, password)
    data_len = len(encrypted_data)
    len_bits = format(data_len, '032b')
    data_bits = len_bits + to_bits(encrypted_data)

    if image.mode != 'RGB':
        image = image.convert('RGB')
    pixels = list(image.getdata())
    total_channels = len(pixels) * 3  

    if len(data_bits) > total_channels:
        raise ValueError("Image is too small to hold this message.")

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
    return new_image

def extract_message_from_image_obj(image: Image.Image, password: str) -> str:

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

    return decrypt_message(encrypted_data, password)


@app.post("/encode")
async def encode_image(
    file: UploadFile = File(...),
    message: str = Form(...),
    password: str = Form(...)
):

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        new_image = hide_message_in_image_obj(image, message, password)

        new_image.save("stego.png", format="PNG")

        return {"status": "success", "message": "Encoded image saved as stego.png"}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post("/decode")
async def decode_image(password: str = Form(...)):

    if not os.path.exists("stego.png"):
        return JSONResponse(status_code=400, content={"error": "No stego.png found. Please encode first."})
    
    try:
        image = Image.open("stego.png")
        hidden_message = extract_message_from_image_obj(image, password)
        return {"message": hidden_message}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
