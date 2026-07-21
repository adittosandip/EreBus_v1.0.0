from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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

            releases.append({
                "title": title,
                "link": f"https://cs.rin.ru/forum/{href}"
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
        subject = ""
        posted = ""
        image = ""

        topic = soup.select_one("h2.topic-title")

        if topic:
            title = topic.get_text(" ", strip=True)

        if not title:
            page = soup.select_one("title")
            if page:
                title = page.get_text(strip=True)

        post_subject = soup.select_one("h3 a")

        if post_subject:
            subject = post_subject.get_text(" ", strip=True)

        for dt in soup.select("dt"):
            text = dt.get_text(" ", strip=True)
            if "Posted" in text:
                posted = text
                break

        size = "-"

        if subject:
            size = subject

        if posted:
            size += f" | {posted}"

        return {
            "site": self.NAME,
            "title": title,
            "link": url,
            "image": image,
            "size": size
        }

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()
