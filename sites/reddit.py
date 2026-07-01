import feedparser


class Reddit:

    NAME = "Reddit"

    RSS = "https://rss.app/feeds/E8gQn63RJEIwh7To.xml"

    def latest(self):

        feed = feedparser.parse(self.RSS)

        releases = []

        for post in feed.entries:

            releases.append({
                "title": post.title,
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
