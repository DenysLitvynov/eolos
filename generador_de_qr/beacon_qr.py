# -------------------------------------------------------------
# Módulo: beacon_qr_uuid
# Descripción: Genera un código QR para un beacon BLE usando UUID
# Autor: Hugo Belda
# Fecha: 18/11/2025
# Requisitos: pip install qrcode pillow
# -------------------------------------------------------------

import qrcode
import json
from PIL import Image

# -------------------------------------------------------------
# UUID real de tu beacon (16 bytes tal como en Publicador)
# -------------------------------------------------------------
beacon_bytes = [
    ord('E'), ord('P'), ord('S'), ord('G'),
    ord('-'), ord('G'), ord('T'), ord('I'),
    ord('-'), ord('P'), ord('R'), ord('O'),
    ord('Y'), ord('-'), ord('3'), ord('A')
]

# Convertir a string hexadecimal tipo UUID (8-4-4-4-12)
uuid_hex = ''.join(f'{b:02X}' for b in beacon_bytes)
uuid_formatted = f'{uuid_hex[0:8]}-{uuid_hex[8:12]}-{uuid_hex[12:16]}-{uuid_hex[16:20]}-{uuid_hex[20:32]}'

# Datos que irá en el QR
data = {
    "uuid": uuid_formatted,   # UUID del beacon
    "id_bici": "VLC001"      # Identificador de la bici
}

# Convertir a JSON
payload = json.dumps(data)

# -------------------------------------------------------------
# Crear el QR
# -------------------------------------------------------------
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4
)
qr.add_data(payload)
qr.make(fit=True)

# Generar imagen y guardar
img = qr.make_image(fill_color="black", back_color="white")
img.save("qr-images/VLC001_uuid.png")

print("QR generado con UUID real del beacon:")
print(uuid_formatted)
