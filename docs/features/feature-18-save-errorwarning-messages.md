# Feature 18: Save Error/Warning Messages

**[← Back to Index](../00-INDEX.md)**

---

### Feature 18: Save Error/Warning Messages
**Current:** Upload_History table stores: upload_id, log_date, upload_timestamp, filename, row_count, total_students_affected, upload_type, status

**Add Columns:**
- `warnings` TEXT - JSON array of warning messages
- `errors` TEXT - JSON array of error messages
- `details` TEXT - Additional details (JSON)

**Schema Change:**
```sql
ALTER TABLE Upload_History ADD COLUMN warnings TEXT;
ALTER TABLE Upload_History ADD COLUMN errors TEXT;
ALTER TABLE Upload_History ADD COLUMN details TEXT;
```

**Update Upload Functions:**
```python
# In database.py upload functions
result = {
    'success': True,
    'warnings': [],
    'errors': []
}

# When saving to Upload_History:
cursor.execute("""
    INSERT INTO Upload_History
    (log_date, upload_timestamp, filename, row_count,
     total_students_affected, upload_type, status, warnings, errors, details)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (log_date, timestamp, filename, row_count, students_affected,
      upload_type, status,
      json.dumps(result['warnings']),
      json.dumps(result['errors']),
      json.dumps({'metadata': 'any additional info'})))
```

**Display in Upload History:**
- Show warnings/errors count in table
- Click to expand full messages
- Add tooltip with first warning/error

---



---

**[← Back to Index](../00-INDEX.md)**
