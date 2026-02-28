# Ürün Otomasyon ve Stok Takip Paneli

Basit bir ön-yüz çözümüyle aşağıdaki ihtiyaçlar için hazır bir panel:

- **Toplu ürün ekleme/güncelleme** (CSV üzerinden)
- **Tekil ürün ekleme**
- **Stok giriş/çıkış işlemleri**
- **Kritik stok alarmı**
- **İşlem logları**
- Veriler tarayıcıda `localStorage` içine kaydedilir.

## Çalıştırma

```bash
python3 -m http.server 4173
```

Ardından tarayıcıdan açın:

- `http://localhost:4173`

## CSV örneği

```text
SKU-001,Kablo,199.90,25
SKU-002,Powerbank,899.00,12
SKU-003,Kulaklık,499.90,4
```

> Not: Aynı SKU tekrar gelirse ürün adı/fiyatı güncellenir, stok miktarı mevcut stoğa eklenir.
