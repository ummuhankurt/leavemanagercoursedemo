# Spec 0001 — Walking skeleton

- Status: Shipped
- Mode: lite
- Plan: `specs/plans/0001-plan.md`
- Self-critique: done

## Intent

Ekip (kursu hazırlayan ve izleyenler), ilk gerçek izin özelliğine başlamadan önce uygulamanın
uçtan uca çalıştığını ve her değişikliğin tek bir doğrulama komutuyla kanıtlanabildiğini görmek
istiyor. Başarı: uygulama yerelde başlatılır, bir tarayıcı sayfası sistemin çalıştığını ve
veritabanına ulaşabildiğini gösterir, ve `scripts/check` hızlı ve tam profilde gerçek adımlarla
yeşil döner. Bilinçli olarak yapılmayanlar: kullanıcı girişi, roller, izin talepleri ve hiçbir
iş kuralı (BR-1…BR-8) — bunlar sonraki spec'lerdir.

## Requirements

- R-1: Sistem, kendi durumunu sorgulamaya izin verir: çalışıp çalışmadığını, uygulama sürümünü ve
  veritabanına erişilebilip erişilemediğini bildirir.
- R-2: Veritabanına erişilemediğinde sistem "çalışmıyor" durumunu bildirir; yanıt projenin
  standart hata biçimindedir ve iç ayrıntı (yol, sorgu, yığın izi) içermez.
- R-3: Uygulamanın ana sayfası, sistem durumunu kullanıcıya gösterir.
- R-4: Doğrulama komutu projenin gerçek kalite kontrollerini çalıştırır: hızlı profilde biçim,
  lint, tip, mimari sınır ve birim testleri; tam profilde ek olarak entegrasyon testleri ve
  bağımlılık güvenlik taraması.
- R-5: Katman sınırları (`docs/architecture.md`, F-1…F-4) araçla zorlanır.

## User experience

- Flow: kullanıcı tarayıcıda uygulamanın ana adresini açar → sayfa durumu otomatik olarak bir kez
  sorgular → sonucu gösterir.
- States:
  - Yükleniyor: durum alınırken "Sistem durumu kontrol ediliyor…" metni.
  - Başarılı: "Sistem çalışıyor", uygulama sürümü ve "Veritabanı: erişilebilir".
  - Hata (sistem çalışmıyor veya sunucuya ulaşılamıyor): "Sistem şu anda kullanılamıyor" metni;
    teknik ayrıntı yok.
  - Boş: yok (gösterilecek liste yok). Yetkisiz: yok (bu sürümde giriş yok).
- Design reference: none — the flow above is the design.
- Accessibility: durum metni ekran okuyucuya duyurulur (canlı bölge); sayfa dili `tr`; metin ile
  arka plan kontrastı en az WCAG AA (4.5:1).

## Constraints & out of scope

- Out of scope: kimlik doğrulama, roller, izin türleri/talepleri/bakiyeleri, güvenlik
  header'ları ve CSRF (ilk giriş spec'iyle gelir), üretim dağıtımı, periyodik yenileme.
- Ortam: bu makinede uv ve Python 3.13 yok — kurulum PLAN'ın Risks bölümünde, doctor'ın profil
  hükmüyle karara bağlanır (R-13).
- Stack ve sürümler `docs/conventions.md`; yeni bağımlılıklar `docs/security.md` "Dependencies"e
  göre planda listelenir.
- Sensitive area: none.
- Durum sorgusu kimlik doğrulamasız (herkese açık) erişilebilir; yanıtında gizli bilgi yoktur.
  Bu iş `docs/security.md` "AuthN / AuthZ" default-deny istisna listesine durum sorgusunu ekler
  (self-critique G-1).
- Sürümün tek kaynağı proje tanımındaki sürümdür; kodda ikinci kez yazılmaz (G-3).
- Kanıt yöntemi (G-4, G-5): AC-3…AC-6 sayfa içeriği entegrasyon testinde, üç durum ayrıca VERIFY'da
  ajanın aldığı ekran görüntüleriyle (API stub'lı, yükleniyor için gecikmeli yanıt; kontrast
  ekran görüntüsünde ölçülür); AC-8 VERIFY'da bir kasıtlı bozmayla (geçici F-1 ihlali → `--fast`
  kırmızı → geri al).
- CI tam profili çalıştırır: `.github/workflows/check.yml` bu işte uv + Python 3.13 kurulumunu alır;
  tam yeşilin kanıtı CI'dır (G-6).
- Split: proposed none; kept as one — Ümmühan Kurt, walking skeleton tanımı gereği tüm katmanları
  kuran tek dilim (G-7).

## Acceptance criteria

- [x] AC-1 — Uygulama ve veritabanı çalışırken durum sorgusu başarılı yanıt döner; yanıt
  "çalışıyor" durumunu, uygulamanın sürümünü (proje tanımındaki sürümle aynı) ve veritabanının
  erişilebilir olduğunu içerir.
- [x] AC-2 — Veritabanına erişilemiyorken durum sorgusu "hizmet kullanılamıyor" yanıtı
  (HTTP 503) döner; gövde standart hata biçimindedir (`code` + `message`) ve yol, SQL veya yığın izi içermez.
- [x] AC-3 — Ana sayfa açıldığında, durum yanıtı gelene kadar yükleniyor metni görünür.
- [x] AC-4 — Durum başarılıysa ana sayfa "Sistem çalışıyor", sürümü ve "Veritabanı: erişilebilir"
  bilgisini gösterir.
- [x] AC-5 — Durum sorgusu hata dönerse veya sunucuya ulaşılamazsa ana sayfa "Sistem şu anda
  kullanılamıyor" mesajını gösterir; teknik ayrıntı göstermez.
- [x] AC-6 — Durum metni bir canlı bölgede yer alır (ekran okuyucuya duyurulur) ve sayfanın dili
  `tr` olarak tanımlıdır.
- [x] AC-7 — `./scripts/check --fast` biçim, lint, tip, mimari ve birim testi adımlarını;
  `./scripts/check` ek olarak entegrasyon testlerini ve bağımlılık taramasını çalıştırır ve ikisi
  de yeşil döner; her test iki profilden tam olarak birinde çalışır.
- [x] AC-8 — Sunum katmanı veri erişim katmanını doğrudan kullanacak şekilde değiştirildiğinde
  (F-1 ihlali) `./scripts/check --fast` kırmızı döner.

## Definition of Done
- [x] Every acceptance criterion mapped to proof (test or reproducible observation)
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale, deferred ones in `specs/backlog.md`
- [x] Docs / ADRs updated if behavior or architecture changed
- [x] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | 0 (self-critique G-1…G-7 folded before approval) |
| Fix rounds | 1 (documents only) |
| Review findings: real / noise / deferred | 1 / 1 / 3 (L-2 / I-2 / L-1→B-1, I-1→B-2, VERIFY F-V1→B-3) |
| Regressions introduced | 0 |
| Bugs escaped to production | 0 (not deployed) |
