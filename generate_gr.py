import qrcode
import os
from dotenv import load_dotenv

load_dotenv()

access_code = os.environ.get("ACCESS_CODE")
base_url = "http://127.0.0.1:5000" 
link = f"{base_url}/access?code={access_code}"

img = qrcode.make(link)
img.save("dostep_qr.png")

print(f"QR code generated for link: {link}")