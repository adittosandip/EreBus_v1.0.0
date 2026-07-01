import re
import requests
from bs4 import BeautifulSoup

from core.base import BaseSite


class Skidrow(BaseSite):

    NAME = "Skidrow"

    URL = "https://www.skidrowreloaded.com/"

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        })

    def latest(self):

        response = self.session.get(self.URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        releases = []

        for post in soup.select("div.post"):

            title = post.select_one("h2 a")

            if title is None:
                continue

            href = title.get("href")

            if not href:
                continue

            releases.append({
                "title": title.get_text(strip=True),
                "link": href
            })

        return releases

    def details(self, url):

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        text = soup.get_text("\n", strip=True)

        size = "-"

        patterns = [
            r"Size:\s*([0-9]+(?:\.[0-9]+)?\s*(?:MB|GB|TB))",
            r"Game Size:\s*([0-9]+(?:\.[0-9]+)?\s*(?:MB|GB|TB))",
            r"Download Size:\s*([0-9]+(?:\.[0-9]+)?\s*(?:MB|GB|TB))"
        ]

        for pattern in patterns:

            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                size = match.group(1).strip()
                break

        return {
            "site": self.NAME,
            "title": "",
            "link": url,
            "image": "",
            "size": size
        }
