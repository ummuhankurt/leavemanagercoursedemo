# Backlog — deferred findings

Findings a human triaged as **defer**: real, but fixed later by decision (`workflows/feature-development.md`,
step 7). Nothing lands here without that decision; noise is rejected in the triage record, not parked here.

- A criterion moved out at the ship gate (R-08, `→ moved to B-<n>`) lands here too, by the
  human's ship decision; the entry names the spec and criterion.
- One entry per finding, newest last. Delete the entry in the commit of the work that closes it.
- An entry that grows into new behavior becomes a spec (`specs/active/`), not a fix.

<!-- Format (labels stay English):
- **B-<n>** — <finding, one line> — Source: spec <NNNN>, review round <n> (<file:line>) — Severity: <…>
  — Recommendation: <the reviewer's action> — Deferred by: <name>, <YYYY-MM-DD>, <why>
  A decision deferred at bootstrap (its REPORT) uses Source: bootstrap <YYYY-MM-DD>.
-->

- **B-1** — FastAPI/Starlette framework hataları (404, 405, `RequestValidationError` 422) standart `{"error": {code, message}}` yerine `{"detail": ...}` dönüyor — Source: spec 0001, review round 1 (`src/leave_manager/api/errors.py:36-37`) — Severity: Low
  — Recommendation: girdi alan ilk spec'te `StarletteHTTPException` ve `RequestValidationError` için `error_body` ile handler + test — Deferred by: Ümmühan Kurt, 2026-11-07, girdi alan uç yok; bu işte plan kapsamını genişletir
- **B-2** — `StarletteDeprecationWarning`: TestClient `httpx` yerine `httpx2` istiyor — Source: spec 0001, review round 1 (`pyproject.toml:86`) — Severity: Info
  — Recommendation: `docs/security.md` Dependencies kuralıyla httpx → httpx2 geçişi — Deferred by: Ümmühan Kurt, 2026-11-07, bugün yeşil; bağımlılık değişikliği onaylı bir plan ister
