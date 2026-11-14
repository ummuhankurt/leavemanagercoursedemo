# ADR 0001 — PR'lar merge commit ile birleştirilir; merge yalnızca ship commit'inden sonra

- Status: Accepted
- Date: 2026-11-13

## Context

`docs/git.md` "squash-merge" diyordu; uygulamada ilk üç PR'ın üçü de merge commit ile girdi
(#1 `47f2995`, #2 `a089337`, #3 `24d53ec`; 0002 plan A-3). Kural ile pratik ayrıştı.

Bu projede kanıt bir işaretçidir (`docs/testing.md`, Evidence policy): plan'ların `## Build
evidence` ve `## Triage` bölümleri branch commit hash'lerini gösterir (ör. 0002 için `@7320d6e`,
`1891d98`); reviewer fix round'larını `[plan NNNN/fix-k]` commit mesajlarından sayar. Squash bu
commit'leri main'den koparır — branch silinince işaretçiler hiçbir yere varmaz.

Ayrıca PR #2, spec 0002 hâlâ `In progress` iken ve VERIFY yapılmadan main'e merge edildi.
Zararsız kaldı (sonradan kod değişmedi, VERIFY 11/11), ama `workflows/feature-development.md`
adım 10'un sırasını (ship commit'i PR'da, CI onu yargılar, sonra merge) çiğnedi. CI'daki
`doctor --strict` bunu yakalamadı: PR'da ship yoktu, yargılayacak bir şey de yoktu.

Proje tek kişilik bir kurs demosu; CI hem `push` hem `pull_request` ile koşar.

## Decision

PR'lar main'e **merge commit** ile birleştirilir. Bir PR erken (tercihen draft) açılabilir, ama
**yalnızca branch'te ship commit'i varken** (spec `specs/done/`'da, `Status: Shipped`, kriterler
işaretli) **ve CI o commit üzerinde yeşilken** merge edilir.

## Consequences

Kazançlar:
- Build evidence, triage ve fix round hash'leri branch silindikten sonra da main'den erişilir;
  kanıt işaretçileri kalıcıdır.
- `[plan NNNN/n]` ve `[plan NNNN/fix-k]` commit izi main'de kalır; bir spec'in nasıl yapıldığı
  geçmişten okunur.
- Kural mevcut geçmişle tutarlıdır; 0001 ve 0002'deki sapmalar bu kararla kapanır.
- PR erken açılabildiği için review sırasında PR ve CI linki görünür; merge kapısı ship'e bağlıdır.

Bedeller:
- Main geçmişi kalabalıklaşır; spec başına tek satırlık görünüm için `git log --first-parent`
  gerekir.
- Main'e ara commit'ler girer; bunlarda yalnızca `--fast` yeşili garantilidir. `git bisect`
  yaparken `--first-parent` kullanılmalı ya da ara commit'lerin tam yeşil olmadığı bilinmelidir.
- Bir feature'ı geri almak `git revert -m 1 <merge-sha>` ister; squash'taki tek commit revert'ünden
  biraz daha incelikli.
- "Ship'ten önce merge yok" kuralı şimdilik yalnızca disiplinle korunur; mekanik bir engel yok.

## Alternatives considered

- **Squash-merge** (eski kural): spec başına tek, temiz bir main commit'i ve en basit revert.
  Kaybetti, çünkü kanıt işaretçilerini main'den koparır; bunu önlemek için her branch'i sonsuza
  dek saklamak gerekirdi. `docs/testing.md` rule 6'daki tree diff kanıtı her iki yöntemde de
  çalıştığından squash'ın bu açıdan bir üstünlüğü yok.
- **Rebase-merge**: lineer geçmiş ve commit izi korunur. Kaybetti, çünkü hash'leri yeniden
  yazar; build evidence'taki her işaretçi geçersiz olur.
- **PR yalnızca ship commit'inden sonra açılır**: daha basit bir kural. Kaybetti, çünkü sorun
  PR'ın açılması değil merge edilmesiydi; erken PR'ın görünürlüğünü bir şey kazanmadan atar.

## Revisit triggers

- Proje tek kişilikten çıkar, paralel feature branch'ler artar ve `--first-parent` geçmişi
  okumaya yetmez.
- Lineer geçmiş isteyen bir araç ya da branch protection kuralı gelir (ör. semantic-release).
- Kanıtlar commit hash'inden bağımsızlaşır (ör. CI run linkleri tek kaynak olur); squash'ın
  bedeli düşer.
- Ship'ten önce merge bir kez daha olur: kural mekanik olarak zorlanır (doctor kontrolü ya da
  branch protection).
