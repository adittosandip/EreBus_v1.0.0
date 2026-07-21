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

import getpass
import paramiko

# ===== VPS Configuration =====
VPS_HOST = "89.58.35.2"
VPS_PORT = 22
VPS_USER = "root"
REMOTE_PATH = "/root/release-monitor/cookies/state.json"

print("\nUploading state.json to VPS...")

password = getpass.getpass("VPS Password: ")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(
    hostname=VPS_HOST,
    port=VPS_PORT,
    username=VPS_USER,
    password=password,
)

sftp = ssh.open_sftp()
sftp.put(str(STATE_FILE), REMOTE_PATH)
sftp.close()
ssh.close()

print("Upload completed successfully!")

print("Upload completed successfully!")

    print(f"\nLogin session saved successfully!")
    print(f"File: {STATE_FILE}")

    browser.close()
