import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "food.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY, name TEXT, cuisine TEXT,
    rating REAL, delivery_mins INTEGER
);
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY, restaurant_id INTEGER, name TEXT,
    description TEXT, price REAL, is_veg INTEGER,
    allergens TEXT, available INTEGER DEFAULT 1,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, name TEXT, address TEXT
);
CREATE TABLE IF NOT EXISTS cart_items (
    user_id INTEGER, item_id INTEGER, quantity INTEGER,
    PRIMARY KEY (user_id, item_id)
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
    status TEXT, total REAL, created_at TEXT
);
CREATE TABLE IF NOT EXISTS order_items (
    order_id INTEGER, item_id INTEGER, quantity INTEGER, price REAL
);
"""

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)