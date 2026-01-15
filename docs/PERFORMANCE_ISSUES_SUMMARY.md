# Performance Issues Summary
**Quick Reference Guide**

## Critical Issues (Fix Immediately)

### 1. Missing Database Indexes 🔥
**Impact:** Every report does full table scans
**Location:** Database schema
**Fix:** 5 minutes
```sql
CREATE INDEX idx_daily_logs_student ON Daily_Logs(student_name);
CREATE INDEX idx_daily_logs_date ON Daily_Logs(log_date);
CREATE INDEX idx_reader_cumulative_student ON Reader_Cumulative(student_name);
CREATE INDEX idx_roster_class ON Roster(class_name);
CREATE INDEX idx_roster_grade ON Roster(grade_level);
```
**Result:** 60-84% faster queries

---

### 2. N+1 Query in Database Comparison 🔥
**Impact:** 3-8 second page load
**Location:** `database.py:3385-4662`
**Problem:** 67 sequential queries instead of 2 batched queries
**Fix:** Refactor to use CTE with UNION ALL
**Result:** 87-95% faster (200-400ms)

---

### 3. Multiple Metadata Queries 🔥
**Impact:** 60ms overhead on every stats update
**Location:** `database.py:1435-1444`
**Problem:** 3 separate queries for data that could be fetched in 1
**Fix:** Combine into single query with subselects
**Result:** 58% faster

---

## High Priority Issues

### 4. No Query Caching
**Impact:** Identical queries re-run on every page load
**Fix:** Add TTL cache (5 min) for report results
**Result:** Cache hits = instant (75-84% faster)

### 5. No Connection Pooling
**Impact:** Database locks with 3+ concurrent users
**Fix:** Add connection timeout + consider pooling
**Result:** 10× better concurrent support

### 6. Large Templates Without Pagination
**Impact:** 1000ms+ rendering for 411 rows
**Fix:** Server-side pagination (50 rows/page)
**Result:** 80-90% faster rendering

### 7. Context Processor Overhead
**Impact:** 10-50ms on every page load
**Location:** `app.py:130-148`
**Fix:** Cache database registry lookups
**Result:** 98-99% faster (cached)

---

## Quick Wins Checklist (1-3 days)

- [ ] **Add database indexes** (5 min, 60% faster)
- [ ] **Add connection timeout** (2 min, prevents hangs)
- [ ] **Cache context processor** (30 min, saves 10-50ms/page)
- [ ] **Batch metadata queries** (20 min, 58% faster stats)
- [ ] **Test improvements** (1 hour, verify results)

**Total Effort:** 2-3 hours
**Total Improvement:** 60-70% faster application

---

## Performance Metrics

### Current (Single User)
- School page: 300-800ms
- Students page: 500-1500ms
- Report workflows: 5-10s
- Database comparison: 3-8s

### After Quick Wins
- School page: 100-250ms (67-75% faster)
- Students page: 150-450ms (70-75% faster)
- Report workflows: 2-4s (60-70% faster)
- Database comparison: Still slow (needs Phase 2)

### After All Fixes
- School page: 50-150ms (83-94% faster)
- Students page: 100-200ms (80-87% faster)
- Report workflows: 500ms-1.5s (75-90% faster)
- Database comparison: 200-400ms (87-95% faster)

---

## Implementation Order

1. **Day 1:** Add indexes + connection timeout
2. **Day 2:** Add caching (context processor + query results)
3. **Day 3-5:** Fix N+1 database comparison query
4. **Day 6-7:** Add pagination to large tables
5. **Day 8-10:** Optimize CSV uploads + workflow parallelization

---

## Testing Commands

```bash
# Before optimization - measure baseline
time python3 -c "
from app import app
with app.test_client() as client:
    client.get('/school')
"

# Check for indexes
python3 -c "
import sqlite3
conn = sqlite3.connect('db/readathon_sample.db')
cursor = conn.cursor()
cursor.execute(\"SELECT sql FROM sqlite_master WHERE type='index'\")
print('Indexes found:', cursor.fetchall())
"

# Profile application
python3 -m cProfile -o profile.stats app.py

# Analyze query plan
python3 -c "
import sqlite3
conn = sqlite3.connect('db/readathon_sample.db')
cursor = conn.cursor()
cursor.execute('EXPLAIN QUERY PLAN SELECT * FROM Daily_Logs dl JOIN Roster r ON dl.student_name = r.student_name')
print(cursor.fetchall())
"
```

---

## Key Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `db/readathon_sample.db` | Add 5 indexes | 🔥 Critical |
| `db/readathon_2025.db` | Add 5 indexes | 🔥 Critical |
| `database.py:413-418` | Add timeout to connection | 🔥 Critical |
| `database.py:1435-1444` | Batch metadata queries | 🔥 Critical |
| `app.py:130-148` | Cache context processor | ⚠️ High |
| `database.py:3385-4662` | Fix N+1 comparison query | ⚠️ High |
| `templates/students.html` | Add pagination | ⚠️ High |

---

## Root Cause Analysis

All performance issues stem from:
1. **No indexes:** Database designed without performance optimization
2. **No caching:** Every request treated as fresh (no memory)
3. **Sequential operations:** No parallelization or batching
4. **Desktop-first design:** Not built for concurrent access

**Fix these 4 root causes → 70-90% performance improvement**

---

See `docs/PERFORMANCE_ANALYSIS.md` for detailed analysis (962 lines).
