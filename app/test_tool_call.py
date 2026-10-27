import pytest
from app import db, seed, tools


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", path)
    monkeypatch.setattr(seed, "DB_PATH", path)
    seed.seed()


def test_search_veg_under_200():
    res = tools.search_menu(max_price=200, veg_only=True)
    assert res["count"] > 0
    assert all(i["veg"] and i["price"] <= 200 for i in res["items"])


def test_search_by_keyword():
    res = tools.search_menu(query="pizza")
    assert res["count"] > 0
    assert all("pizza" in i["name"].lower() or "pizza" in i["restaurant"].lower()
               for i in res["items"])


def test_exclude_allergen():
    res = tools.search_menu(query="biryani", exclude_allergen="nuts")
    assert all("nuts" not in i["allergens"] for i in res["items"])


def test_add_invalid_item():
    assert "error" in tools.add_to_cart(1, 9999, 1)


def test_add_bad_quantity():
    assert "error" in tools.add_to_cart(1, 1, 0)


def test_cart_accumulates_and_totals():
    tools.add_to_cart(1, 1, 1)   # Margherita, 249
    tools.add_to_cart(1, 1, 1)
    cart = tools.view_cart(1)
    assert cart["items"][0]["quantity"] == 2
    assert cart["total"] == 498


def test_place_order_empty_cart():
    assert "error" in tools.place_order(1)


def test_place_order_clears_cart():
    tools.add_to_cart(1, 12, 2)  # Masala Dosa, 129
    res = tools.place_order(1)
    assert res["status"] == "preparing" and res["total"] == 258
    assert tools.view_cart(1)["items"] == []


def test_order_status_ownership():
    assert tools.get_order_status(2, 3)["status"] == "preparing"
    assert "error" in tools.get_order_status(1, 3)   # wrong user


def test_order_history():
    assert len(tools.get_order_history(1)["orders"]) == 2