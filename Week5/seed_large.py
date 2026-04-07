"""
Chay 1 lan de tao 1 trieu ban ghi vao books_bench.
    python seed_large.py
"""
import sqlite3
import uuid
import time
import random

DB = "library.db"
TOTAL = 1_000_000
BATCH = 10_000

genres = ["Python", "Java", "JavaScript", "Go", "Rust",
          "C++", "Design", "DevOps", "Security", "AI"]

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS books_bench (
        id    TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        genre TEXT,
        year  INTEGER
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_bench_id ON books_bench(id)")
conn.commit()

existing = cur.execute("SELECT COUNT(*) FROM books_bench").fetchone()[0]
if existing >= TOTAL:
    print(f"Da co {existing:,} ban ghi. Bo qua.")
    conn.close()
    exit()

need = TOTAL - existing
print(f"Tao them {need:,} ban ghi (batch={BATCH:,})...")
start = time.time()

rows = []
done = 0
for i in range(existing + 1, TOTAL + 1):
    rows.append((str(uuid.uuid4()), f"Book Title {i:07d}", random.choice(
        genres), random.randint(1990, 2024)))
    if len(rows) == BATCH:
        cur.executemany(
            "INSERT OR IGNORE INTO books_bench VALUES (?,?,?,?)", rows)
        conn.commit()
        rows.clear()
        done += BATCH
        elapsed = time.time() - start
        pct = done / need * 100
        print(f"  {done:>9,} / {need:,}  ({pct:.1f}%)  {elapsed:.1f}s")

if rows:
    cur.executemany("INSERT OR IGNORE INTO books_bench VALUES (?,?,?,?)", rows)
    conn.commit()

total_time = time.time() - start
final = cur.execute("SELECT COUNT(*) FROM books_bench").fetchone()[0]
conn.close()
print(f"\nXong! Tong: {final:,} ban ghi trong {total_time:.1f}s")
