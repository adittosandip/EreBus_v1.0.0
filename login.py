from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_DIR = Path("cookies")
STATE_FILE = COOKIES_DIR / "state.json"

COOKIES_DIR.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context()
    page = context.new_page()

    print("\nOpening CS.RIN login page...")
    page.goto("https://cs.rin.ru/forum/", wait_until="networkidle")

    print("\n==========================================")
    print("1. Login to your CS.RIN account.")
    print("2. After login is complete, return here.")
    print("3. Press ENTER to save your login session.")
    print("==========================================\n")

    input("Press ENTER after you have logged in... ")

    context.storage_state(path=str(STATE_FILE))

    print(f"\nLogin session saved successfully!")
    print(f"File: {STATE_FILE}")

    browser.close()
