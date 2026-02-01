## 2024-10-24 — Wasted I/O in Icon Search
**Learning:** Limiting `os.walk` iteration to match the UI display limit significantly reduces I/O overhead. Searching for 100 items when only 20 are displayed resulted in ~64% wasted time in benchmarks.
**Action:** Always ensure data retrieval limits match data presentation limits.
