import time
import traceback

from loader import load_sites
from database import Database
from telegram import Telegram


class ReleaseMonitor:

    def __init__(self):

        self.database = Database()
        self.telegram = Telegram()
        self.sites = load_sites()

        print("=" * 60)
        print("Release Monitor Started")
        print("=" * 60)
        print()
        print(f"Loaded {len(self.sites)} site(s).")
        print()

    def check_site(self, site):

        print(f"Checking {site.NAME}...")

        try:
            releases = site.latest()

        except Exception as e:

            print()
            print("ERROR")
            print(site.NAME)
            print(e)
            print()

            traceback.print_exc()
            return

        if not releases:

            print("No release found.\n")
            return

        print(f"{len(releases)} release(s) found.\n")

        for release in releases:
            self.check_release(site, release)

    def check_release(self, site, release):

        title = release["title"]
        link = release["link"]

        if self.database.exists(link):

            print(f"Already exists: {title}")
            return

        print()
        print(f"NEW: {title}")

        try:
            details = site.details(link)

        except Exception as e:

            print(e)
            return

        details["source"] = site.NAME
        details["link"] = link

        if not details.get("title"):
            details["title"] = title

        self.send(details)

        self.database.save(
            details["site"],
            details["title"],
            details["link"]
        )

        print("Saved.\n")

    def send(self, details):

        message = (
            f"🔥 <b>NEW GAMES FROM {details['source']} !!!</b>\n\n"
            f"🎮 <b>{details['title']}</b>\n\n"
        )

        if details.get("size") and details["size"] != "-":
            message += f"📦 <b>Size:</b> {details['size']}\n\n"

        message += f"🌐 <b>Site:</b> {details['site']}\n\n"
        message += f"🔗 {details['link']}"

        try:

            self.telegram.send(message)

            print("Telegram Sent.\n")

        except Exception as e:

            print()
            print("Telegram Error")
            print(e)
            print()

    def run_once(self):

        print("=" * 60)
        print("Checking all sites...")
        print("=" * 60)
        print()

        for site in self.sites:
            self.check_site(site)

        print()
        print("Check Complete.\n")

    def loop(self):

        print("Monitor is running...\n")

        while True:

            try:
                self.run_once()

            except KeyboardInterrupt:

                print("\nStopping monitor...")
                break

            except Exception:

                print("\nUnexpected Error\n")
                traceback.print_exc()

            print("Waiting 120 seconds...\n")
            time.sleep(120)


def main():

    monitor = ReleaseMonitor()
    monitor.loop()


if __name__ == "__main__":

    main()
