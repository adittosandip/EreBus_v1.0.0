import requests
from bs4 import BeautifulSoup

from core.base import BaseSite


class Scene(BaseSite):

    NAME = "Scene"

    URL = "https://scene.cat/"

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

        for row in soup.select("div.release-row"):

            title = row.select_one("span.release-name")

            link = row.select_one("a.deep-link")

            if title is None or link is None:
                continue

            href = link.get("href")

            if not href:
                continue

            releases.append({
                "title": title.get_text(strip=True),
                "link": "https://scene.cat" + href
            })

        return releases

    def details(self, url):

        return {
            "site": self.NAME,
            "title": "",
            "link": url,
            "image": "",
            "size": "-"
        }
