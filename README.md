# EreBus

EreBus is a modular release monitoring system that monitors multiple game release sources and automatically sends Telegram notifications.

---

## Features

- FitGirl Repack
- Scene.cat
- Skidrow
- Reddit RSS (voices38)
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

During installation, EreBus will ask for:

- Telegram Bot Token
- Telegram Chat ID
- Check Interval (optional)

The installer will automatically create `config.yaml`, install dependencies, configure the systemd service, and start the monitor.

---

## Service Commands

Start:

```bash
systemctl start release-monitor
```

Stop:

```bash
systemctl stop release-monitor
```

Restart:

```bash
systemctl restart release-monitor
```

Enable at boot:

```bash
systemctl enable release-monitor
```

Disable:

```bash
systemctl disable release-monitor
```

Check status:

```bash
systemctl status release-monitor
```

View logs:

```bash
journalctl -u release-monitor -f
```

---

## Requirements

- Debian 12 or Ubuntu
- Python 3.11+
- Internet connection

---

## License

MIT License
