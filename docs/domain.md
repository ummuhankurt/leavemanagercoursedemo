# Domain

> İş tarafı, insanlar ve ajanlar arasındaki ortak dil. Bir terim burada yoksa, ajan kendi
> anlamını uydurur — eksik terimi önce buraya ekleyin.

**Ürün:** Kurs demosu olarak geliştirilen küçük, uçtan uca bir izin yönetimi uygulaması.
Çalışanlar izin talep eder, yöneticileri onaylar veya reddeder, sistem kalan izin bakiyesini
izler. Başarı ölçütü: ANEW akışını (spec → plan → build → review → verify) gerçek ama küçük
özelliklerle gösterebilmek. Kapsam dışı: bordro, e-posta bildirimi, resmî tatil takvimi,
yarım gün izin, çoklu şirket.

## Ubiquitous language

| Term | Meaning | Notes / not to be confused with |
|---|---|---|
| Çalışan (`Employee`) | İzin talep eden kişi | Kullanıcı hesabı (`User`) ayrı kavram; her çalışanın bir hesabı vardır |
| Yönetici (`Manager`) | Kendi ekibindeki çalışanların taleplerini onaylayan/reddeden çalışan | İK/Admin değildir |
| İK/Admin (`HR`) | İzin türlerini ve yıllık hakları tanımlar | Talep onaylamaz |
| Ekip (`Team`) | Bir yöneticiye bağlı çalışanlar kümesi | |
| İzin türü (`LeaveType`) | Yıllık, mazeret, hastalık vb.; bakiyeden düşüp düşmediği türe bağlıdır | |
| Yıllık hak (`Entitlement`) | Bir çalışanın bir yıl ve bir izin türü için tanımlı gün sayısı | Bakiye değildir |
| İzin talebi (`LeaveRequest`) | Çalışanın bir izin türü için başlangıç–bitiş tarihli talebi | |
| Talep durumu (`LeaveRequestStatus`) | `Pending` → `Approved` / `Rejected`; ayrıca `Cancelled` (çalışan iptali) | Serbest string değil, enum |
| İzin bakiyesi (`LeaveBalance`) | Çalışanın bir yıl ve bir tür için kalan gün sayısı | Yıllık hak − onaylı günler |
| İş günü | Cumartesi ve pazar hariç gün; resmî tatil ilk sürümde yok | Takvim günü |

## Business rules

- **BR-1:** Bitiş tarihi başlangıç tarihinden önce olamaz.
- **BR-2:** Talep süresi *iş günü* olarak hesaplanır; 0 iş günlük talep geçersizdir.
- **BR-3:** Bakiyeden düşen bir türde talep edilen gün sayısı kalan bakiyeyi aşamaz.
- **BR-4:** Bir çalışanın `Pending` veya `Approved` iki talebi tarih olarak çakışamaz.
- **BR-5:** Bakiye yalnızca talep `Approved` olduğunda düşer; `Approved` bir talep iptal edilirse
  düşen günler bakiyeye iade edilir.
- **BR-6:** Yönetici yalnızca kendi ekibindeki taleplere karar verebilir; kendi talebine karar
  veremez.
- **BR-7:** Yalnızca `Pending` talepler onaylanır/reddedilir; `Rejected` ve `Cancelled` talepler
  değiştirilemez.
- **BR-8:** Çalışan `Pending` talebini veya başlangıç tarihi gelmemiş `Approved` talebini iptal
  edebilir.

## Key domain invariants

- Bakiye hiçbir zaman negatif olamaz.
- Durum geçişleri yalnızca şunlardır: `Pending → Approved`, `Pending → Rejected`,
  `Pending → Cancelled`, `Approved → Cancelled` (BR-8 koşuluyla). Başka geçiş yoktur.

## Sensitive areas

- **Yetkilendirme (onay yetkisi)** — BR-6 ve rol kontrolleri (Employee / Manager / HR): kim hangi
  talebi görebilir ve hangi talebe karar verebilir. Hata = erişim ihlali (kendi iznini onaylama,
  başka ekibin verisine erişim). Bu alana dokunan spec, Constraints bölümünde
  `Sensitive area: Yetkilendirme` yazar.
- Bakiye hesabı ve kişisel veri bilinçli olarak hassas alan **değildir**: bordro bağlantısı yok,
  demo yalnızca sahte veriyle çalışır.
