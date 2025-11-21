---
name: Readathon Database Safety
description: Warn and protect against dangerous database operations on production database in the readathon project
---

# Readathon Database Safety

**TRIGGER:** Before any database modification operation (INSERT, UPDATE, DELETE, DROP, TRUNCATE, or running clear_all_data.py)

## Database Safety Protocol

### 1. Identify Current Database

Check which database is currently active:

```bash
# Check config file
grep -E "(active_db|database)" .readathon_config 2>/dev/null

# Or query registry
sqlite3 db/readathon_registry.db "SELECT filename, display_name FROM Database_Registry WHERE is_active = 1;"
```

### 2. Production Database Warning

**If operating on production database (readathon_2025.db):**

```
⚠️ WARNING: Operating on PRODUCTION database!

Database: readathon_2025.db (2025 Read-a-Thon)
Operation: [describe what's about to happen]
Impact: [estimated number of records affected]
Data: Real student data (411 students)

This operation will modify ACTUAL read-a-thon data.

Confirm operation on PRODUCTION database? (yes/no)
```

**User must explicitly type "yes" to proceed.**

### 3. Destructive Operation Protection

**BLOCK these operations without explicit confirmation:**

- `python3 clear_all_data.py` (wipes all contest data)
- `DELETE FROM` queries (removes records)
- `DROP TABLE` (destroys table structure)
- `TRUNCATE` (empties tables)
- `UPDATE` without WHERE clause (affects all records)

**Require user to:**
1. Confirm they understand the impact
2. Confirm they want to proceed
3. Consider if backup exists

### 4. Sample Database Recommendation

**For development and testing, always suggest:**

```bash
python3 app.py --db sample
```

**Benefits:**
- Safe to experiment with fictitious data
- No risk to real student information
- Easily reset without consequences
- Yellow/amber banner provides visual reminder

### 5. Registry Database Protection

**Extra caution for registry database (readathon_registry.db):**

```
⚠️ REGISTRY DATABASE: This tracks ALL contest databases!

Modifying registry affects:
- Database catalog
- Active database selection
- Summary statistics
- Database availability

Proceed with registry modification? (yes/no)
```

## Architecture Context

From CLAUDE.md:
- **Registry Database:** `db/readathon_registry.db` (central catalog)
- **Production Database:** `db/readathon_2025.db` (real contest data)
- **Sample Database:** `db/readathon_sample.db` (safe for testing)

## Default Behavior

- ✅ READ operations: Allow on any database
- ⚠️ WRITE operations on production: Warn and ask
- ❌ DESTRUCTIVE operations: Block and require explicit confirmation
- ✅ Operations on sample: Allow (safe environment)

## When to Skip Warnings

Skip warnings only if:
- User explicitly said "use production database"
- Operation is clearly intended for production (e.g., "update production contest data")
- User has confirmed in same conversation

Otherwise, ALWAYS warn before production modifications.
