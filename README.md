# EreBus

EreBus is a modular release monitoring system that monitors multiple game release sources and automatically sends Telegram notifications.

---

## Features

- FitGirl Repack
- Scene.cat
- Skidrow
- Reddit RSS-voices38
- SRRDB
- SQLite duplicate detection
- Telegram notifications
- systemd service support
- One-command installer

---

## Quick Start

Clone the repository:

```bash
git clone https://github.com/adittosandip/EreBus.git
cd EreBus
```

Run the installer:

```bash
bash install.sh
```

If `config.yaml` is created:

1. Edit `config.yaml`
2. Run the installer again:

```bash
bash install.sh
```

---

## Service Commands

Check status:

```bash
systemctl status release-monitor
```

Restart:

```bash
systemctl restart release-monitor
```

Logs:

```bash
journalctl -u release-monitor -f
```

---

## Requirements

- Debian 12 / Ubuntu
- Python 3.11+
- Internet connection

---

## License

MIT License
