import requests
import yaml
from pathlib import Path


CONFIG = Path("config.yaml")


class Telegram:

    def __init__(self):

        with open(CONFIG, "r") as f:
            config = yaml.safe_load(f)

        self.token = config["telegram"]["token"]
        self.chat_id = config["telegram"]["chat_id"]

        self.api = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send(self, text):

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        r = requests.post(self.api, json=payload, timeout=30)

        if r.status_code == 200:
            print("Telegram Sent ✓")
            return True

        print(r.text)
        return False
