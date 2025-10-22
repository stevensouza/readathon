# File Formats Reference

**[← Back to Index](../00-INDEX.md)**

---

## CSV File Types

### Daily Minutes File

**Purpose:** Upload daily reading minutes for a specific date

**Actual Format (from PledgeReg):**
```csv
ClassID,Teacher,ReaderID,ReaderName,Minutes
3339286,"Mrs. Brown",,,"Reagan Palmer",24
3339287,"Ms. Spencer",2117353619,"Reagan Palmer",24
...
```

**Mandatory Columns:**
- `ReaderName` (or `Reader Name`, `Student Name`, `Name`) - Student's full name
- `Minutes` (or `Minutes Read`) - Reading minutes for the day

**Optional Columns:**
- `ClassID` - PledgeReg class identifier
- `Teacher` - Teacher name
- `ReaderID` - PledgeReg student identifier

**Key Characteristics:**
- ❌ NO `Raised` column
- ❌ NO `Sponsors` column
- ✅ HAS `Minutes` column
- ✅ HAS student name column

---

### Cumulative Stats File

**Purpose:** Upload cumulative fundraising and reading data

**Actual Format (from PledgeReg):**
```csv
"Reader Name",Teacher,Email,Raised,Sponsors,Sessions,PageCreated,Minutes
"John Spencer","Mrs. Snyder","parent@email.com",125.50,5,3,"2025-10-01",180
...
```

**Mandatory Columns:**
- `Reader Name` (or `Student Name`, `Name`) - Student's full name
- `Raised` (or `Donation Amount`, `Donations`) - Total donation amount
- `Sponsors` (or `Sponsor Count`) - Number of sponsors
- `Minutes` (or `Cumulative Minutes`) - Total reading minutes

**Optional Columns:**
- `Teacher` - Teacher name
- `Email` - Parent/guardian email
- `Sessions` - Number of reading sessions (ignored)
- `PageCreated` - PledgeReg signup date (ignored)

**Key Characteristics:**
- ✅ HAS `Raised` column
- ✅ HAS `Sponsors` column
- ✅ HAS `Minutes` column
- ✅ HAS student name column

---

## File Type Detection Logic

**Detection Rules:**

1. **If file has both `Raised` AND `Sponsors` columns** → Cumulative file
2. **If file has `Minutes` but NO `Raised` or `Sponsors`** → Daily file

**Implementation (database.py):**

```python
def _detect_columns(self, csv_headers: List[str]) -> Dict[str, bool]:
    """Detect which columns are present (case-insensitive)"""
    headers_lower = [h.lower().strip() for h in csv_headers]

    return {
        'student_name': any(h in headers_lower for h in ['reader name', 'readername', 'student name', 'student_name', 'name']),
        'minutes': any(h in headers_lower for h in ['minutes', 'minutes read', 'minutes_read', 'cumulative minutes', 'cumulative_minutes']),
        'teacher': any(h in headers_lower for h in ['teacher', 'teacher name', 'teacher_name']),
        'raised': any(h in headers_lower for h in ['raised', 'donation amount', 'donation_amount', 'donations']),
        'sponsors': any(h in headers_lower for h in ['sponsors', 'sponsor count', 'sponsor_count'])
    }
```

**Validation Logic:**

```python
# In cumulative upload (upload_cumulative_stats):
if detected['student_name'] and detected['minutes'] and not detected['raised'] and not detected['sponsors']:
    # This is a DAILY file uploaded to cumulative section
    return error: "This appears to be a daily minutes file..."

# In daily upload (upload_daily_data):
if detected['raised'] and detected['sponsors']:
    # This is a CUMULATIVE file uploaded to daily section
    return error: "This appears to be a cumulative stats file..."
```

---

## Error Messages

### Daily file uploaded to Cumulative section:
```
ERROR: This appears to be a daily minutes file (has Reader Name and Minutes,
but missing Raised and Sponsors columns). Please use the "Daily Minutes Upload"
section instead.
```

### Cumulative file uploaded to Daily section:
```
ERROR: This appears to be a cumulative stats file (contains Raised and Sponsors
columns). Please use the "Cumulative Stats Upload" section instead.
```

---

## Column Name Variations (Case-Insensitive Matching)

### Student Name:
- `Reader Name`
- `ReaderName`
- `Student Name`
- `Student_Name`
- `Name`

### Minutes:
- `Minutes`
- `Minutes Read`
- `Minutes_Read`
- `Cumulative Minutes`
- `Cumulative_Minutes`

### Raised/Donations:
- `Raised`
- `Donation Amount`
- `Donation_Amount`
- `Donations`

### Sponsors:
- `Sponsors`
- `Sponsor Count`
- `Sponsor_Count`

### Teacher:
- `Teacher`
- `Teacher Name`
- `Teacher_Name`

---

**[← Back to Index](../00-INDEX.md)**
