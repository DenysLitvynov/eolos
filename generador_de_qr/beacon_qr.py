"""
---------------------------------------------
 Módulo: beacon_qr
 Descripción: Genera un código QR con los datos
              de identificación de un beacon BLE.
 Autor: Hugo Belda
 Fecha: 07/11/2025
---------------------------------------------

 Requisitos de instalación (pip):
     pip install qrcode[pil]
     # o, alternativamente:
     pip install qrcode pillow
---------------------------------------------
"""

import qrcode
import json
from PIL import Image, ImageDraw

# Datos del beacon
data = {
    "name": "Emisora01",
    "uuid": "fda50693-a4e2-4fb1-afcf-c6eb07647825"
}

# Convertir a JSON
payload = json.dumps(data)

# Crear QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(payload)
qr.make(fit=True)

# Generar imagen
img = qr.make_image(fill_color="black", back_color="white")
img.save("beacon_qr.png")
