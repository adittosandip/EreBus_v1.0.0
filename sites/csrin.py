from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from pathlib import Path
from datetime import datetime
import json
import logging

from core.base import BaseSite

# Configure logging
logger = logging.getLogger(__name__)


class CSRIN(BaseSite):

    NAME = "Voices38"

    URL = "https://cs.rin.ru/forum/search.php?author_id=885704&sr=posts"
    
    # Cookies/session configuration
    COOKIES_DIR = Path("cookies")
    STATE_FILE = COOKIES_DIR / "state.json"
    
    # Debug output directory
    DEBUG_DIR = Path("debug_csrin")

    def __init__(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=True
        )

        # Create cookies directory if it doesn't exist
        self.COOKIES_DIR.mkdir(parents=True, exist_ok=True)
        self.DEBUG_DIR.mkdir(parents=True, exist_ok=True)

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
            
            # Check for login form (indicates NOT logged in)
            login_form_exists = self.page.locator("form[method='post'][action*='login']").count() > 0
            
            # Check for logout link (indicates logged in)
            logout_link_exists = self.page.locator("a[href*='logout'], a:has-text('Logout')").count() > 0
            
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
                "login_form_exists": login_form_exists,
                "logout_link_exists": logout_link_exists,
                "cloudflare_challenge_detected": cf_challenge,
            }
            
            return debug_info
        
        except Exception as e:
            logger.error(f"Error collecting debug info: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _save_debug_artifacts(self, reason: str) -> None:
        """
        Save debug artifacts (screenshot, HTML, metadata) when session validation fails.
        
        Args:
            reason: Description of why debug artifacts are being saved
        """
        try:
            debug_info = self._get_debug_info()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save screenshot
            screenshot_path = self.DEBUG_DIR / f"screenshot_{timestamp}.png"
            try:
                self.page.screenshot(path=str(screenshot_path))
                logger.info(f"Debug screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.warning(f"Failed to save screenshot: {e}")
            
            # Save HTML
            html_path = self.DEBUG_DIR / f"page_{timestamp}.html"
            try:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(self.page.content())
                logger.info(f"Debug HTML saved: {html_path}")
            except Exception as e:
                logger.warning(f"Failed to save HTML: {e}")
            
            # Save metadata
            metadata_path = self.DEBUG_DIR / f"metadata_{timestamp}.json"
            debug_info['reason'] = reason
            try:
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(debug_info, f, indent=2, default=str)
                logger.info(f"Debug metadata saved: {metadata_path}")
            except Exception as e:
                logger.warning(f"Failed to save metadata: {e}")
            
            # Log debug info to console
            logger.info(f"=== SESSION VALIDATION DEBUG INFO ===")
            logger.info(f"Reason: {reason}")
            logger.info(f"URL: {debug_info.get('current_url', 'N/A')}")
            logger.info(f"Title: {debug_info.get('page_title', 'N/A')}")
            logger.info(f"Cookies loaded: {debug_info.get('cookie_count', 0)}")
            logger.info(f"Cookie names: {debug_info.get('loaded_cookies', [])}")
            logger.info(f"Login form detected: {debug_info.get('login_form_exists', False)}")
            logger.info(f"Logout link detected: {debug_info.get('logout_link_exists', False)}")
            logger.info(f"Cloudflare challenge: {debug_info.get('cloudflare_challenge_detected', False)}")
            logger.info(f"HTML preview: {debug_info.get('html_preview', '')[:200]}...")
            logger.info(f"=====================================")
        
        except Exception as e:
            logger.error(f"Error saving debug artifacts: {e}")

    def _check_session_valid(self) -> None:
        """
        Validate that the user is logged into CS.RIN.
        
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
            login_form_exists = debug_info.get('login_form_exists', False)
            logout_link_exists = debug_info.get('logout_link_exists', False)
            cf_challenge = debug_info.get('cloudflare_challenge_detected', False)
            cookie_count = debug_info.get('cookie_count', 0)
            
            # Check 1: Cloudflare challenge
            if cf_challenge:
                self._save_debug_artifacts("Cloudflare challenge detected")
                raise RuntimeError(
                    "CS.RIN session expired: Cloudflare challenge detected. "
                    "The forum is blocking automated access. "
                    "Please regenerate cookies by running login.py with a real browser."
                )
            
            # Check 2: Redirect to login page
            if "ucp.php?mode=login" in url.lower():
                self._save_debug_artifacts("Redirected to login page")
                raise RuntimeError(
                    "CS.RIN session expired: Redirected to login page. "
                    "Cookies are invalid or expired. "
                    "Please regenerate cookies by running login.py."
                )
            
            # Check 3: No cookies loaded at all
            if cookie_count == 0:
                self._save_debug_artifacts("No cookies loaded")
                raise RuntimeError(
                    f"CS.RIN session expired: No cookies loaded from {self.STATE_FILE}. "
                    "File does not exist or is invalid. "
                    "Please run login.py to generate a new session."
                )
            
            # Check 4: Login form present without logout link (not logged in)
            # The login form exists on every phpBB page, but if we're NOT logged in,
            # we'll see it in a specific context and there will be NO logout link.
            # If we ARE logged in, we'll have a logout link instead.
            if login_form_exists and not logout_link_exists:
                self._save_debug_artifacts("Login form present but no logout link - not authenticated")
                raise RuntimeError(
                    "CS.RIN session expired: Not authenticated. "
                    "Cookies were loaded but are invalid or expired. "
                    "Please regenerate cookies by running login.py."
                )
            
            # Check 5: Generic fallback - neither login form nor logout link
            # This shouldn't happen on a valid phpBB page, indicates structure changed
            if not login_form_exists and not logout_link_exists:
                logger.warning(
                    "Warning: Neither login form nor logout link detected. "
                    "Page structure may have changed. Continuing anyway."
                )
            
            # If we got here, session appears valid
            logger.debug("Session validation passed")
        
        except RuntimeError:
            # Re-raise RuntimeError (our session errors)
            raise
        except Exception as e:
            # Catch unexpected errors
            self._save_debug_artifacts(f"Unexpected error during session check: {e}")
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
