import uuid
from datetime import datetime, timezone

payments_db: dict = {}
refunds_db: dict = {}


def new_id(prefix="pay") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def now() -> str:
    # THAY DOI: v2 tra "2026-04-26T16:56:51+00:00" (ISO 8601 day du timezone)
    return datetime.now(timezone.utc).isoformat()
