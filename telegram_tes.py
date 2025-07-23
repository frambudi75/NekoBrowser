import requests

token = "7995402951:AAHDufHskS7Yi4RTUb-39_xRaFeWMciSFAE"
chat_id = "-754026431"
message = "Notifikasi berhasil terkirim dari Python!"

url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {"chat_id": chat_id, "text": message}

response = requests.post(url, data=payload)
print(response.status_code, response.text)
