from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from pathlib import Path
from datetime import datetime
import logging

from core.base import BaseSite
from telegram import Telegram

# Configure logging
logger = logging.getLogger(__name__)


class CSRIN(BaseSite):

    NAME = "Voices38"

    URL = "https://cs.rin.ru/forum/search.php?author_id=885704&sr=posts"
    
    # Cookies/session configuration
    COOKIES_DIR = Path("cookies")
    STATE_FILE = COOKIES_DIR / "state.json"

    def __init__(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=True
        )

        # Create cookies directory if it doesn't exist
        self.COOKIES_DIR.mkdir(parents=True, exist_ok=True)

        # Load cookies from state.json if it exists
        storage_state = None
        if self.STATE_FILE.exists():
            try:
                storage_state = str(self.STATE_FILE)
                logger.info(f"Loading cookies from {self.STATE_FILE}")
            except Exception as e:
                logger.warning(f"Failed to load cookies: {e}")
                storage_state = None
        else:
            logger.warning(f"Cookie file not found: {self.STATE_FILE}")

        self.context = self.browser.new_context(
            storage_state=storage_state,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        )

        self.page = self.context.new_page()
        
        # Initialize Telegram client for session expiration notifications
        self.telegram = Telegram()

    def _print_debug_header(self) -> None:
        """
        Print comprehensive debug information about current page state.
        Used for troubleshooting session issues.
        """
        print("=" * 70)
        print("URL:", self.page.url)
        print("TITLE:", self.page.title())

        cookies = self.context.cookies()

        print("COOKIE COUNT:", len(cookies))
        print("COOKIE NAMES:")
        for c in cookies:
            print(" -", c["name"], c["domain"])
        print("=" * 70)

    def _get_debug_info(self) -> dict:
        """
        Collect comprehensive debug information about the current page state.
        
        Returns:
            Dictionary with debugging data
        """
        try:
            url = self.page.url
            title = self.page.title()
            html = self.page.content()
            
            # Check for logout link (indicates logged in)
            logout_link_exists = self.page.locator("a[href*='mode=logout']").count() > 0
            
            # Check for login link (indicates NOT logged in)
            login_link_exists = self.page.locator("a[href*='mode=login']").count() > 0
            
            # Check for Cloudflare challenge
            cf_challenge = self.page.locator("cf-challenge").count() > 0 or \
                          "Checking your browser" in html or \
                          "Cloudflare" in title or \
                          "__cf_bm" in self.context.cookies().__str__()
            
            # Get loaded cookies
            cookies = self.context.cookies()
            cookie_names = [c.get('name', '') for c in cookies]
            
            # Get first 500 chars of HTML for inspection
            html_preview = html[:500]
            
            debug_info = {
                "timestamp": datetime.now().isoformat(),
                "current_url": url,
                "page_title": title,
                "html_preview": html_preview,
                "html_length": len(html),
                "loaded_cookies": cookie_names,
                "cookie_count": len(cookies),
                "logout_link_exists": logout_link_exists,
                "login_link_exists": login_link_exists,
                "cloudflare_challenge_detected": cf_challenge,
            }
            
            return debug_info
        
        except Exception as e:
            logger.error(f"Error collecting debug info: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _notify_session_expired(self) -> None:
        """
        Send Telegram notification about session expiration.
        
        Uses the existing Telegram class from telegram.py.
        If notification fails, logs the error but does not raise.
        """
        message = (
            "⚠️ <b>CS.RIN SESSION EXPIRED</b>\n\n"
            f"Source: <b>{self.NAME}</b>\n\n"
            "Your CS.RIN login session has expired.\n\n"
            "Please run <b>login.py</b> on your MacBook "
            "and upload the new <b>state.json</b>."
        )
        
        try:
            self.telegram.send(message)
        except Exception as e:
            logger.error(f"Failed to send session expiration notification: {e}")

    def _check_session_valid(self) -> None:
        """
        Validate that the user is logged into CS.RIN.
        
        On a valid CS.RIN page, a logged-in user will have:
        - A logout link (a[href*='mode=logout'])
        - No login page redirect
        - Valid cookies
        
        If session is invalid, sends a Telegram notification before raising RuntimeError.
        
        Raises:
            RuntimeError: If session is invalid with detailed reason
        """
        try:
            # Print debug header to console for immediate inspection
            self._print_debug_header()
            
            # Get debug info
            debug_info = self._get_debug_info()
            
            url = debug_info.get('current_url', '')
            title = debug_info.get('page_title', '')
            logout_link_exists = debug_info.get('logout_link_exists', False)
            login_link_exists = debug_info.get('login_link_exists', False)
            cf_challenge = debug_info.get('cloudflare_challenge_detected', False)
            cookie_count = debug_info.get('cookie_count', 0)
            
            # Check 1: Cloudflare challenge
            if cf_challenge:
                self._notify_session_expired()
                raise RuntimeError(
                    "CS.RIN session expired: Cloudflare challenge detected. "
                    "The forum is blocking automated access. "
                    "Please regenerate cookies by running login.py with a real browser."
                )
            
            # Check 2: Redirect to login page URL
            if "ucp.php?mode=login" in url.lower():
                self._notify_session_expired()
                raise RuntimeError(
                    "CS.RIN session expired: Redirected to login page (URL contains ucp.php?mode=login). "
                    "Cookies are invalid or expired. "
                    "Please regenerate cookies by running login.py."
                )
            
            # Check 3: No cookies loaded at all
            if cookie_count == 0:
                self._notify_session_expired()
                raise RuntimeError(
                    f"CS.RIN session expired: No cookies loaded from {self.STATE_FILE}. "
                    "File does not exist or is invalid. "
                    "Please run login.py to generate a new session."
                )
            
            # Check 4: MAIN CHECK - Logout link exists = logged in
            # If logout link exists, user IS logged in - session is VALID
            if logout_link_exists:
                logger.debug("Session validation passed: Logout link detected (user is logged in)")
                return
            
            # Check 5: If NO logout link but login link exists = NOT logged in
            if login_link_exists and not logout_link_exists:
                self._notify_session_expired()
                raise RuntimeError(
                    "CS.RIN session expired: Not authenticated. "
                    "Cookies were loaded but are invalid or expired (page shows login link, no logout). "
                    "Please regenerate cookies by running login.py."
                )
            
            # Check 6: Fallback - neither logout nor login link visible
            # This could mean page structure changed or user is in some intermediate state
            logger.warning(
                "Warning: Neither logout nor login link detected. "
                "Page structure may have changed. Proceeding anyway."
            )
        
        except RuntimeError:
            # Re-raise RuntimeError (our session errors)
            raise
        except Exception as e:
            # Catch unexpected errors and send Telegram before raising
            self._notify_session_expired()
            raise RuntimeError(f"CS.RIN session check failed: {e}")

    def latest(self):

        self.page.goto(
            self.URL,
            wait_until="networkidle",
            timeout=60000
        )

        # Validate session AFTER page load
        self._check_session_valid()

        html = self.page.content()

        soup = BeautifulSoup(html, "lxml")

        releases = []
        seen = set()

        # Find all topic header rows (tr.row2 contains topic title in td>p.topictitle)
        for row in soup.select("tr.row2"):

            # Debug: Print row structure for inspection
            print(f"Processing row: {row.get('class')}")
            
            # Extract topic title from <p class="topictitle"><a>...</a></p>
            topic = row.select_one("p.topictitle a")
            
            # Debug: If topic not found, try alternative selectors
            if topic is None:
                print("  -> 'p.topictitle a' not found, trying alternatives...")
                # Try other common topic selectors
                topic = row.select_one("a.topictitle")
                if topic is None:
                    topic = row.select_one("a[href*='viewtopic.php']")
                if topic is None:
                    print("  -> No topic link found in this row, skipping")
                    continue
                else:
                    print(f"  -> Found topic with alternative selector")

            title = topic.get_text(" ", strip=True)
            print(f"  -> Title: {title[:60]}")

            if title in seen:
                print(f"  -> Duplicate, skipping")
                continue

            seen.add(title)

            # Find the next sibling row (tr.row1) which contains post details
            info = row.find_next_sibling("tr")

            if info is None:
                print(f"  -> No info row found, skipping")
                continue

            # In the info row, look for the "Post subject" link which links to the specific post
            post = info.select_one("a[href*='viewtopic.php']")

            if post is None:
                print(f"  -> No post link found in info row, skipping")
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
            print(f"  -> Added to releases")

        print(f"\nTotal releases found: {len(releases)}\n")
        return releases

    def details(self, url):

        self.page.goto(
            url,
            wait_until="networkidle",
            timeout=60000
        )

        # Validate session AFTER page load
        self._check_session_valid()

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
