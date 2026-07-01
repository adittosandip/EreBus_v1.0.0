# EreBus

EreBus is a modular release monitoring system that watches multiple game release sources and sends Telegram notifications automatically.

## Features

- FitGirl
- Scene
- Skidrow
- Reddit RSS
- SQLite duplicate detection
- Telegram notifications
- Systemd support

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python monitor.py
```

## Requirements

- Python 3.11+
- requests
- beautifulsoup4
- feedparser
- lxml
