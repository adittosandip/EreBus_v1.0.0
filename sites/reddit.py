import requests
import feedparser


class Reddit:

    NAME = "Reddit"

    RSS = "https://www.reddit.com/user/VOICES38/.rss"

    HEADERS = {
        "User-Agent": "linux:EreBus:1.0 (by /u/sxxdwip)"
    }

    def latest(self):

        response = requests.get(
            self.RSS,
            headers=self.HEADERS,
            timeout=30
        )

        response.raise_for_status()

        feed = feedparser.parse(response.content)

        releases = []

        for post in feed.entries:

            # Skip Reddit comments
            if post.title.startswith("/u/"):
                continue

            releases.append({
                "title": post.title.strip(),
                "link": post.link
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
