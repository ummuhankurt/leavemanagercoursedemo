# Conventions

> Yalnızca gerçek kurallar: her kural ya araçla zorlanır (tercih edilen) ya da review'da kontrol
> edilir.

## Language
<!-- Set at bootstrap (step 0) and mirrored in AGENTS.md. Changing it later is allowed — edit both
     places; existing documents are not translated retroactively. -->
- Chat language (interviews, sessions): Türkçe (`tr`)
- Document language (docs/, specs, plans, ADRs, review and verify reports): Türkçe (`tr`)
- Always English (protocol, not prose): ANEW core files, template headings and field labels,
  `Status:` values (Draft / Approved / In progress / Shipped), `Approved by / on:`, `Source:`.
- Code identifiers, branch names, commit messages: İngilizce (Türkçe karakterli tanımlayıcı yok;
  alan terimlerinin kod karşılıkları `docs/domain.md`'de).
- Agent messages (handoff summaries, refusals, `Next:` lines): chat language; command names, file
  paths and protocol fields verbatim.

## Language & framework versions

- **Python 3.13** — `.python-version` ile sabit; **uv** Python'u, sanal ortamı ve bağımlılıkları
  yönetir (`pyproject.toml` + `uv.lock`, lock commit edilir).
- FastAPI + Uvicorn (Uvicorn yalnızca geliştirme; `check`'e girmez), Pydantic v2,
  SQLAlchemy 2.x (ORM), Alembic, SQLite (Python ile gelir).
- Araçlar: ruff (lint + format), mypy (`--strict`), import-linter, pytest, pip-audit.
- Frontend: düz HTML/CSS/JS, ES modules; **npm ve build adımı yok**.
- Sürümler `uv.lock` ile kilitli; yeni bağımlılık `docs/security.md` "Dependencies"e göre.

## Naming

- Python: PEP 8 — `snake_case` fonksiyon/modül, `PascalCase` sınıf, `UPPER_CASE` sabit (ruff).
- Katman başına kaynak türüne göre dosya: `api/leave_requests.py`, `services/leave_requests.py`,
  `repositories/leave_requests.py`.
- Testler: `tests/unit/test_<konu>.py`, `tests/integration/test_<konu>.py`; test adı davranışı
  söyler: `test_rejects_request_when_balance_insufficient`.
- API yolları: `/api/v1/<kaynak>` — kebab-case, çoğul (`/api/v1/leave-requests`); JSON alanları
  `snake_case`.
- Frontend: dosyalar `kebab-case.js`, değişkenler `camelCase`.

## Error handling

- `services/` iş kuralı ihlalinde yalnızca `core/errors.py` alan hatalarını fırlatır:
  `ValidationError` (422), `NotFoundError` (404), `ForbiddenError` (403), `ConflictError` (409 —
  çakışma, bakiye yetersiz). Servisler `HTTPException` fırlatmaz (F-2).
- `api/`'de **tek exception handler** bunları şu biçime çevirir:
  `{"error": {"code": "INSUFFICIENT_BALANCE", "message": "..."}}`.
- Beklenmeyen hata → 500 + genel mesaj. Stack trace, SQL, iç detay kullanıcıya asla sızmaz;
  yalnızca loglanır.

## Data rules

- İzin günleri saatsiz `date`; zaman damgaları (`created_at`, `decided_at`) UTC, timezone-aware
  `datetime`.
- "Bugün" her zaman `core.Clock`'tan gelir — `date.today()` / `datetime.now()` doğrudan çağrılmaz.
- Gün sayıları `int` (yarım gün kapsam dışı).
- ID'ler tam sayı autoincrement primary key; API'de aynı ID.
- Talep durumu `LeaveRequestStatus` (`StrEnum`: `Pending`, `Approved`, `Rejected`, `Cancelled`);
  serbest string yok.
- Şema değişikliği yalnızca Alembic migration ile.

## Known traps
<!-- "<trap> — <what to do instead> — from <spec/finding>". Builders read this section before
     the first plan step. A trap that tooling can catch moves to "Enforced by tooling". -->
- SQLite foreign key'leri varsayılan olarak kapalı — her bağlantıda `PRAGMA foreign_keys=ON`
  (SQLAlchemy `connect` event'i) — from bootstrap.
- Bakiye kontrolü ve düşme ayrı transaction'larda — onay + bakiye düşme (BR-3, BR-5) tek
  transaction'da; iki eşzamanlı onay bakiyeyi negatife düşüremez — from bootstrap.
- Pydantic v1 kalıpları (`orm_mode`, `.dict()`, `class Config`) — `model_config =
  ConfigDict(from_attributes=True)`, `.model_dump()` — from bootstrap.
- FastAPI/Starlette'in varsayılan `{"detail": ...}` hata gövdesi (404, 405, 422) — `HTTPException`
  ve `RequestValidationError` için de tek handler'a bağla (`error_body`) — from 0001 review L-1.
- Starlette'in `Exception` handler'ı 500 yanıtını `ServerErrorMiddleware`'de, yani her
  `@app.middleware("http")` / `add_middleware` dışında üretir; middleware'in eklediği header'lar 500'de
  yoktur — her yanıtta olması gereken header'ı (güvenlik header'ları) o handler'ın yanıtına da ekle
  — from 0002 review M-1.

## Enforced by tooling
<!-- Wire new rules into `scripts/check` whenever possible — prose is advice, tooling is law. -->
- ruff: PEP 8 adlandırma, import sırası, `DTZ` ailesi (naive `datetime`, `date.today()`,
  `datetime.now()` çağrıları — `core/clock.py` dışında), format (`ruff format --check`).
- mypy `--strict`: tip hataları, eksik annotation.
- import-linter: F-1…F-4 (`docs/architecture.md`).
<!-- Walking skeleton bu araçları ve konfigürasyonlarını pyproject.toml'a ekler; o zamana kadar
     bunlar planlanan zorlamalardır. -->
