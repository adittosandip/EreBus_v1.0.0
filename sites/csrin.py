from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from core.base import BaseSite


class CSRIN(BaseSite):

    NAME = "Voices38"

    URL = "https://cs.rin.ru/forum/search.php?author_id=885704&sr=posts"

    def __init__(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=True
        )

        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        )

        self.page = self.context.new_page()

    def latest(self):

        self.page.goto(
            self.URL,
            wait_until="networkidle",
            timeout=60000
        )

        html = self.page.content()

        soup = BeautifulSoup(html, "lxml")

        releases = []
        seen = set()

        for row in soup.select("tr.row2"):

            topic = row.select_one("p.topictitle a:last-of-type")

            if topic is None:
                continue

            title = topic.get_text(" ", strip=True)

            if title in seen:
                continue

            seen.add(title)

            info = row.find_next_sibling("tr")

            if info is None:
                continue

            post = info.select_one("b + a")

            if post is None:
                continue

            href = post.get("href", "")

            if href.startswith("./"):
                href = href[2:]

            url = f"https://cs.rin.ru/forum/{href}"

            parts = urlsplit(url)

            query = [
                (k, v)
                for k, v in parse_qsl(parts.query)
                if k != "sid"
            ]

            clean_url = urlunsplit((
                parts.scheme,
                parts.netloc,
                parts.path,
                urlencode(query),
                ""
            ))

            releases.append({
                "title": title.replace("[ Info ]", "").strip(),
                "link": clean_url
            })

        return releases

    def details(self, url):

        self.page.goto(
            url,
            wait_until="networkidle",
            timeout=60000
        )

        html = self.page.content()

        soup = BeautifulSoup(html, "lxml")

        title = ""

        topic = soup.select_one("h2.topic-title")

        if topic:
            title = topic.get_text(" ", strip=True)

        if not title:
            page = soup.select_one("title")

            if page:
                title = page.get_text(strip=True)

        title = (
            title.replace("CS RIN - Steam Underground • View topic -", "")
                 .replace("[ Info ]", "")
                 .strip()
        )

        return {
            "site": "CS RIN",
            "title": title,
            "link": url.split("&sid=")[0],
            "image": "",
            "size": ""
        }

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()
