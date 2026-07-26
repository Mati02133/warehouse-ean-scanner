import qrcode
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

access_code = os.environ.get("ACCESS_CODE")
base_url = "https://mati02133.eu.pythonanywhere.com"

link = f"{base_url}/access?code={access_code}"

img = qrcode.make(link)
img.save(os.path.join(BASE_DIR, "dostep_qr.png"))

print(f"QR code generated for link: {link}")