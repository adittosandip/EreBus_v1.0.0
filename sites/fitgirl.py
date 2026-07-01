import re
import requests
from bs4 import BeautifulSoup

from core.base import BaseSite


class FitGirl(BaseSite):

    NAME = "FitGirl"

    URL = "https://fitgirl-repacks.site/"

    SKIP = [
        "Upcoming Repacks",
        "Updates Digest",
        "Repack Updated",
        "Upcoming",
        "Digest"
    ]

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0 Safari/537.36"
        })

    def latest(self):

        response = self.session.get(self.URL, timeout=30)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        releases = []

        for article in soup.select("article"):

            title = article.select_one("h1.entry-title")

            if title is None:
                continue

            game_title = title.get_text(strip=True)

            if any(x.lower() in game_title.lower() for x in self.SKIP):
                continue

            releases.append({

                "title": game_title,

                "link": title.a["href"]

            })

        return releases

    def details(self, url):

        response = self.session.get(url, timeout=30)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        title = ""

        image = ""

        size = "Unknown"

        # ---------------- TITLE ----------------

        h1 = soup.select_one("h1.entry-title")

        if h1:

            title = h1.get_text(strip=True)

        # ---------------- IMAGE ----------------

        meta = soup.select_one("meta[property='og:image']")

        if meta:

            image = meta.get("content", "")

        # ---------------- SIZE ----------------

        content = soup.select_one("div.entry-content")

        if content:

            text = content.get_text("\n", strip=True)

            patterns = [

                r"Repack Size:\s*(.+)",

                r"Original Size:\s*(.+)",

                r"Final Size:\s*(.+)",

                r"Size:\s*(.+)"

            ]

            for pattern in patterns:

                match = re.search(pattern, text, re.IGNORECASE)

                if match:

                    size = match.group(1).strip()

                    break

        return {

            "site": self.NAME,

            "title": title,

            "link": url,

            "image": image,

            "size": size

        }
