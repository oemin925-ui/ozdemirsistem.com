# Kişisel Stok Takip Programı

Bu proje, kendi ürün stoklarınızı komut satırından yönetebilmeniz için hazırlanmış basit bir Python uygulamasıdır.

## Özellikler

- Ürün ekleme / silme
- Stok giriş ve çıkış işlemleri
- Ürün adı, minimum stok ve birim fiyat güncelleme
- Tüm stokları tablo halinde listeleme
- Kritik stok seviyesindeki ürünleri görme
- Toplam envanter değerini hesaplama

## Kurulum

Python 3.10+ ile çalışır.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
```

## Kullanım

Varsayılan veri dosyası `stoklar.json` dosyasıdır.

```bash
python3 stok_takip.py ekle KLM01 "Kalem" 50 10 7.5
python3 stok_takip.py giris KLM01 20
python3 stok_takip.py cikis KLM01 5
python3 stok_takip.py guncelle KLM01 --min-stok 15 --birim-fiyat 8.0
python3 stok_takip.py liste
python3 stok_takip.py kritik
python3 stok_takip.py ozet
```

Farklı bir veri dosyası kullanmak isterseniz:

```bash
python3 stok_takip.py --db benim_stoklarim.json liste
```

## Test

```bash
pytest -q
```
