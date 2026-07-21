from http.cookiejar import MozillaCookieJar

import requests
from bs4 import BeautifulSoup

from core.base import BaseSite


class CSRIN(BaseSite):

    NAME = "Voices38"

    URL = "https://cs.rin.ru/forum/search.php?author_id=885704&sr=posts"

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://cs.rin.ru/forum/",
            "Origin": "https://cs.rin.ru",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })

        jar = MozillaCookieJar("cookies/csrin.txt")

        try:
            jar.load(ignore_discard=True, ignore_expires=True)
            self.session.cookies.update(jar)
        except Exception as e:
            print(f"Cookie load failed: {e}")

    def latest(self):

        response = self.session.get(
            self.URL,
            timeout=30,
            allow_redirects=True
        )

        print("=" * 60)
        print("CSRIN DEBUG")
        print("=" * 60)
        print("Status:", response.status_code)
        print("URL:", response.url)
        print("Cookies Sent:", self.session.cookies.get_dict())
        print("Response:")
        print(response.text[:500])
        print("=" * 60)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

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

        response = self.session.get(url, timeout=30)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

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
