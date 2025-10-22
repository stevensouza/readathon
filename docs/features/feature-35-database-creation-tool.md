# Feature 35: Database Creation Tool

**[← Back to Index](../00-INDEX.md)**

---

### Feature 35: Database Creation Tool
**Requirement:** Web UI to create new databases instead of manual file copying or command-line scripts.

**Purpose:**
- Create new year's database (e.g., readathon_2026.db)
- Create demo/test databases for training
- Create backup copies with different names
- Initialize databases with sample data or empty tables

**Current Pain Points:**
- Users must manually copy database files
- Risk of forgetting to update year-specific data
- No easy way to create demo database
- Command-line intimidating for non-technical users

---

## Proposed UI Design

### A. Location
**Admin Tab → "Database Management" section → "Create New Database"**

### B. Create Database Interface

```
┌──────────────────────────────────────────────────────────────┐
│ 🗄️ Create New Database                                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ Database Name:                                                │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ readathon_                                       .db      │ │
│ └──────────────────────────────────────────────────────────┘ │
│ Examples: readathon_2026.db, readathon_demo.db               │
│                                                               │
│ Initialize With:                                              │
│ ⚪ Empty database (schema only, no data)                      │
│ ⚪ Copy from existing database                                │
│    └─ Select database: [▼ readathon_prod.db        ]         │
│        Options:                                               │
│        ☐ Copy roster only (no reading/donation data)         │
│        ☐ Copy complete data (full clone)                     │
│ ⚪ Sample data (411 students + demo reading data)             │
│                                                               │
│ Campaign Settings (Optional):                                 │
│ Start Date: [10/10/2026]  End Date: [10/15/2026]             │
│                                                               │
│ [Create Database]  [Cancel]                                   │
└──────────────────────────────────────────────────────────────┘
```

### C. Confirmation Dialog

```
┌──────────────────────────────────────────────────────────────┐
│ Confirm Database Creation                                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ You are about to create:                                      │
│                                                               │
│ 📁 File: readathon_2026.db                                   │
│ 📊 Type: Copy from readathon_prod.db (roster only)           │
│ 👥 Students: 411 (copied from prod)                          │
│ 📅 Campaign: Oct 10-15, 2026                                 │
│                                                               │
│ ⚠️ Note: If a file with this name exists, it will be         │
│    renamed to readathon_2026_backup_TIMESTAMP.db             │
│                                                               │
│ [Confirm & Create]  [Cancel]                                  │
└──────────────────────────────────────────────────────────────┘
```

### D. Success Message

```
┌──────────────────────────────────────────────────────────────┐
│ ✅ Database Created Successfully                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ Database: readathon_2026.db                                  │
│ Students: 411                                                │
│ Classes: 18                                                  │
│ Status: Ready to use                                         │
│                                                               │
│ What's Next?                                                  │
│ • Switch to this database using the environment selector     │
│ • Upload daily reading data                                  │
│ • Upload cumulative fundraising data                         │
│                                                               │
│ [Switch to readathon_2026.db]  [Stay on Current]             │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### A. Backend (database.py)

```python
class DatabaseManager:
    """Manages database creation and cloning"""

    @staticmethod
    def create_database(
        db_name: str,
        init_type: str = 'empty',
        source_db: str = None,
        copy_options: dict = None,
        campaign_dates: dict = None
    ) -> Dict[str, Any]:
        """
        Create a new database

        Args:
            db_name: Name of new database (e.g., 'readathon_2026.db')
            init_type: 'empty', 'clone', or 'sample'
            source_db: Source database path (if init_type='clone')
            copy_options: {'roster_only': bool, 'full_clone': bool}
            campaign_dates: {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}

        Returns:
            dict with success status, counts, messages
        """
        result = {
            'success': True,
            'db_name': db_name,
            'students': 0,
            'classes': 0,
            'messages': []
        }

        try:
            # Validate database name
            if not db_name.endswith('.db'):
                db_name += '.db'

            if not db_name.startswith('readathon_'):
                db_name = 'readathon_' + db_name

            # Check if file exists
            if os.path.exists(db_name):
                # Create backup
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = db_name.replace('.db', f'_backup_{timestamp}.db')
                shutil.copy(db_name, backup_name)
                result['messages'].append(f'Existing file backed up to {backup_name}')

            # Create based on init type
            if init_type == 'empty':
                result = DatabaseManager._create_empty_db(db_name)

            elif init_type == 'clone':
                if not source_db:
                    result['success'] = False
                    result['error'] = 'Source database required for clone'
                    return result

                result = DatabaseManager._clone_db(db_name, source_db, copy_options)

            elif init_type == 'sample':
                result = DatabaseManager._create_sample_db(db_name)

            # Update campaign dates if provided
            if campaign_dates and result['success']:
                DatabaseManager._update_campaign_dates(db_name, campaign_dates)

            return result

        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            return result

    @staticmethod
    def _create_empty_db(db_name: str) -> Dict[str, Any]:
        """Create empty database with schema only"""
        # Create new database connection
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Create all tables (same schema as production)
        cursor.execute('''
            CREATE TABLE Roster (
                student_name TEXT PRIMARY KEY,
                class_name TEXT,
                teacher_name TEXT,
                grade_level TEXT,
                team_name TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE Daily_Logs (
                student_name TEXT,
                log_date TEXT,
                minutes_read INTEGER,
                capped_minutes INTEGER,
                PRIMARY KEY (student_name, log_date),
                FOREIGN KEY (student_name) REFERENCES Roster(student_name)
            )
        ''')

        cursor.execute('''
            CREATE TABLE Reader_Cumulative (
                student_name TEXT PRIMARY KEY,
                total_minutes INTEGER DEFAULT 0,
                donation_amount REAL DEFAULT 0,
                sponsors INTEGER DEFAULT 0,
                FOREIGN KEY (student_name) REFERENCES Roster(student_name)
            )
        ''')

        cursor.execute('''
            CREATE TABLE Class_Info (
                class_name TEXT PRIMARY KEY,
                teacher_name TEXT,
                grade_level TEXT,
                team_name TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE Grade_Rules (
                grade_level TEXT PRIMARY KEY,
                min_daily_minutes INTEGER,
                max_daily_minutes INTEGER DEFAULT 120
            )
        ''')

        cursor.execute('''
            CREATE TABLE Upload_History (
                upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_timestamp TEXT,
                file_name TEXT,
                file_type TEXT,
                rows_affected INTEGER,
                log_date TEXT
            )
        ''')

        # Insert default grade rules
        grade_rules = [
            ('K', 20, 120),
            ('1', 20, 120),
            ('2', 30, 120),
            ('3', 30, 120),
            ('4', 30, 120),
            ('5', 30, 120)
        ]

        cursor.executemany('''
            INSERT INTO Grade_Rules (grade_level, min_daily_minutes, max_daily_minutes)
            VALUES (?, ?, ?)
        ''', grade_rules)

        conn.commit()
        conn.close()

        return {
            'success': True,
            'db_name': db_name,
            'students': 0,
            'classes': 0,
            'messages': [f'Created empty database {db_name} with schema']
        }

    @staticmethod
    def _clone_db(db_name: str, source_db: str, copy_options: dict) -> Dict[str, Any]:
        """Clone database from existing database"""
        roster_only = copy_options.get('roster_only', False)

        # First create empty schema
        result = DatabaseManager._create_empty_db(db_name)

        # Connect to both databases
        source_conn = sqlite3.connect(source_db)
        dest_conn = sqlite3.connect(db_name)

        # Copy roster
        source_conn.row_factory = sqlite3.Row
        source_cursor = source_conn.cursor()
        dest_cursor = dest_conn.cursor()

        # Copy Roster table
        source_cursor.execute('SELECT * FROM Roster')
        roster_rows = source_cursor.fetchall()

        for row in roster_rows:
            dest_cursor.execute('''
                INSERT INTO Roster (student_name, class_name, teacher_name, grade_level, team_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['student_name'], row['class_name'], row['teacher_name'],
                  row['grade_level'], row['team_name']))

        result['students'] = len(roster_rows)

        # Copy Class_Info table
        source_cursor.execute('SELECT * FROM Class_Info')
        class_rows = source_cursor.fetchall()

        for row in class_rows:
            dest_cursor.execute('''
                INSERT INTO Class_Info (class_name, teacher_name, grade_level, team_name)
                VALUES (?, ?, ?, ?)
            ''', (row['class_name'], row['teacher_name'], row['grade_level'], row['team_name']))

        result['classes'] = len(class_rows)

        # If full clone, copy data tables too
        if not roster_only:
            # Copy Daily_Logs
            source_cursor.execute('SELECT * FROM Daily_Logs')
            daily_rows = source_cursor.fetchall()
            for row in daily_rows:
                dest_cursor.execute('''
                    INSERT INTO Daily_Logs (student_name, log_date, minutes_read, capped_minutes)
                    VALUES (?, ?, ?, ?)
                ''', (row['student_name'], row['log_date'], row['minutes_read'], row['capped_minutes']))

            # Copy Reader_Cumulative
            source_cursor.execute('SELECT * FROM Reader_Cumulative')
            cumulative_rows = source_cursor.fetchall()
            for row in cumulative_rows:
                dest_cursor.execute('''
                    INSERT INTO Reader_Cumulative (student_name, total_minutes, donation_amount, sponsors)
                    VALUES (?, ?, ?, ?)
                ''', (row['student_name'], row['total_minutes'], row['donation_amount'], row['sponsors']))

            result['messages'].append(f'Copied complete data from {source_db}')
        else:
            result['messages'].append(f'Copied roster only from {source_db}')

        dest_conn.commit()
        source_conn.close()
        dest_conn.close()

        return result

    @staticmethod
    def _create_sample_db(db_name: str) -> Dict[str, Any]:
        """Create database with sample data"""
        # Use existing init_data.py logic or create sample data
        # For now, just create empty and user can run init_data.py separately
        return DatabaseManager._create_empty_db(db_name)
```

### B. Flask Route (app.py)

```python
@app.route('/api/create_database', methods=['POST'])
def create_database():
    """Create a new database"""
    try:
        db_name = request.form.get('db_name')
        init_type = request.form.get('init_type', 'empty')
        source_db = request.form.get('source_db')
        roster_only = request.form.get('roster_only') == 'true'

        copy_options = {
            'roster_only': roster_only,
            'full_clone': not roster_only
        }

        campaign_dates = None
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if start_date and end_date:
            campaign_dates = {'start': start_date, 'end': end_date}

        result = DatabaseManager.create_database(
            db_name=db_name,
            init_type=init_type,
            source_db=source_db,
            copy_options=copy_options,
            campaign_dates=campaign_dates
        )

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/list_databases', methods=['GET'])
def list_databases():
    """List all available database files"""
    db_files = [f for f in os.listdir('.') if f.endswith('.db') and f.startswith('readathon_')]

    databases = []
    for db_file in db_files:
        # Get basic info about each database
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM Roster')
            student_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM Class_Info')
            class_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM Daily_Logs')
            log_count = cursor.fetchone()[0]

            conn.close()

            databases.append({
                'file': db_file,
                'students': student_count,
                'classes': class_count,
                'log_entries': log_count,
                'size_mb': round(os.path.getsize(db_file) / 1024 / 1024, 2)
            })
        except:
            databases.append({
                'file': db_file,
                'error': 'Could not read database'
            })

    return jsonify({'databases': databases})
```

---

## Database Creation Options

### 1. Empty Database
- Creates schema only (all tables)
- Includes default Grade_Rules
- **Use case:** Starting completely fresh, will import roster manually

### 2. Clone from Existing
**Option A: Roster Only**
- Copies Roster table (student names, classes, teams)
- Copies Class_Info table
- No reading or donation data
- **Use case:** New year with same students/classes

**Option B: Full Clone**
- Complete copy of everything
- **Use case:** Creating backup, demo database, what-if scenarios

### 3. Sample Data
- Pre-populated with 411 sample students
- Demo reading data
- Demo fundraising data
- **Use case:** Testing, training, demonstrations

---

## Additional Features

### A. Database List View (Admin Tab)

```
┌────────────────────────────────────────────────────────────────┐
│ Available Databases                                            │
├──────────────────────┬──────────┬─────────┬────────┬──────────┤
│ Database             │ Students │ Classes │ Logs   │ Size     │
├──────────────────────┼──────────┼─────────┼────────┼──────────┤
│ readathon_prod.db    │ 411      │ 18      │ 2,466  │ 2.4 MB   │
│ readathon_2025.db    │ 405      │ 18      │ 2,430  │ 2.3 MB   │
│ readathon_demo.db    │ 411      │ 18      │ 150    │ 0.8 MB   │
│ readathon_sample.db  │ 50       │ 6       │ 300    │ 0.2 MB   │
└──────────────────────┴──────────┴─────────┴────────┴──────────┘

[Create New Database]
```

### B. Validation
- Database name must start with "readathon_"
- Database name must end with ".db"
- Cannot overwrite current active database
- Warn if database already exists (offer backup)

### C. Post-Creation Actions
- Auto-switch to new database option
- Show success message with next steps
- Offer to run init_data.py for sample data

---

**Status:** NEW
**Priority:** Medium-High
**Type:** Admin Tool
**Effort:** 1-2 sessions

**Dependencies:**
- Feature 16: Multi-Database System (already exists)

**Related Features:**
- Feature 34: Database Comparison Tool (compare created databases)
- Feature 29: Selective Table Clearing (clear data from created databases)

**Testing Scenarios:**
- [ ] Create empty database
- [ ] Clone database (roster only)
- [ ] Clone database (full data)
- [ ] Create with campaign dates
- [ ] Verify backup of existing file
- [ ] Switch to newly created database
- [ ] List all databases with stats

---

**[← Back to Index](../00-INDEX.md)**
