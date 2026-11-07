# Security

> Ajanların her planda ve review'da uyduğu temel kurallar (bootstrap, 2026-11-07).

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- Oturum imza anahtarı `.env`'den okunur. Demo kullanıcı şifreleri yalnızca yerel seed betiğinde
  üretilir, repoya yazılmaz.

## Input & output
- Tüm girdiler sınırda (`api/`) Pydantic şemalarıyla doğrulanır; bilinmeyen alanlar reddedilir
  (`extra="forbid"`).
- SQL yalnızca SQLAlchemy ile, parametreli; string birleştirmeyle SQL yok.
- Frontend'de kullanıcı verisi DOM'a **yalnızca `textContent`** ile yazılır; `innerHTML` yok (XSS).
- Hata yanıtlarında stack trace, SQL veya iç detay sızmaz (`docs/conventions.md` "Error
  handling"); şifre ve token'lar loglanmaz.
- Güvenlik header'ları: `Content-Security-Policy: default-src 'self'`,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy`.

## AuthN / AuthZ
- **AuthN:** e-posta + şifre; şifreler **argon2** (`argon2-cffi`) ile hash'lenir. Oturum
  **HttpOnly + SameSite=Lax + Secure** (üretimde) cookie'de imzalı token; frontend token'ı JS'te
  tutmaz (`localStorage` yok).
- **CSRF:** oturum gerektiren durum değiştiren isteklerde (POST/PUT/PATCH/DELETE) **oturuma
  bağlı token**, `X-CSRF-Token` header'ı. Token imzalı oturumun içindedir; istemci onu giriş ve
  `/api/v1/auth/me` yanıtının gövdesinden alır, sunucu header'ı oturumdakiyle sabit zamanlı
  karşılaştırır (`services/auth.py`). Giriş isteği token istemez: henüz oturum yoktur ve cookie
  SameSite=Lax'tır (spec 0002, plan R-2).
- **Default deny:** `/api/v1/auth/login`, sistem durumu sorgusu (`/api/v1/health` — yalnızca
  çalışma durumu, sürüm ve veritabanı erişimi; gizli bilgi yok, spec 0001) ve statik dosyalar
  dışındaki her uç kimlik doğrulama ister.
- **AuthZ (hassas alan, BR-6):** yetki kararı **yalnızca `services/`** katmanında verilir
  (ör. `can_decide(actor, request)`); `api/` yalnızca oturumdaki kullanıcıyı servise iletir.
  Frontend'deki gizleme/gösterme güvenlik değildir.
- Çalışan yalnızca **kendi** taleplerini ve bakiyesini görür; yönetici yalnızca **kendi ekibini**;
  izin türlerini ve hakları yalnızca İK yönetir.
- Var olan ama erişim izni olmayan kaynak → **404** (başka ekibin taleplerinin varlığı sızmaz);
  görünür kaynakta yetki kuralı ihlali (örn. kendi talebini onaylama) → **403**.

## Dependencies
- Yeni bağımlılık **yalnızca onaylı bir planla** eklenir. Plan adını, gerekçesini, lisansını
  (MIT/BSD/Apache uyumlu) ve bakım durumunu (son 12 ayda sürüm) yazar; onayı planı onaylayan
  insan verir.
- Sürümler `uv.lock` ile kilitli; lock commit edilir.
- `check` (yalnızca full profil, ağ gerektirir) **pip-audit** ile bilinen CVE'leri tarar.

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
