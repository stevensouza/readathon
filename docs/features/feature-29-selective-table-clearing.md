# Feature 29: Selective Table Clearing

**[← Back to Index](../00-INDEX.md)**

---

### Feature 29: Selective Table Clearing
**Feature:** Admin page interface for selectively clearing data from Upload_History, Reader_Cumulative, and Daily_Logs tables

**Implementation Date:** 2025-10-15
**Status:** NEW
**Priority:** Medium

---

## Overview

Provides a web-based UI on the Admin page for selectively clearing records from transactional data tables. Users can choose which tables to clear using checkboxes, similar to the multi-file upload interface pattern already established in the application.

---

## Requirements

### A. User Interface Components

**Location:** Admin page (`/admin`)

**New Card Section: "Clear Data Tables"**
- Position: Below "Database Management" card
- Header: Warning style (bg-warning text-dark)
- Icon: 🗑️ trash icon

**Table Selection:**
- Three checkboxes with descriptions:
  - ☐ **Upload_History** - "Clear all upload history records"
  - ☐ **Reader_Cumulative** - "Clear all cumulative fundraising data (donations, sponsors, minutes)"
  - ☐ **Daily_Logs** - "Clear all daily reading minutes data"

**Record Count Display:**
- Show current record count next to each checkbox
- Format: `Upload_History (234 records)`
- Updates on page load

**Selection Controls:**
- Two small buttons: "Select All" and "Deselect All"
- Pattern matches upload.html checkbox interface (lines 43, 293-314)

**Clear Button:**
- Large danger button: "Clear Selected Tables"
- Shows dynamic count when tables selected: "Clear 2 Tables"
- Disabled state when no checkboxes selected
- Red/danger styling (btn-danger)

### B. Confirmation Dialog

**Simple Confirmation:**
- Standard JavaScript `confirm()` dialog - **NO TYPING REQUIRED**
- Multi-line warning message includes:
  - List of tables to be cleared
  - Number of records to be deleted per table
  - Warning that action cannot be undone
- Example:
  ```
  ⚠️ CLEAR DATA TABLES WARNING!

  You are about to permanently delete:
  - Upload_History: 234 records
  - Daily_Logs: 1,200 records

  This action CANNOT be undone!

  Are you sure you want to continue?
  ```

### C. Backend API

**Endpoint:** `/api/clear_tables`
**Method:** DELETE
**Content-Type:** application/json

**Request Body:**
```json
{
  "tables": ["Upload_History", "Reader_Cumulative", "Daily_Logs"]
}
```

**Response (Success):**
```json
{
  "success": true,
  "deleted": {
    "Upload_History": 234,
    "Reader_Cumulative": 150,
    "Daily_Logs": 1200
  },
  "environment": "prod"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid table name: InvalidTable"
}
```

### D. Backend Logic

**Validation:**
- Only allow valid table names: `Upload_History`, `Reader_Cumulative`, `Daily_Logs`
- Return error for invalid table names
- Require at least one table to be specified

**Transaction Safety:**
- Use database transaction (BEGIN...COMMIT/ROLLBACK)
- If any table deletion fails, rollback all changes
- All-or-nothing approach

**Deletion Order:**
- Clear tables in safe order (no foreign key violations)
- Suggested order:
  1. Upload_History (independent)
  2. Reader_Cumulative (independent)
  3. Daily_Logs (independent)

**Audit Logging:**
- Log deletion to console/logs with:
  - Timestamp
  - Tables cleared
  - Record counts deleted
  - Environment (prod/sample)

---

## User Experience Flow

1. **Navigate** to Admin page
2. **View** "Clear Data Tables" section with current record counts
   - Upload_History (234 records)
   - Reader_Cumulative (150 records)
   - Daily_Logs (1,200 records)
3. **Select** tables to clear (e.g., check Upload_History + Daily_Logs)
4. **Click** "Clear 2 Tables" button
5. **Confirm** in dialog:
   ```
   ⚠️ You are about to delete 234 Upload_History records and
   1,200 Daily_Logs records. This cannot be undone. Continue?
   ```
6. **See** success message:
   ```
   ✅ Successfully cleared 2 tables!
   - Upload_History: 234 records deleted
   - Daily_Logs: 1,200 records deleted
   ```
7. **Page refreshes** to show updated record counts (both now show 0)

---

## Technical Implementation

### Files Modified

**1. templates/admin.html**
- Add "Clear Data Tables" card after line 99 (after Database Management card)
- Add JavaScript functions:
  - `loadTableCounts()` - Fetch current record counts
  - `toggleAllTableCheckboxes()` - Select/deselect all
  - `updateClearButton()` - Update button text with count
  - `clearSelectedTables()` - Call API and handle response

**2. app.py**
- Add `/api/clear_tables` DELETE endpoint
- Add `/api/table_counts` GET endpoint (for loading counts)
- Implement table clearing logic with transaction support

**3. database.py (if needed)**
- May add helper method: `clear_tables(table_list)` for reusability
- Returns dict with deletion counts

### JavaScript Pattern (Reuse from upload.html)

```javascript
// Toggle all checkboxes
function toggleAllTableCheckboxes(selectAllCheckbox) {
    const checkboxes = document.querySelectorAll('.table-checkbox');
    checkboxes.forEach(cb => cb.checked = selectAllCheckbox.checked);
    updateClearButton();
}

// Update button state
function updateClearButton() {
    const checked = document.querySelectorAll('.table-checkbox:checked');
    const btn = document.getElementById('clearTablesBtn');
    if (checked.length > 0) {
        btn.disabled = false;
        btn.textContent = `Clear ${checked.length} Table${checked.length > 1 ? 's' : ''}`;
    } else {
        btn.disabled = true;
        btn.textContent = 'Clear Selected Tables';
    }
}
```

---

## Benefits Over clear_all_data.py Script

| Aspect | Script | Web UI |
|--------|--------|--------|
| **Selectivity** | All-or-nothing | Choose specific tables |
| **Access** | Terminal required | Web browser |
| **Visibility** | Text-based | Visual with counts |
| **Confirmation** | Type "reset" | Simple OK/Cancel |
| **Audit** | Console only | Could log to database |
| **User-Friendly** | Technical users | All users |

---

## Safety Considerations

1. **No Roster/Class_Info/Grade_Rules** - These core tables are NOT included in clearing options
2. **Transaction Rollback** - If any table fails to clear, all changes are rolled back
3. **Warning Message** - Clear multi-line confirmation with record counts
4. **Visual Feedback** - Success/error messages after operation
5. **Environment Display** - Shows whether PROD or SAMPLE environment

---

## Future Enhancements (Optional)

- [ ] Add "Clear All Data" checkbox to match clear_all_data.py (all 3 tables at once)
- [ ] Add download/export before clear option
- [ ] Add "Undo" capability with temp backup table
- [ ] Add deletion to audit log table
- [ ] Add role-based access control (admin-only feature)

---

## Testing Scenarios

- [ ] Load page - record counts display correctly
- [ ] Select single table - confirmation shows correct count
- [ ] Select multiple tables - confirmation shows all tables
- [ ] Clear tables - records deleted successfully
- [ ] Page refresh - counts update to show 0
- [ ] Invalid table name - error returned
- [ ] Database error - transaction rolled back
- [ ] Cancel confirmation - no deletion occurs

---

## Related Features

- **Feature 28:** Upload Audit Trail System - Provides audit records that can be cleared
- **Feature 17:** Admin Tab - Location where this feature is implemented
- **clear_all_data.py Script:** Command-line equivalent for full database reset

---

**Document Version:** 1.0
**Created:** 2025-10-15
**Last Updated:** 2025-10-15

---

**[← Back to Index](../00-INDEX.md)**
