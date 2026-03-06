from pathlib import Path

from stok_takip import StockManager


def test_add_and_list_products(tmp_path: Path):
    manager = StockManager(tmp_path / "stok.json")
    manager.add_product("A1", "Kalem", 10, 5, 7.5)
    manager.add_product("A2", "Defter", 3, 4, 20)

    products = manager.list_products()
    assert [p.code for p in products] == ["A2", "A1"]
    assert manager.total_inventory_value() == 135


def test_low_stock_and_update(tmp_path: Path):
    manager = StockManager(tmp_path / "stok.json")
    manager.add_product("A1", "Kalem", 10, 5, 7.5)
    manager.update_stock("A1", -5)

    low = manager.low_stock_products()
    assert len(low) == 1
    assert low[0].code == "A1"


def test_cannot_drop_below_zero(tmp_path: Path):
    manager = StockManager(tmp_path / "stok.json")
    manager.add_product("A1", "Kalem", 1, 1, 1.0)

    try:
        manager.update_stock("A1", -2)
    except ValueError as exc:
        assert "sifirin altina" in str(exc)
    else:
        raise AssertionError("ValueError bekleniyordu")
