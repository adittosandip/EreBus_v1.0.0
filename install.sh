#!/bin/bash

set -e

clear

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_DIR"

echo "Project Directory: $PROJECT_DIR"
echo

cat << "EOF"

███████╗██████╗ ███████╗██████╗ ██╗   ██╗███████╗
██╔════╝██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝
█████╗  ██████╔╝█████╗  ██████╔╝██║   ██║███████╗
██╔══╝  ██╔══██╗██╔══╝  ██╔══██╗██║   ██║╚════██║
███████╗██║  ██║███████╗██████╔╝╚██████╔╝███████║
╚══════╝╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝

                 E R E B U S

        Release Monitor Installer v1.0

EOF

echo "======================================================"
echo " Starting Installation..."
echo "======================================================"
echo

########################################
# Root Check
########################################

if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Please run as root."
    exit 1
fi

########################################
# OS Check
########################################

if [ ! -f /etc/debian_version ]; then
    echo "[ERROR] Only Debian / Ubuntu is supported."
    exit 1
fi

########################################
# Required Files
########################################

FILES=(
    "requirements.txt"
    "monitor.py"
    "loader.py"
    "telegram.py"
    "database.py"
    "release-monitor.service"
)

for file in "${FILES[@]}"
do
    if [ ! -f "$file" ]; then
        echo "[ERROR] Missing file: $file"
        exit 1
    fi
done

########################################
# Update
########################################

echo "[1/9] Updating package index..."
apt update

########################################
# Install Packages
########################################

echo
echo "[2/9] Installing required packages..."

apt install -y \
python3 \
python3-pip \
python3-venv \
git

########################################
# Virtual Environment
########################################

echo
echo "[3/9] Preparing virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created venv."
else
    echo "Existing venv found."
fi

source venv/bin/activate

########################################
# Python Packages
########################################

echo
echo "[4/9] Installing Python dependencies..."

pip install -r requirements.txt

########################################
# Create Directories
########################################

echo
echo "[5/9] Creating required directories..."

mkdir -p data
mkdir -p logs

########################################
# Configuration
########################################

echo
echo "[6/9] Checking configuration..."

if [ ! -f config.yaml ]; then

    echo
    echo "No configuration found."
    echo

    read -p "Telegram Bot Token: " BOT_TOKEN
    read -p "Telegram Chat ID: " CHAT_ID
    read -p "Check Interval (default 300): " INTERVAL

    if [ -z "$INTERVAL" ]; then
        INTERVAL=300
    fi

cat > config.yaml <<EOF
telegram:

  token: "$BOT_TOKEN"

  chat_id: "$CHAT_ID"

settings:

  interval: $INTERVAL

  timeout: 30

  user_agent: "Mozilla/5.0"

sites:

  fitgirl:
    enabled: true
    url: "https://fitgirl-repacks.site/"

  kaos:
    enabled: true
    url: "https://kaoskrew.org/viewforum.php?f=13"

  scene:
    enabled: true
    url: "https://scene.cat/"

  srrdb:
    enabled: true
    url: "https://www.srrdb.com/browse/order:date-desc/category:pc/1"

  skidrow:
    enabled: true
    url: "https://www.skidrowreloaded.com/"

  reddit:
    enabled: true
    rss: "https://rss.app/feeds/E8gQn63RJEIwh7To.xml"

EOF

    echo
    echo "[OK] Configuration created successfully."

fi

########################################
# Install Service
########################################

echo
echo "[7/9] Installing systemd service..."

sed "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
release-monitor.service \
> /etc/systemd/system/release-monitor.service

systemctl daemon-reload

########################################
# Enable Service
########################################

echo
echo "[8/9] Enabling service..."

systemctl enable release-monitor

########################################
# Start Service
########################################

echo
echo "[9/9] Starting service..."

systemctl restart release-monitor

########################################
# Status
########################################

echo
echo "======================================================"
echo " Service Status"
echo "======================================================"

systemctl --no-pager status release-monitor || true

echo
echo "======================================================"
echo " EreBus Installation Complete"
echo "======================================================"
echo

echo "Useful Commands"

echo
echo "systemctl status release-monitor"
echo "systemctl restart release-monitor"
echo "systemctl stop release-monitor"
echo "journalctl -u release-monitor -f"

echo
echo "Thank you for using EreBus!"
echo
