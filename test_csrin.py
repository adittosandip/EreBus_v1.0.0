from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(
        "https://cs.rin.ru/forum/search.php?author_id=885704&sr=posts",
        wait_until="networkidle",
        timeout=60000,
    )

    print("TITLE:", page.title())
    print("URL:", page.url)

    browser.close()
