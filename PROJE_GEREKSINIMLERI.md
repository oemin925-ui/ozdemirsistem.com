# Misafirhane Rezervasyon Sistemi (Android + iOS + Web)

Bu doküman; 3 daireli (Daire 2, Daire 5, Daire 8), toplam 10 kullanıcılı bir misafirhane rezervasyon sistemi için ihtiyaçları ve önerilen teknik tasarımı özetler.

## 1) Hedef

- Kullanıcılar mobil (Android/iOS) ve web üzerinden daire rezervasyonu yapabilsin.
- Tabloda kimin rezervasyon yaptığı görünsün.
- Kimin rezervasyonu sildiği (audit log) takip edilsin.
- Genel kullanıcı tablosunda rezervasyonlar "Rezervasyon Var" gibi görünsün; admin detayda yazılan ismi görsün.
- Rezervasyon girilirken tarih çakışması varsa anında uyarı verilsin.
- Aylık daire bazlı rapor alınabilsin.

## 2) Roller

1. **Admin**
   - Tüm rezervasyon detaylarını görür (giren kişi, silen kişi, zaman damgaları).
   - Kullanıcı yönetimi yapar.
   - Aylık raporları alır / dışa aktarır.

2. **Standart Kullanıcı (10 kişi)**
   - Rezervasyon oluşturur, kendi rezervasyonunu günceller/siler.
   - Tabloda diğer kayıtları detay isim yerine "Rezervasyon" olarak görür.
   - Kendi oluşturduğu kaydın adını ve detayını görebilir.

## 3) Daireler

- Daire 2
- Daire 5
- Daire 8

> Sistem başlangıçta bu 3 daire sabit gelir, ileride panelden yeni daire eklenebilir şekilde tasarlanır.

## 4) Ekranlar

## 4.1 Giriş / Yetkilendirme
- E-posta + şifre ile giriş (opsiyonel SMS doğrulama).
- Rol bazlı yetki (admin / kullanıcı).

## 4.2 Rezervasyon Takvim Tablosu
- Satırlar: Daireler (2,5,8)
- Sütunlar: Günler (ay görünümü)
- Hücre durumu:
  - Boş
  - Rezervasyon var
- Kullanıcı görünümü:
  - Detay isim gizli ("Rezervasyon")
- Admin görünümü:
  - Detay isim açık (misafir adı / açıklama)
- Kayıt üzerine tıklayınca:
  - Oluşturan kullanıcı
  - Oluşturma tarihi
  - (Silindiyse) Silen kullanıcı + silme tarihi (logdan)

## 4.3 Rezervasyon Oluşturma
- Alanlar:
  - Daire
  - Giriş tarihi
  - Çıkış tarihi
  - Misafir adı
  - Not
- Kural:
  - Aynı daire için tarih aralığı çakışıyorsa **kaydetme engellenir**.
  - Kullanıcıya net uyarı: "Seçtiğiniz tarihler dolu. Lütfen farklı tarih seçiniz."

## 4.4 Raporlama (Aylık)
- Daire bazlı doluluk oranı (%).
- Toplam rezervasyon sayısı.
- İptal/silme sayısı.
- En çok kullanılan daire.
- Excel/PDF dışa aktarma.

## 5) İş Kuralları

1. Tarih çakışma kontrolü zorunlu.
2. Geçmiş tarihe yeni rezervasyon açılamaz (opsiyonel, kuruma göre değişebilir).
3. Kullanıcı sadece kendi rezervasyonunu silebilir; admin herkesi silebilir.
4. Silinen rezervasyonlar fiziksel olarak kaybolmaz, `is_deleted = true` ve log kaydı ile tutulur.
5. Tüm kritik işlemler audit log’a yazılır.

## 6) Önerilen Veritabanı Şeması

## 6.1 `users`
- `id` (PK)
- `full_name`
- `email` (unique)
- `password_hash`
- `role` (`admin` / `user`)
- `is_active`
- `created_at`

## 6.2 `apartments`
- `id` (PK)
- `name` (ör: Daire 2)
- `is_active`

## 6.3 `reservations`
- `id` (PK)
- `apartment_id` (FK -> apartments)
- `start_date`
- `end_date`
- `guest_name`
- `note`
- `created_by` (FK -> users)
- `updated_by` (FK -> users, nullable)
- `deleted_by` (FK -> users, nullable)
- `is_deleted` (bool)
- `created_at`
- `updated_at`
- `deleted_at`

## 6.4 `audit_logs`
- `id` (PK)
- `entity_type` (reservation)
- `entity_id`
- `action` (`create` / `update` / `delete`)
- `old_value` (json)
- `new_value` (json)
- `performed_by` (FK -> users)
- `performed_at`

## 7) Çakışma Kontrolü (Örnek Mantık)

Aynı daire için aşağıdaki koşul sağlanırsa çakışma vardır:

- `new_start < existing_end` VE
- `new_end > existing_start`

Ayrıca sadece `is_deleted = false` kayıtlar dikkate alınır.

## 8) API Önerisi (Özet)

- `POST /auth/login`
- `GET /apartments`
- `GET /reservations?month=2026-04`
- `POST /reservations`
- `PUT /reservations/{id}`
- `DELETE /reservations/{id}`
- `GET /reports/monthly?month=2026-04`

## 9) Teknoloji Önerisi

### Seçenek A (tek kod tabanı)
- **Frontend:** Flutter (Android + iOS + Web)
- **Backend:** Node.js (NestJS)
- **DB:** PostgreSQL
- **Auth:** JWT + Refresh Token

### Seçenek B
- **Mobil:** React Native
- **Web:** React
- **Backend:** .NET / Node.js
- **DB:** PostgreSQL

> Küçük ekip ve hızlı çıkış için Seçenek A daha pratiktir.

## 10) Güvenlik ve Kayıt

- Rol bazlı erişim kontrolü (RBAC).
- Tüm API çağrılarında kullanıcı kimliği zorunlu.
- Silme/güncelleme aksiyonlarında audit log.
- Kişisel veri için loglarda hassas alan maskeleme.
- Düzenli yedekleme (günlük).

## 11) MVP (İlk Sürüm) Kapsamı

1. Giriş + rol yönetimi
2. 3 daire için takvim tablosu
3. Rezervasyon ekle/güncelle/sil
4. Çakışma kontrolü ve dolu tarih uyarısı
5. Admin için detay görünümü + silen/oluşturan bilgisi
6. Aylık daire raporu (ekranda + Excel)

## 12) Sonraki Faz

- Bildirimler (rezervasyon yaklaşınca)
- Çoklu misafirhane desteği
- Onay akışı (rezervasyon talebi -> admin onayı)
- Takvim senkronizasyonu (Google/Outlook)

