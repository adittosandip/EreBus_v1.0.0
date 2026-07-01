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
# Config
########################################

if [ ! -f config.yaml ]; then

    cp config.example.yaml config.yaml

    echo
    echo "[INFO] config.yaml has been created."
    echo
    echo "Please edit config.yaml and add your Telegram Bot Token and Chat ID."
    echo
    echo "Then run:"
    echo
    echo "bash install.sh"
    echo

    exit 0

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
