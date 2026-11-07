# Spec 0003 — Giriş ekranı

- Status: Draft
- Mode: lite
- Plan: `specs/plans/0003-plan.md`
- Self-critique: pending (0002 ships — the screen builds on its final session behavior)

## Intent

Spec 0002 oturumu sunucu tarafında kurar; bu iş kullanıcıya onu ana sayfada kullanılabilir kılar.
Çalışan, yönetici ve İK kullanıcıları tarayıcıda e-posta ve şifreyle giriş yapar, kim olduklarını
ve rollerini görür ve çıkış yapar. Başarı: seed kullanıcılarıyla tarayıcıdan giriş ve çıkış
yapılır, her ekran durumu anlaşılır ve erişilebilirdir. Bilinçli olarak yapılmayanlar: kayıt,
şifre sıfırlama, "beni hatırla" ve role göre farklı ana sayfalar (sonraki spec'ler).

## Requirements

- R-1: Oturum yokken ana sayfa bir giriş formu gösterir; oturum varken karşılama ve çıkış
  seçeneği gösterir.
- R-2: Rol ekranda Türkçe adıyla gösterilir: `Employee` → Çalışan, `Manager` → Yönetici,
  `HR` → İK (0002 self-critique G-2).
- R-3: Sistem durumu bölümü her durumda sayfada kalır (spec 0001 davranışı korunur).

## User experience

- Flow: kullanıcı ana sayfayı açar → sayfa oturumu sorgular → oturum yoksa giriş formu görünür →
  kullanıcı e-posta ve şifreyi girip "Giriş yap"a basar → başarılıysa karşılama ve "Çıkış"
  düğmesi görünür → "Çıkış"a basınca form geri gelir.
- States:
  - Oturum kontrol ediliyor: oturum sorgusu dönene kadar ne form ne karşılama görünür.
  - Giriş yapılmamış (boş form): "E-posta" ve "Şifre" alanları ve "Giriş yap" düğmesi.
  - Eksik alan: boş alanla gönderimde "E-posta ve şifre gerekli" uyarısı; istek gitmez.
  - Gönderiliyor: düğme devre dışı, metni "Giriş yapılıyor…".
  - Hatalı giriş: "E-posta veya şifre hatalı" mesajı; şifre alanı temizlenir, e-posta kalır.
  - Sunucuya ulaşılamıyor / beklenmeyen hata: "Şu anda giriş yapılamıyor, lütfen tekrar deneyin";
    teknik ayrıntı yok.
  - Giriş yapılmış: "Hoş geldin, <ad> (<rol>)" ve "Çıkış" düğmesi; sayfa yenilense de oturum
    sürdüğü sürece bu görünür.
  - Yetkisiz: oturum süresi dolmuşsa sayfa "giriş yapılmamış" durumuna düşer.
- Design reference: none — the flow above is the design. Mevcut `styles.css` kullanılır; yeni
  görsel öğe uydurulmaz.
- Accessibility: alanlar görünür etiketlerle bağlıdır; form klavyeyle (Tab, Enter) baştan sona
  kullanılabilir; uyarı ve hata mesajları ekran okuyucuya duyurulur (canlı bölge); şifre alanı
  maskelidir; kontrast en az WCAG AA (4.5:1).

## Constraints & out of scope

- Sensitive area: Yetkilendirme — ekran yalnızca 0002'nin oturumunu kullanır; frontend'deki
  gizleme/gösterme güvenlik değildir (`docs/security.md`).
- Depends on: spec 0002 shipped.
- Kullanıcı verisi (ad, e-posta) DOM'a yalnızca `textContent` ile yazılır.
- Kanıt yöntemi: ekran durumları VERIFY'da ekran görüntüleriyle (`docs/testing.md`, Evidence for
  UI criteria); JS render testi backlog B-3'e göre yok.
- Split: 0002 Oturum + 0003 (bu spec) — Ümmühan Kurt, 2026-11-07 (0002, G-1).

## Acceptance criteria

- [ ] AC-1 — Oturum yokken ana sayfada etiketli "E-posta" ve "Şifre" alanları ve "Giriş yap"
  düğmesi görünür; sistem durumu bölümü de görünür.
- [ ] AC-2 — Boş alanla gönderimde "E-posta ve şifre gerekli" uyarısı görünür ve sunucuya istek
  gitmez.
- [ ] AC-3 — Gönderim sürerken düğme devre dışıdır ve "Giriş yapılıyor…" yazar.
- [ ] AC-4 — Hatalı girişte "E-posta veya şifre hatalı" mesajı görünür, şifre alanı temizlenir;
  sunucuya ulaşılamazsa "Şu anda giriş yapılamıyor, lütfen tekrar deneyin" görünür; ikisi de
  canlı bölgede duyurulur.
- [ ] AC-5 — Başarılı girişte "Hoş geldin, <ad> (<rol>)" Türkçe rol adıyla ve "Çıkış" düğmesi
  görünür; sayfa yenilendiğinde oturum sürdükçe aynı görünüm gelir.
- [ ] AC-6 — "Çıkış"a basınca form geri gelir; form yalnızca klavyeyle doldurulup gönderilebilir.

## Definition of Done
- [ ] Every acceptance criterion mapped to proof (test or reproducible observation)
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale, deferred ones in `specs/backlog.md`
- [ ] Docs / ADRs updated if behavior or architecture changed
- [ ] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | |
| Fix rounds | |
| Review findings: real / noise / deferred | |
| Regressions introduced | |
| Bugs escaped to production | |
