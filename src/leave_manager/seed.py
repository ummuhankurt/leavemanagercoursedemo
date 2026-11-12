"""Local demo data: ``uv run python -m leave_manager.seed`` (spec 0002, R-9).

Migrates the database, then creates one demo user per role. The demo password comes from the
environment and is never printed (docs/security.md, Secrets).
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping

from leave_manager.core.config import DATABASE_URL_ENV, DEFAULT_DATABASE_URL
from leave_manager.core.db import Database, migrate
from leave_manager.services.auth import DEMO_USERS, seed_demo_users

DEMO_PASSWORD_ENV = "LEAVE_MANAGER_DEMO_PASSWORD"


def run(environ: Mapping[str, str]) -> int:
    password = environ.get(DEMO_PASSWORD_ENV, "")
    if not password.strip():
        print(
            f"{DEMO_PASSWORD_ENV} ortam değişkeni tanımlı değil; hiçbir kullanıcı oluşturulmadı.",
            file=sys.stderr,
        )
        return 1
    url = environ.get(DATABASE_URL_ENV, DEFAULT_DATABASE_URL)
    migrate(url)
    database = Database(url)
    try:
        created = seed_demo_users(database, password)
    finally:
        database.dispose()
    print(f"{created} yeni demo kullanıcı oluşturuldu.")
    for demo in DEMO_USERS:
        print(f"  {demo.role.value:<8} {demo.email}")
    return 0


if __name__ == "__main__":
    sys.exit(run(os.environ))
