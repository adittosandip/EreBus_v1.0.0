from pathlib import Path
from playwright.sync_api import sync_playwright
import getpass
import paramiko

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

    print("\nLogin session saved successfully!")
    print(f"File: {STATE_FILE}")

    print("\n========== VPS Upload ==========")

    VPS_HOST = input("VPS IP/Host: ").strip()
    while not VPS_HOST:
        VPS_HOST = input("VPS IP/Host (required): ").strip()

    VPS_PORT = input("VPS Port [22]: ").strip()
    VPS_PORT = int(VPS_PORT) if VPS_PORT else 22

    VPS_USER = input("VPS Username [root]: ").strip()
    VPS_USER = VPS_USER if VPS_USER else "root"

    REMOTE_PATH = input(
        "Remote Path [/root/release-monitor/cookies/state.json]: "
    ).strip()
    REMOTE_PATH = (
        REMOTE_PATH
        if REMOTE_PATH
        else "/root/release-monitor/cookies/state.json"
    )

    password = getpass.getpass("VPS Password: ")

    print("\nUploading state.json to VPS...")

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

    print("\nUpload completed successfully!")
    print(f"Uploaded to: {VPS_HOST}:{REMOTE_PATH}")

    browser.close()
