# Feature 17: Admin Tab 🔧 ENHANCED

**[← Back to Index](../00-INDEX.md)**

---

### Feature 17: Admin Tab 🔧 ENHANCED
**Requirements:**
- Add new top-level navigation item: "Admin"
- Create `/admin` route and page
- Organize into sections with enhanced database management

**Section 1: Database Management (Enhanced)**

**A. Create New Database:**
```html
┌─────────────────────────────────────────────────┐
│ Create New Database                              │
├─────────────────────────────────────────────────┤
│ Database Name: [lincoln_2025_______________]     │
│                (letters, numbers, underscore only)│
│                (system will add 'readathon_' prefix)│
│                                                  │
│ Description: [Lincoln Elementary 2025 Campaign_] │
│              (shown in dropdown selector)        │
│                                                  │
│ Database Type: [School ▼]                       │
│                - Production                      │
│                - Sample                          │
│                - School                          │
│                - Experiment                      │
│                - Archive                         │
│                - Other                           │
│                                                  │
│ Clone from: [readathon_prod_2025 ▼] (optional) │
│             (copies structure, not data)         │
│                                                  │
│ [Create Database]                                │
└─────────────────────────────────────────────────┘

Result:
- Filename: readathon_lincoln_2025.db
- Appears in dropdown under "Schools" group
- Empty tables (if cloned) or base schema
- Metadata stored in Database_Metadata table
```

**B. Manage Existing Databases:**
```html
┌─────────────────────────────────────────────────────────────────────────────┐
│ Existing Databases                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Name                    | Type       | Size   | Records | Modified  | RO    │
├─────────────────────────────────────────────────────────────────────────────┤
│ readathon_prod_2025     | Production | 2.4 MB | 1,245   | 10/14/25  | [ ]   │
│ readathon_prod_2024     | Archive    | 2.1 MB | 1,189   | 10/12/24  | [✓]   │
│ readathon_lincoln_2025  | School     | 1.8 MB | 856     | 10/13/25  | [ ]   │
│ readathon_sample_2025   | Sample     | 500 KB | 500     | 09/01/25  | [ ]   │
│ readathon_exp_test1     | Experiment | 120 KB | 125     | 10/10/25  | [ ]   │
└─────────────────────────────────────────────────────────────────────────────┘

[RO] = Read-Only checkbox
- Check to mark database as read-only (prevents uploads/changes)
- Uncheck to make writable again
- Useful for protecting archived campaigns
```

**C. Current Database Info:**
```html
┌─────────────────────────────────────────────────┐
│ Current Database Information                     │
├─────────────────────────────────────────────────┤
│ Name: readathon_prod_2025                       │
│ Description: 2025 Main Campaign                  │
│ Type: Production                                 │
│ Created: 2025-09-01 10:30:00                    │
│ File Size: 2.4 MB                                │
│ Read-Only: No                                    │
│                                                  │
│ Table Row Counts:                                │
│ - Roster: 411 students                           │
│ - Class_Info: 18 classes                         │
│ - Grade_Rules: 6 grade levels                    │
│ - Daily_Logs: 1,233 entries                      │
│ - Reader_Cumulative: 411 entries                 │
│ - Upload_History: 12 uploads                     │
│                                                  │
│ Last Modified: 2025-10-14 14:45:12              │
└─────────────────────────────────────────────────┘
```

**Section 2: Setup Data Upload**
```
Setup Data Upload
├─ Upload Roster
│  └─ [File: roster.csv] [Upload]
│      Uploads to Roster table (replaces all)
│      Required columns: student_name, class_name, teacher_name, grade_level
├─ Upload Class Info
│  └─ [File: class_info.csv] [Upload]
│      Uploads to Class_Info table (replaces all)
│      Required columns: class_name, teacher_name, grade_level
└─ Upload Grade Rules
   └─ [File: grade_rules.csv] [Upload]
       Uploads to Grade_Rules table (replaces all)
       Required columns: grade_level, min_daily_minutes
```

**Section 3: Data Quality**
```
Data Quality
├─ Data Validation Report
│  └─ [Run Validation] → Shows report inline
│      Checks: Duplicates, missing data, orphaned records, mismatches
└─ Bulk Name Correction
   └─ [Review Names] → Opens correction interface
       Find and fix name variations/typos across tables
```

**Implementation:**

**Create Database Form (HTML):**
```html
<form id="create-db-form" onsubmit="createDatabase(event)">
    <div class="mb-3">
        <label for="db-name" class="form-label">Database Name</label>
        <input type="text" class="form-control" id="db-name"
               pattern="[a-zA-Z0-9_]+"
               title="Only letters, numbers, and underscores allowed"
               required>
        <small class="text-muted">System will prefix with 'readathon_'</small>
    </div>

    <div class="mb-3">
        <label for="db-description" class="form-label">Description</label>
        <input type="text" class="form-control" id="db-description"
               placeholder="E.g., Lincoln Elementary 2025 Campaign"
               required>
    </div>

    <div class="mb-3">
        <label for="db-type" class="form-label">Database Type</label>
        <select class="form-select" id="db-type" required>
            <option value="production">Production</option>
            <option value="sample">Sample</option>
            <option value="school">School</option>
            <option value="experiment">Experiment</option>
            <option value="archive">Archive</option>
            <option value="other">Other</option>
        </select>
    </div>

    <div class="mb-3">
        <label for="clone-from" class="form-label">Clone From (Optional)</label>
        <select class="form-select" id="clone-from">
            <option value="">-- Create Empty --</option>
            {% for db in available_databases %}
            <option value="{{ db.filename }}">{{ db.description }}</option>
            {% endfor %}
        </select>
        <small class="text-muted">Copies structure only, not data</small>
    </div>

    <button type="submit" class="btn btn-primary">Create Database</button>
</form>
```

**Create Database JavaScript:**
```javascript
async function createDatabase(event) {
    event.preventDefault();

    const formData = {
        name: document.getElementById('db-name').value,
        description: document.getElementById('db-description').value,
        type: document.getElementById('db-type').value,
        clone_from: document.getElementById('clone-from').value || null
    };

    try {
        const response = await fetch('/admin/create_database', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            alert(`Database created successfully: ${result.filename}`);
            location.reload();
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Failed to create database: ${error.message}`);
    }
}
```

**Manage Databases Table:**
```html
<table class="table table-striped">
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Size</th>
            <th>Records</th>
            <th>Last Modified</th>
            <th>Read-Only</th>
        </tr>
    </thead>
    <tbody>
        {% for db in all_databases %}
        <tr>
            <td><code>{{ db.filename }}</code></td>
            <td><span class="badge bg-secondary">{{ db.type|capitalize }}</span></td>
            <td>{{ db.size_mb }} MB</td>
            <td>{{ db.total_records }}</td>
            <td>{{ db.modified_date }}</td>
            <td>
                <input type="checkbox"
                       class="form-check-input"
                       {% if db.read_only %}checked{% endif %}
                       onchange="toggleReadOnly('{{ db.filename }}', this.checked)">
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**Toggle Read-Only JavaScript:**
```javascript
async function toggleReadOnly(filename, isReadOnly) {
    try {
        const response = await fetch('/admin/toggle_readonly', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                filename: filename,
                read_only: isReadOnly
            })
        });

        const result = await response.json();

        if (result.success) {
            const status = isReadOnly ? 'read-only' : 'writable';
            alert(`Database ${filename} is now ${status}`);
        } else {
            alert(`Error: ${result.error}`);
            // Revert checkbox if failed
            event.target.checked = !isReadOnly;
        }
    } catch (error) {
        alert(`Failed to update database: ${error.message}`);
        event.target.checked = !isReadOnly;
    }
}
```

**Server Routes:**
```python
@app.route('/admin/create_database', methods=['POST'])
def admin_create_database():
    """Create new database with metadata"""
    data = request.json

    try:
        name = data.get('name')
        description = data.get('description')
        db_type = data.get('type', 'other')
        clone_from = data.get('clone_from')

        # Validate inputs
        if not name or not description:
            return jsonify({'success': False, 'error': 'Name and description required'}), 400

        # Create database
        filename = create_database(name, description, db_type, clone_from)

        return jsonify({
            'success': True,
            'filename': filename,
            'message': f'Database {filename} created successfully'
        })

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/admin/toggle_readonly', methods=['POST'])
def admin_toggle_readonly():
    """Toggle read-only flag for database"""
    data = request.json

    try:
        filename = data.get('filename')
        read_only = data.get('read_only', False)

        if not filename:
            return jsonify({'success': False, 'error': 'Filename required'}), 400

        # Toggle flag
        set_readonly_flag(filename, read_only)

        return jsonify({
            'success': True,
            'message': f'Database {filename} {"locked" if read_only else "unlocked"}'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Database Info Function:**
```python
def get_database_info(db_filename):
    """Get detailed information about database"""
    import os
    from datetime import datetime

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Get file size
    file_size_bytes = os.path.getsize(db_filename)
    file_size_mb = file_size_bytes / (1024 * 1024)

    # Get table counts
    tables = ['Roster', 'Class_Info', 'Grade_Rules', 'Daily_Logs',
              'Reader_Cumulative', 'Upload_History']
    counts = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]

    # Get metadata
    cursor.execute("SELECT key, value FROM Database_Metadata")
    metadata = dict(cursor.fetchall())

    # Get last modified time
    mod_time = os.path.getmtime(db_filename)
    mod_date = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

    conn.close()

    return {
        'filename': db_filename,
        'size_mb': round(file_size_mb, 2),
        'total_records': sum(counts.values()),
        'table_counts': counts,
        'metadata': metadata,
        'modified_date': mod_date
    }
```

**Implementation Priority:** 🟡 MEDIUM
- Foundation for Feature 16 (database system)
- Required for multi-database management
- Enables safe experimentation and archives

**Testing Scenarios:**
- [ ] Create new production database → Appears in selector
- [ ] Create database with description → Shows in dropdown
- [ ] Clone from existing database → Has same schema, no data
- [ ] Toggle read-only → Prevents uploads/deletions
- [ ] View database info → Shows accurate counts
- [ ] Invalid database name → Shows validation error

**Files to Modify:**
- `templates/admin.html` - Create admin UI
- `app.py` - Add admin routes
- `database.py` - Add database management functions

**Security Considerations:**
- Add admin authentication (future enhancement)
- Validate all user inputs
- Prevent deletion of current database
- Confirm before destructive operations
- Log all admin actions

---



---

**[← Back to Index](../00-INDEX.md)**
