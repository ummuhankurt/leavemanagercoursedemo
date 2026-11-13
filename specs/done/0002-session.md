# Spec 0002 — Oturum (giriş / çıkış, sunucu tarafı)

- Status: Shipped
- Mode: lite
- Plan: `specs/plans/0002-plan.md`
- Self-critique: done

## Intent

Uygulamanın her iş özelliği (talep, onay, bakiye) isteği **kimin** yaptığını bilmek zorundadır;
`docs/security.md` de durum sorgusu dışındaki her ucu kimlik doğrulamaya bağlar. Bu iş, örnek
çalışan, yönetici ve İK kullanıcılarının e-posta ve şifreyle oturum açmasını, kim olduklarını ve
rollerini sorgulamasını ve oturumu kapatmasını sunucu tarafında sağlar. Başarı: seed
kullanıcılarıyla oturum açılır, sonraki spec'ler "oturumdaki kullanıcı ve rolü" üzerine
kurulabilir, oturumsuz hiçbir korunan bilgiye erişilemez. Bilinçli olarak yapılmayanlar: giriş
ekranı (spec 0003), kayıt, şifre sıfırlama/değiştirme, kullanıcı yönetimi, ekip ataması, deneme
sınırı/hesap kilitleme ve talep yetkileri (BR-6).

## Requirements

- R-1: Kayıtlı bir kullanıcı e-posta ve şifresiyle oturum açabilir. Zaten oturumu olan biri
  tekrar giriş yaparsa yeni oturum eskisinin yerine geçer (G-3).
- R-2: E-posta karşılaştırması büyük/küçük harfe duyarsızdır; baştaki ve sondaki boşluklar yok
  sayılır. Şifre olduğu gibi karşılaştırılır.
- R-3: Bilinmeyen e-posta ve yanlış şifre aynı genel hata ile reddedilir; yanıt hangi e-postaların
  kayıtlı olduğunu ele vermez.
- R-4: Oturumdaki kullanıcı kendi adını, e-postasını ve rolünü sorgulayabilir. Oturum yoksa,
  süresi dolmuşsa veya geçersizse sistem "giriş yapılmamış" yanıtı verir.
- R-5: Oturum, başladığı andan itibaren sabit 8 saat geçerlidir; tam 8. saatte ve sonrasında
  geçersizdir. Kullanım süreyi uzatmaz; "beni hatırla" yoktur. "Şimdi" sistemin saat
  soyutlamasından gelir (G-4).
- R-6: Kullanıcı oturumu kapatabilir; kapatıldıktan sonra o tarayıcıda oturum yoktur.
- R-7: Oturum gerektiren her durum değiştiren istek CSRF korumasına tabidir; istemci, geçerli
  token'ı oturum açılışında ve oturum sorgusunda edinebilir. Oturum açma isteği CSRF token'ı
  istemez — henüz oturum yoktur ve cookie SameSite=Lax'tır (G-7).
- R-8: Her kullanıcının tam olarak bir rolü vardır: `Employee`, `Manager` veya `HR`.
- R-9: Örnek kullanıcılar yerel bir seed adımıyla oluşturulur (her rolden en az bir kullanıcı).
  Seed demo şifresini ortamdan okur; tanımlı değilse kullanıcı oluşturmadan açıklayıcı bir
  hatayla durur ve şifreyi hiçbir yere yazdırmaz. Şifreler yalnızca hash'lenmiş saklanır (G-5).
- R-10: Oturum imza anahtarı ortamda tanımlı değilse uygulama başlamayı açıklayıcı bir hatayla
  reddeder; varsayılan anahtar yoktur (G-6).
- R-11: Durum sorgusu ve ana sayfa oturumsuz erişilebilir kalır; bu işte eklenen diğer her uç
  oturum ister (default deny).
- R-12: Geçersiz girdi (eksik/boş alan, bilinmeyen alan) ve framework kaynaklı hatalar (bulunamadı,
  izin verilmeyen yöntem) projenin standart hata biçiminde döner (backlog B-1'i kapatır, G-8).
- R-13: Her yanıt projenin güvenlik header'larını taşır (`docs/security.md`, Input & output).

## User experience

none — no user interface. Giriş ekranı spec 0003'tür; bu işte ana sayfa değişmez.

## Constraints & out of scope

- Sensitive area: Yetkilendirme — bu iş kimliği ve rolü belirler; sonraki her yetki kararı
  (BR-6) buna dayanır.
- Out of scope: giriş ekranı (spec 0003), kayıt, şifre sıfırlama/değiştirme, kullanıcı yönetimi,
  pasif kullanıcı, ekip ataması, deneme sınırı / hesap kilitleme / rate limiting, çok faktörlü
  doğrulama, talep ve onay yetkileri (BR-6 sonraki spec'lerde).
- Kabul edilen risk (karar: Ümmühan Kurt, 2026-11-07): oturum sunucuda tutulmaz. Kapatma oturumu
  tarayıcıdan siler; ancak kopyalanmış/çalınmış bir oturum, başladığı andan 8 saat dolana kadar
  geçerli kalır. Sunucu tarafı iptal gerekirse ayrı spec.
- Sırlar (`docs/security.md`, Secrets): imza anahtarı ve demo şifresi ortamdan okunur;
  `.env.example`'da yalnızca yer tutucu bulunur. Testler kendi kullanıcılarını ve anahtarlarını
  oluşturur, seed şifresine bağlı değildir.
- Stack ve sürümler `docs/conventions.md`; yeni bağımlılıklar (ör. şifre hash'leme, imzalama)
  `docs/security.md` "Dependencies"e göre planda listelenir.
- B-1 bu işin commit'inde `specs/backlog.md`'den silinir (G-8).
- Kanıt yöntemi: tüm kriterler otomatik testlerle (entegrasyon; AC-4'teki süre sınırı sabit
  zamanlı saatle). AC-10 bir başlatma testiyle.
- Split: 0002 (bu spec) + 0003 Giriş ekranı — Ümmühan Kurt, 2026-11-07, 16 kriter boyut sınırını
  aşıyordu; hassas alanda daha küçük review (G-1).

## Acceptance criteria

- [x] AC-1 — Doğru e-posta ve şifreyle oturum açılır; ardından oturum sorgusu kullanıcının adını,
  e-postasını ve rolünü döner; yanıtta şifre veya hash yoktur. Oturumu olan biri tekrar giriş
  yaparsa yeni kullanıcının bilgileri döner.
- [x] AC-2 — E-posta farklı büyük/küçük harfle ve baş/son boşluklu girildiğinde oturum yine açılır.
- [x] AC-3 — Yanlış şifre ve kayıtlı olmayan e-posta aynı HTTP durumunu (401) ve aynı standart hata
  gövdesini döner.
- [x] AC-4 — Oturum yokken, oturum değiştirilmişken veya başlangıcından tam 8 saat (ve sonrası)
  geçmişken oturum sorgusu 401 ve standart hata gövdesi döner; 8 saatten bir saniye önce oturum
  hâlâ geçerlidir.
- [x] AC-5 — Oturum kapatıldıktan sonra oturum sorgusu 401 döner. CSRF token'ı olmadan veya yanlış
  token'la yapılan kapatma isteği 403 ile reddedilir ve oturum sürer. Oturum açma isteği CSRF
  token'ı olmadan kabul edilir.
- [x] AC-6 — Oturum cookie'si HttpOnly ve SameSite=Lax'tır; üretim ayarında Secure'dur.
- [x] AC-7 — Kullanıcının şifresi veritabanında yalnızca argon2 hash'i olarak bulunur. Seed her
  rolden en az bir kullanıcı oluşturur ve tekrar çalıştırıldığında kullanıcıları çoğaltmaz; demo
  şifresi tanımlı değilse hiç kullanıcı oluşturmadan hatayla durur.
- [x] AC-8 — Eksik/boş alanlı veya bilinmeyen alan içeren oturum açma isteği 422 döner; bilinmeyen
  bir yol 404, desteklenmeyen yöntem 405 döner; üçü de standart `{"error": {code, message}}`
  biçimindedir ve iç ayrıntı içermez.
- [x] AC-9 — Durum sorgusu ve ana sayfa oturumsuz erişilebilir; spec 0001'in AC-1…AC-6
  davranışı değişmez.
- [x] AC-10 — İmza anahtarı ortamda tanımlı değilken uygulama başlamaz ve hatası anahtarın eksik
  olduğunu söyler (anahtar değerini içermez).
- [x] AC-11 — Yanıtlar `Content-Security-Policy: default-src 'self'`,
  `X-Content-Type-Options: nosniff` ve `Referrer-Policy` header'larını taşır.

## Definition of Done
- [x] Every acceptance criterion mapped to proof (test or reproducible observation)
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale, deferred ones in `specs/backlog.md`
- [x] Docs / ADRs updated if behavior or architecture changed
- [x] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | 0 (yalnızca Status değişti; self-critique G-1…G-8 onaydan önce işlendi) |
| Fix rounds | 1 (M-1 kod + test, I-2 doküman) |
| Review findings: real / noise / deferred | 2 / 0 / 1 (M-1, I-2 / — / I-1→B-4); VERIFY: gap yok, 3 Info notu |
| Regressions introduced | 0 |
| Bugs escaped to production | 0 (not deployed) |
