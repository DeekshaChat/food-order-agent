from app.db import DB_PATH, get_conn, init_db

RESTAURANTS = [
    (1, "Pizza Piazza", "Italian", 4.3, 30),
    (2, "Spice Route", "North Indian", 4.5, 35),
    (3, "Dosa Darbar", "South Indian", 4.4, 25),
    (4, "Dragon Wok", "Chinese", 4.1, 30),
    (5, "Burger Barn", "Fast Food", 4.0, 20),
    (6, "Sweet Tooth", "Desserts", 4.6, 25),
]

# (restaurant_id, name, description, price, is_veg, allergens)
MENU = [
    (1, "Margherita Pizza", "Classic tomato, mozzarella and basil", 249, 1, "gluten,dairy"),
    (1, "Farmhouse Pizza", "Capsicum, onion, mushroom, corn", 329, 1, "gluten,dairy"),
    (1, "Pepperoni Pizza", "Spicy pepperoni with cheese", 399, 0, "gluten,dairy"),
    (1, "Garlic Bread", "Toasted bread with garlic butter", 119, 1, "gluten,dairy"),
    (1, "Penne Arrabbiata", "Penne in spicy tomato sauce", 229, 1, "gluten"),
    (2, "Paneer Butter Masala", "Paneer in creamy tomato gravy", 279, 1, "dairy,nuts"),
    (2, "Dal Makhani", "Slow-cooked black lentils", 219, 1, "dairy"),
    (2, "Butter Chicken", "Chicken in rich buttery gravy", 349, 0, "dairy,nuts"),
    (2, "Garlic Naan", "Tandoor-baked garlic flatbread", 59, 1, "gluten,dairy"),
    (2, "Veg Biryani", "Fragrant rice with vegetables", 239, 1, ""),
    (2, "Chicken Biryani", "Hyderabadi style chicken biryani", 319, 0, ""),
    (3, "Masala Dosa", "Crispy dosa with potato filling", 129, 1, ""),
    (3, "Idli Sambar", "Steamed rice cakes with sambar", 89, 1, ""),
    (3, "Medu Vada", "Fried lentil donuts", 99, 1, ""),
    (3, "Mysore Dosa", "Spicy red chutney dosa", 149, 1, ""),
    (3, "Filter Coffee", "South Indian filter coffee", 49, 1, "dairy"),
    (4, "Veg Hakka Noodles", "Wok-tossed noodles with vegetables", 179, 1, "gluten,soy"),
    (4, "Chilli Paneer", "Paneer tossed in spicy sauce", 249, 1, "soy,dairy"),
    (4, "Chicken Manchurian", "Fried chicken in Manchurian sauce", 289, 0, "soy,gluten"),
    (4, "Veg Fried Rice", "Stir-fried rice with vegetables", 169, 1, "soy"),
    (4, "Veg Manchow Soup", "Spicy soup with crispy noodles", 129, 1, "soy,gluten"),
    (5, "Classic Veg Burger", "Aloo tikki patty with lettuce", 139, 1, "gluten"),
    (5, "Chicken Burger", "Grilled chicken patty with mayo", 189, 0, "gluten,egg"),
    (5, "Cheese Fries", "Fries topped with cheese sauce", 129, 1, "dairy"),
    (5, "Peri Peri Fries", "Spicy seasoned fries", 109, 1, ""),
    (5, "Chocolate Shake", "Thick chocolate milkshake", 149, 1, "dairy"),
    (6, "Gulab Jamun", "Two pieces with sugar syrup", 79, 1, "dairy,gluten"),
    (6, "Chocolate Brownie", "Warm brownie with walnuts", 119, 1, "gluten,egg,nuts"),
    (6, "Rasmalai", "Soft paneer dumplings in milk", 99, 1, "dairy,nuts"),
    (6, "Vanilla Ice Cream", "Two scoops", 89, 1, "dairy"),
]

USERS = [
    (1, "Asha", "12 MG Road, Delhi"),
    (2, "Rohan", "45 Sector 21, Gurugram"),
    (3, "Meera", "8 Lake View, Jaipur"),
]

# (user_id, status, total, created_at, [(item_id, qty, price)])
ORDERS = [
    (1, "delivered", 578, "2026-09-20 19:30", [(1, 1, 249), (6, 1, 279), (9, 1, 59)]),
    (1, "delivered", 318, "2026-09-27 13:10", [(7, 1, 219), (9, 1, 59), (10, 1, 239)]),
    (2, "preparing", 428, "2026-10-24 12:45", [(18, 1, 249), (17, 1, 179)]),
    (3, "out_for_delivery", 258, "2026-10-24 12:30", [(12, 2, 129)]),
]

def seed():
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
    with get_conn() as conn:
        conn.executemany("INSERT INTO restaurants VALUES (?,?,?,?,?)", RESTAURANTS)
        for i, m in enumerate(MENU, start=1):
            conn.execute(
                "INSERT INTO menu_items (id, restaurant_id, name, description, price, is_veg, allergens) "
                "VALUES (?,?,?,?,?,?,?)", (i, *m))
        conn.executemany("INSERT INTO users VALUES (?,?,?)", USERS)
        for user_id, status, total, created, items in ORDERS:
            cur = conn.execute(
                "INSERT INTO orders (user_id, status, total, created_at) VALUES (?,?,?,?)",
                (user_id, status, total, created))
            for item_id, qty, price in items:
                conn.execute("INSERT INTO order_items VALUES (?,?,?,?)",
                             (cur.lastrowid, item_id, qty, price))
    print("Database seeded.")

if __name__ == "__main__":
    seed()