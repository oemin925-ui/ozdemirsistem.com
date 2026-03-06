#!/usr/bin/env python3
"""Basit stok takip uygulamasi (CLI)."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

DEFAULT_DB_PATH = Path("stoklar.json")


@dataclass
class Product:
    code: str
    name: str
    quantity: int
    min_quantity: int
    unit_price: float

    @property
    def total_value(self) -> float:
        return self.quantity * self.unit_price


class StockManager:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self.products: Dict[str, Product] = {}
        self.load()

    def load(self) -> None:
        if not self.db_path.exists():
            self.products = {}
            return

        raw = json.loads(self.db_path.read_text(encoding="utf-8"))
        self.products = {
            item["code"]: Product(**item)
            for item in raw
        }

    def save(self) -> None:
        data = [asdict(product) for product in self.products.values()]
        self.db_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def add_product(
        self,
        code: str,
        name: str,
        quantity: int,
        min_quantity: int,
        unit_price: float,
    ) -> Product:
        if code in self.products:
            raise ValueError(f"{code} kodlu urun zaten var.")
        if quantity < 0 or min_quantity < 0 or unit_price < 0:
            raise ValueError("Miktar, minimum miktar ve birim fiyat negatif olamaz.")

        product = Product(
            code=code,
            name=name,
            quantity=quantity,
            min_quantity=min_quantity,
            unit_price=unit_price,
        )
        self.products[code] = product
        self.save()
        return product

    def remove_product(self, code: str) -> None:
        if code not in self.products:
            raise ValueError(f"{code} kodlu urun bulunamadi.")
        del self.products[code]
        self.save()

    def update_stock(self, code: str, delta: int) -> Product:
        product = self.get_product(code)
        new_qty = product.quantity + delta
        if new_qty < 0:
            raise ValueError("Stok miktari sifirin altina dusmez.")
        product.quantity = new_qty
        self.save()
        return product

    def update_product(
        self,
        code: str,
        name: str | None = None,
        min_quantity: int | None = None,
        unit_price: float | None = None,
    ) -> Product:
        product = self.get_product(code)
        if name:
            product.name = name
        if min_quantity is not None:
            if min_quantity < 0:
                raise ValueError("Minimum stok negatif olamaz.")
            product.min_quantity = min_quantity
        if unit_price is not None:
            if unit_price < 0:
                raise ValueError("Birim fiyat negatif olamaz.")
            product.unit_price = unit_price

        self.save()
        return product

    def get_product(self, code: str) -> Product:
        if code not in self.products:
            raise ValueError(f"{code} kodlu urun bulunamadi.")
        return self.products[code]

    def list_products(self) -> List[Product]:
        return sorted(self.products.values(), key=lambda p: p.name.lower())

    def low_stock_products(self) -> List[Product]:
        return [p for p in self.list_products() if p.quantity <= p.min_quantity]

    def total_inventory_value(self) -> float:
        return sum(product.total_value for product in self.products.values())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kisisel stok takip uygulamasi")
    parser.add_argument(
        "--db", default=str(DEFAULT_DB_PATH), help="JSON veri dosyasi yolu"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("ekle", help="Yeni urun ekle")
    add_parser.add_argument("kod")
    add_parser.add_argument("ad")
    add_parser.add_argument("miktar", type=int)
    add_parser.add_argument("min_stok", type=int)
    add_parser.add_argument("birim_fiyat", type=float)

    remove_parser = subparsers.add_parser("sil", help="Urun sil")
    remove_parser.add_argument("kod")

    giris_parser = subparsers.add_parser("giris", help="Stok girisi yap")
    giris_parser.add_argument("kod")
    giris_parser.add_argument("miktar", type=int)

    cikis_parser = subparsers.add_parser("cikis", help="Stok cikisi yap")
    cikis_parser.add_argument("kod")
    cikis_parser.add_argument("miktar", type=int)

    guncelle_parser = subparsers.add_parser("guncelle", help="Urun bilgilerini guncelle")
    guncelle_parser.add_argument("kod")
    guncelle_parser.add_argument("--ad")
    guncelle_parser.add_argument("--min-stok", type=int)
    guncelle_parser.add_argument("--birim-fiyat", type=float)

    subparsers.add_parser("liste", help="Tum urunleri listele")
    subparsers.add_parser("kritik", help="Kritik stok urunleri listele")
    subparsers.add_parser("ozet", help="Toplam stok degerini goster")

    return parser


def format_table(products: List[Product]) -> str:
    if not products:
        return "Kayitli urun yok."

    headers = ["Kod", "Urun", "Miktar", "Min", "Birim", "Toplam"]
    rows = [
        [
            p.code,
            p.name,
            str(p.quantity),
            str(p.min_quantity),
            f"{p.unit_price:.2f}",
            f"{p.total_value:.2f}",
        ]
        for p in products
    ]

    widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def fmt(row: List[str]) -> str:
        return " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row))

    line = "-+-".join("-" * width for width in widths)
    output = [fmt(headers), line]
    output.extend(fmt(row) for row in rows)
    return "\n".join(output)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    manager = StockManager(Path(args.db))

    try:
        if args.command == "ekle":
            product = manager.add_product(
                args.kod, args.ad, args.miktar, args.min_stok, args.birim_fiyat
            )
            print(f"Urun eklendi: {product.name} ({product.code})")

        elif args.command == "sil":
            manager.remove_product(args.kod)
            print(f"Urun silindi: {args.kod}")

        elif args.command == "giris":
            if args.miktar <= 0:
                raise ValueError("Stok giris miktari pozitif olmali.")
            product = manager.update_stock(args.kod, args.miktar)
            print(f"Yeni stok miktari: {product.code} -> {product.quantity}")

        elif args.command == "cikis":
            if args.miktar <= 0:
                raise ValueError("Stok cikis miktari pozitif olmali.")
            product = manager.update_stock(args.kod, -args.miktar)
            print(f"Yeni stok miktari: {product.code} -> {product.quantity}")

        elif args.command == "guncelle":
            product = manager.update_product(
                args.kod, name=args.ad, min_quantity=args.min_stok, unit_price=args.birim_fiyat
            )
            print(f"Urun guncellendi: {product.name} ({product.code})")

        elif args.command == "liste":
            print(format_table(manager.list_products()))

        elif args.command == "kritik":
            critical = manager.low_stock_products()
            if not critical:
                print("Kritik seviyede urun yok.")
            else:
                print(format_table(critical))

        elif args.command == "ozet":
            print(f"Toplam urun adedi: {sum(p.quantity for p in manager.products.values())}")
            print(f"Toplam envanter degeri: {manager.total_inventory_value():.2f} TL")

    except ValueError as exc:
        print(f"Hata: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
