import uuid
from datetime import datetime

# Lưu trữ tạm trong bộ nhớ
payments_db: dict = {}
refunds_db: dict = {}


def new_id(prefix="pay") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
