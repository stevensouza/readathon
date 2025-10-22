# Feature 16: Flexible Multi-Purpose Database System 🗄️ ENHANCED

**[← Back to Index](../00-INDEX.md)**

---

### Feature 16: Flexible Multi-Purpose Database System 🗄️ ENHANCED
**Current:** Two databases: "Production" and "Sample"

**New System:**
- Support multiple databases for different purposes:
  - Year-based production campaigns (2024, 2025, 2026...)
  - Sample/test databases
  - Different schools
  - Experiments and testing
  - Archives (historical, read-only)
  - Any other custom purpose
- Flexible naming with metadata support
- Read-only flag for protecting archived data
- Remember last selected database

**Overview:**
This enhanced system allows users to create and manage multiple databases for any purpose, not just years. Each database has metadata (name, description, type, read-only status) stored within it.

**A. Database Naming Convention:**

**Filename Pattern:** `readathon_{identifier}.db`
- System always adds `readathon_` prefix automatically
- User provides identifier (free-form text: alphanumeric + underscore only)
- Examples:
  - `readathon_prod_2025.db`
  - `readathon_sample_2025.db`
  - `readathon_lincoln_2025.db`
  - `readathon_roosevelt_2025.db`
  - `readathon_experiment_test1.db`
  - `readathon_archive_2024.db`

**B. Database Types (for Organization):**
- **Production** - Main campaigns
- **Sample** - Test data
- **School** - Different schools
- **Experiment** - Testing features
- **Archive** - Historical campaigns
- **Other** - Anything else

**C. Database Metadata Table:**

Each database contains a metadata table with its configuration:

```sql
CREATE TABLE IF NOT EXISTS Database_Metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Example metadata:
INSERT INTO Database_Metadata VALUES ('database_name', 'lincoln_2025');
INSERT INTO Database_Metadata VALUES ('description', 'Lincoln Elementary 2025 Campaign');
INSERT INTO Database_Metadata VALUES ('database_type', 'school');
INSERT INTO Database_Metadata VALUES ('created_date', '2025-01-15');
INSERT INTO Database_Metadata VALUES ('read_only', 'false');
INSERT INTO Database_Metadata VALUES ('created_by', 'Admin');
```

**D. Enhanced Database Discovery:**

```python
# app.py
import os
import glob
import sqlite3

def get_available_databases():
    """Get list of all database files with metadata"""
    db_files = glob.glob('readathon_*.db')
    databases = []

    for f in db_files:
        try:
            # Read metadata from database
            conn = sqlite3.connect(f)
            cursor = conn.cursor()

            # Check if metadata table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='Database_Metadata'
            """)

            if cursor.fetchone():
                # Read metadata
                cursor.execute("SELECT key, value FROM Database_Metadata")
                metadata = dict(cursor.fetchall())
            else:
                # Legacy database without metadata - infer from filename
                db_name = f.replace('readathon_', '').replace('.db', '')
                metadata = {
                    'database_name': db_name,
                    'description': f"Database: {db_name}",
                    'database_type': 'other',
                    'read_only': 'false'
                }

            conn.close()

            databases.append({
                'id': f.replace('.db', ''),
                'filename': f,
                'name': metadata.get('database_name', f),
                'description': metadata.get('description', ''),
                'type': metadata.get('database_type', 'other'),
                'read_only': metadata.get('read_only', 'false') == 'true',
                'created_date': metadata.get('created_date', '')
            })

        except Exception as e:
            print(f"Error reading database {f}: {e}")
            continue

    # Sort: Production first, then by type, then by name
    return sorted(databases, key=lambda x: (
        x['type'] != 'production',  # Production first
        x['type'],
        x['name']
    ))

# Initialize databases dynamically
db_instances = {}
for db in get_available_databases():
    db_instances[db['id']] = ReadathonDB(db['filename'])
```

**E. Enhanced Environment Selector (Grouped):**

```html
<!-- Dropdown with grouped databases -->
<select class="form-select" id="dbSelector" onchange="switchDatabase()">
    {% for type_name, dbs in databases_by_type.items() %}
    <optgroup label="{{ type_name|capitalize }}{% if type_name == 'archive' %} (Read-Only){% endif %}">
        {% for db in dbs %}
        <option value="{{ db.id }}"
                {% if db.id == current_db_id %}selected{% endif %}
                title="{{ db.description }}">
            {{ db.description }}
            {% if db.read_only %}🔒{% endif %}
            ({{ db.filename }})
        </option>
        {% endfor %}
    </optgroup>
    {% endfor %}
</select>
```

**Example Dropdown:**
```
┌─────────────────────────────────────────────────┐
│ Database: [▼]                                    │
├─────────────────────────────────────────────────┤
│ Production                                       │
│   ● 2025 Campaign (readathon_prod_2025)         │
│   ○ 2026 Campaign (readathon_prod_2026)         │
│                                                  │
│ Schools                                          │
│   ○ Lincoln Elementary 2025 (readathon_lincoln_2025)│
│   ○ Roosevelt Elementary 2025 (readathon_roosevelt_2025)│
│                                                  │
│ Sample                                           │
│   ○ 2025 Sample Data (readathon_sample_2025)    │
│                                                  │
│ Experiments                                      │
│   ○ Testing New Features (readathon_exp_test1)  │
│                                                  │
│ Archives (Read-Only)                             │
│   ○ 2024 Campaign 🔒 (readathon_archive_2024)   │
│                                                  │
│ Other                                            │
│   ○ Custom Database (readathon_custom1)         │
└─────────────────────────────────────────────────┘
```

**F. Remember Last Selected Database:**

```python
# Use Flask session to remember selection
from flask import session

@app.route('/api/switch_database', methods=['POST'])
def switch_database():
    db_id = request.json.get('database_id')

    if db_id in db_instances:
        session['current_database'] = db_id
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Database not found'}), 404

# On page load, use remembered database
@app.route('/')
def index():
    current_db_id = session.get('current_database', get_default_database())
    db = db_instances[current_db_id]
    # ... rest of route
```

**Alternative (localStorage):**
```javascript
// JavaScript to remember selection in browser
function switchDatabase() {
    const dbId = document.getElementById('dbSelector').value;

    // Save to localStorage
    localStorage.setItem('selectedDatabase', dbId);

    // Make API call to switch
    fetch('/api/switch_database', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({database_id: dbId})
    }).then(() => location.reload());
}

// On page load, restore selection
document.addEventListener('DOMContentLoaded', function() {
    const savedDb = localStorage.getItem('selectedDatabase');
    if (savedDb) {
        document.getElementById('dbSelector').value = savedDb;
    }
});
```

**G. Read-Only Protection:**

```python
def check_readonly(db_id):
    """Check if database is read-only"""
    db_info = next((db for db in get_available_databases() if db['id'] == db_id), None)
    return db_info and db_info['read_only']

@app.route('/upload_daily', methods=['POST'])
def upload_daily():
    current_db = session.get('current_database')

    if check_readonly(current_db):
        return jsonify({
            'success': False,
            'error': 'Cannot upload to read-only database. Please select a writable database.'
        }), 403

    # Proceed with upload...
```

**H. Database Management Functions:**

```python
def create_database(name, description, db_type='other', clone_from=None):
    """
    Create new database with metadata

    Args:
        name: Database identifier (alphanumeric + underscore)
        description: Human-readable description
        db_type: Type for organization (production, sample, school, experiment, archive, other)
        clone_from: Optional source database to clone structure from
    """
    # Validate name
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        raise ValueError("Database name must contain only letters, numbers, and underscores")

    filename = f"readathon_{name}.db"

    if os.path.exists(filename):
        raise ValueError(f"Database {filename} already exists")

    # Create database
    conn = sqlite3.connect(filename)

    if clone_from:
        # Clone structure from existing database
        source = sqlite3.connect(clone_from)
        for line in source.iterdump():
            if line.startswith('CREATE TABLE') or line.startswith('CREATE INDEX'):
                conn.execute(line)
        source.close()
    else:
        # Create base schema
        create_base_schema(conn)

    # Add metadata table and populate
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Database_Metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    metadata = {
        'database_name': name,
        'description': description,
        'database_type': db_type,
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'read_only': 'false',
        'created_by': 'Admin'
    }

    for key, value in metadata.items():
        conn.execute("INSERT INTO Database_Metadata VALUES (?, ?)", (key, value))

    conn.commit()
    conn.close()

    return filename

def set_readonly_flag(db_filename, read_only=True):
    """Toggle read-only flag for database"""
    conn = sqlite3.connect(db_filename)
    conn.execute("""
        INSERT OR REPLACE INTO Database_Metadata VALUES ('read_only', ?)
    """, ('true' if read_only else 'false',))
    conn.commit()
    conn.close()
```

**Implementation Priority:** 🟡 MEDIUM
- Provides flexibility for multi-school, multi-year, experimental use
- Foundation for year-over-year comparisons
- Enables safe experimentation without affecting production

**Testing Scenarios:**
- [ ] Create production database → Appears in Production group
- [ ] Create school database → Appears in Schools group
- [ ] Create experiment database → Can delete safely
- [ ] Mark database as read-only → Upload/delete operations blocked
- [ ] Switch between databases → Selection remembered
- [ ] Reload page → Last selected database still selected
- [ ] Multiple schools in same year → Can compare side-by-side

**Files to Modify:**
- `database.py` - Add metadata management functions
- `app.py` - Update database discovery, add session management
- `templates/base.html` - Update selector with grouped options
- `templates/admin.html` - Add database creation/management UI

**Database Migration:**
- Existing databases without metadata table continue to work
- System infers basic metadata from filename
- User can update metadata via Admin tab

---



---

**[← Back to Index](../00-INDEX.md)**
