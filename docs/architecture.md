# Architecture

> Karar verilen mimari — bir hedef değil. Ajanlar plan yapmadan önce bu dosyayı okur.

## System overview

Tek bir Python/FastAPI uygulaması ve tek bir SQLite veritabanından oluşan **klasik N-katmanlı
monolit**. İstek her zaman Sunum → İş → Veri erişimi → DB yönünde akar; her katman yalnızca
hemen altındakini çağırır. Frontend build adımı olmayan düz HTML/CSS/JS'tir; FastAPI tarafından
statik dosya olarak sunulur ve yalnızca `/api/v1/...` HTTP uçlarıyla konuşur. Gerekçe: kurs
demosu için anlatması en kolay, en az hareketli parçalı yapı; sınırlar yine de import-linter ile
araçla zorlanır (bootstrap kararı, 2026-11-07).

## Modules / components and ownership

Kod: `src/leave_manager/`. Testler: `tests/`.

| Module | Single responsibility | Owns |
|---|---|---|
| `api/` (Sunum) | FastAPI router'ları, Pydantic istek/yanıt şemaları, HTTP durum kodları, oturumdaki kullanıcıyı servise iletme, tek exception handler | HTTP sözleşmesi |
| `services/` (İş) | BR-1…BR-8, yetki kararı (BR-6), iş günü hesabı, transaction sınırı | İş kuralları |
| `repositories/` (Veri erişimi) | SQLAlchemy sorguları ve kayıt | Sorgular |
| `models/` (Domain / Model) | SQLAlchemy ORM varlıkları (User, Team, LeaveType, Entitlement, LeaveRequest, LeaveBalance), `LeaveRequestStatus` enum | Veri şeması |
| `core/` (Altyapı) | Ayarlar, DB oturumu, `Clock` soyutlaması, alan hata tipleri (`core/errors.py`) | — |
| `static/` (Frontend) | HTML/CSS/JS arayüz (ES modules); yalnızca HTTP API'yi çağırır | — |
| `migrations/` | Alembic migration'ları — tek şema değişikliği yolu | Şema geçmişi |

## Communication rules

- Katmanlar arası çağrı senkron fonksiyon çağrısıdır; event/kuyruk yoktur.
- Her katman yalnızca **hemen altındaki** katmanı çağırır: `api → services → repositories`.
  `models/` ve `core/` her katmandan kullanılabilir.
- Talep onayı ile bakiye düşme (BR-3, BR-5) aynı servis çağrısında, **tek bir DB
  transaction'ında** yapılır; transaction sınırı `services/` katmanındadır.

## Forbidden dependencies (make them testable)

`check` içindeki `lint-imports` (import-linter, sözleşmeler `pyproject.toml`'da) bunları zorlar:

- **F-1:** `api/` hiçbir zaman `repositories/` veya `sqlalchemy`'yi doğrudan import etmez —
  yalnızca `services/`.
- **F-2:** `services/` `fastapi`'yi import etmez (iş kuralları HTTP'den bağımsız).
- **F-3:** Alt katman üst katmanı import etmez (`repositories` → `services`/`api` yok;
  `services` → `api` yok). import-linter `layers`: `api > services > repositories > models`.
- **F-4:** `models/` ve `core/` üst katmanların (`api`, `services`, `repositories`) hiçbirini
  import etmez.
- **F-5:** Frontend (`static/`) veritabanına veya Python koduna bağlı değildir; yalnızca HTTP API.
  (Review'da kontrol edilir: `static/` altında yalnızca `/api/v1/` çağrıları.)

## Deliberately out of scope

Mikroservisler, mesaj kuyruğu, önbellek katmanı, SPA framework'ü veya ayrı frontend projesi,
npm/JS build adımı, çok kiracılık (multi-tenant), bordro ve e-posta entegrasyonu.
