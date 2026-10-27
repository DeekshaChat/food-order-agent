from datetime import datetime
from app.db import get_conn

STOPWORDS = {"veg", "vegetarian", "food", "dish", "dishes", "items",
             "under", "a", "the", "some", "me", "show"}


def search_menu(query="", max_price=None, veg_only=False, exclude_allergen=None, limit=8):
    """Search available menu items by keyword, price, veg preference and allergen."""
    sql = """SELECT m.id, m.name, m.description, m.price, m.is_veg, m.allergens,
                    r.name AS restaurant, r.cuisine
             FROM menu_items m JOIN restaurants r ON r.id = m.restaurant_id
             WHERE m.available = 1"""
    params = []
    if max_price is not None:
        sql += " AND m.price <= ?"
        params.append(float(max_price))
    if veg_only:
        sql += " AND m.is_veg = 1"

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()

    words = [w for w in (query or "").lower().split() if w not in STOPWORDS]
    results = []
    for r in rows:
        allergens = [a for a in r["allergens"].split(",") if a]
        if exclude_allergen and exclude_allergen.lower() in allergens:
            continue
        haystack = f"{r['name']} {r['description']} {r['restaurant']} {r['cuisine']}".lower()
        score = sum(w in haystack for w in words)
        if words and score == 0:
            continue
        results.append((score, r["price"], {
            "item_id": r["id"], "name": r["name"], "restaurant": r["restaurant"],
            "price": r["price"], "veg": bool(r["is_veg"]), "allergens": allergens,
        }))
    results.sort(key=lambda x: (-x[0], x[1]))
    items = [x[2] for x in results[:limit]]
    return {"count": len(items), "items": items}


def add_to_cart(user_id, item_id, quantity=1):
    """Add an item to the user's cart. Quantity must be 1-10."""
    user_id, item_id, quantity = int(user_id), int(item_id), int(quantity)
    if not 1 <= quantity <= 10:
        return {"error": "Quantity must be between 1 and 10."}
    with get_conn() as conn:
        item = conn.execute("SELECT name, available FROM menu_items WHERE id=?",
                            (item_id,)).fetchone()
        if item is None:
            return {"error": f"No menu item with id {item_id}."}
        if not item["available"]:
            return {"error": f"{item['name']} is currently unavailable."}
        conn.execute(
            """INSERT INTO cart_items (user_id, item_id, quantity) VALUES (?,?,?)
               ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + excluded.quantity""",
            (user_id, item_id, quantity))
    return {"added": item["name"], "quantity": quantity}


def view_cart(user_id):
    """Show the items in the user's cart and the total price."""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT m.id, m.name, m.price, c.quantity
               FROM cart_items c JOIN menu_items m ON m.id = c.item_id
               WHERE c.user_id = ?""", (int(user_id),)).fetchall()
    items = [{"item_id": r["id"], "name": r["name"], "price": r["price"],
              "quantity": r["quantity"], "subtotal": r["price"] * r["quantity"]} for r in rows]
    return {"items": items, "total": sum(i["subtotal"] for i in items)}


def place_order(user_id):
    """Place an order for everything in the cart, then empty the cart."""
    user_id = int(user_id)
    cart = view_cart(user_id)
    if not cart["items"]:
        return {"error": "Cart is empty. Add items before placing an order."}
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO orders (user_id, status, total, created_at) VALUES (?,?,?,?)",
            (user_id, "preparing", cart["total"], datetime.now().strftime("%Y-%m-%d %H:%M")))
        order_id = cur.lastrowid
        for i in cart["items"]:
            conn.execute("INSERT INTO order_items VALUES (?,?,?,?)",
                         (order_id, i["item_id"], i["quantity"], i["price"]))
        conn.execute("DELETE FROM cart_items WHERE user_id=?", (user_id,))
    return {"order_id": order_id, "status": "preparing", "total": cart["total"]}


def get_order_status(user_id, order_id):
    """Get the status of one of the user's orders."""
    with get_conn() as conn:
        row = conn.execute("SELECT id, user_id, status, total, created_at FROM orders WHERE id=?",
                           (int(order_id),)).fetchone()
    if row is None or row["user_id"] != int(user_id):
        return {"error": f"No order {order_id} found for this user."}
    return {"order_id": row["id"], "status": row["status"],
            "total": row["total"], "placed_at": row["created_at"]}


def get_order_history(user_id, limit=5):
    """List the user's most recent orders."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, status, total, created_at FROM orders WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (int(user_id), limit)).fetchall()
    return {"orders": [dict(r) for r in rows]}