import sqlite3
from pathlib import Path

DB_PATH = Path("data/releases.db")


class Database:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS releases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def exists(self, link):
        self.cursor.execute(
            "SELECT id FROM releases WHERE link=?",
            (link,)
        )
        return self.cursor.fetchone() is not None

    def save(self, site, title, link):
        self.cursor.execute(
            "INSERT OR IGNORE INTO releases(site,title,link) VALUES(?,?,?)",
            (site, title, link)
        )

        self.conn.commit()

    def close(self):
        self.conn.close()
