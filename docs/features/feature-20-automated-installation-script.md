# Feature 20: Automated Installation Script

**[← Back to Index](../00-INDEX.md)**

---

### Feature 20: Automated Installation Script
**Requirements:**
- Create `install.sh` script in project root that automates entire setup process
- Script should handle installation on a fresh MacBook Air with no prior setup

**Script Features:**

**A. Automated Software Installation:**
- Check for and install Homebrew if missing
- Check for and install Python 3 if missing
- Check for and install pip3 if missing
- Install Flask and pandas dependencies

**B. Directory Setup:**
- Create application directory structure (`~/my/data/readathon`)
- Verify all required files are present
- Set proper file permissions

**C. Desktop Shortcuts:**
- Create `Start_ReadAThon.command` file on desktop
  - Launches Flask server
  - Auto-opens browser to http://127.0.0.1:5000
  - Shows clear startup messages
- Create `Stop_ReadAThon.command` file on desktop
  - Safely stops the Flask server
  - Kills process on port 5000

**D. Validation and Testing:**
- Verify all components installed correctly
- Check Python, pip, Flask, pandas
- Verify database files present
- Test basic application startup

**E. User-Friendly Output:**
- Color-coded output (green for success, red for errors, yellow for warnings)
- Clear progress indicators for each step
- Helpful error messages with solutions
- Final summary with next steps

**Script Structure:**
```bash
#!/bin/bash
# install.sh - Read-a-Thon System Automated Installer

# Steps:
# 1. Check/Install Homebrew
# 2. Check/Install Python 3
# 3. Check/Install pip3
# 4. Install Python dependencies (Flask, pandas)
# 5. Verify application files
# 6. Create requirements.txt
# 7. Create desktop shortcuts
# 8. Test installation
# 9. Offer to start application
```

**Usage Instructions:**
```bash
# On new MacBook Air, after copying files:
cd ~/my/data/readathon
chmod +x install.sh
./install.sh
```

**Implementation Notes:**
- Script must be idempotent (safe to run multiple times)
- Handle errors gracefully with clear messages
- Provide option to skip steps already completed
- Include rollback capability if installation fails
- Test on clean macOS installation

**Integration with User Manual:**
- Add "Quick Install" section to Feature 1 (Help/User Manual)
- Include screenshots of running the script
- Document what the script does at each step
- Provide troubleshooting guide for script failures
- Show manual installation steps as fallback

---

## UI PROTOTYPE REQUIREMENTS

### Prototype 1: Home Screen Design Options
**File:** `ui_prototype_home_options.html`

**Requirements:**
- Three tabs/sections showing different design philosophies:

  **Option A: Dashboard Cards (Uniform)**
  - All metrics in same-sized cards
  - Clean, consistent grid layout
  - 3-4 columns, multiple rows
  - Uniform font sizes
  - Business/professional look

  **Option B: Information Hierarchy**
  - Keep colored boxes for key metrics (larger)
  - Secondary info in smaller uniform cards
  - Most important data prominent
  - Mix of card sizes (responsive)

  **Option C: Data Density**
  - Compact design
  - Fit maximum info on screen
  - Smaller fonts, tighter spacing
  - Focus on information, less on aesthetics

- Use Bootstrap 5 (same as main app)
- Include sample data
- Demonstrate: Verification boxes, participation metrics, database stats

---

### Prototype 2: Verification Box Improvements
**File:** `ui_prototype_verification_boxes.html`

**Requirements:**
- Show all 5 verification boxes with consistent styling
- Implement:
  - Main numbers: 2rem (white, bold)
  - Labels: 0.9-1rem (light gray)
  - Secondary numbers: 1.5rem (white, bold)
  - Timestamps: 0.7rem (lighter gray)
- Box 2 (Minutes): Show breakdown with consistent fonts
- All boxes same visual weight/prominence
- Use current color gradients

**Test with Sample Data:**
- Box 1: $13,966
- Box 2: Daily_Logs: 15,123 | Reader_Cumulative: 17,283 | Difference: 2,160
- Box 3: Top Raised: Myers Hansen $525 | Top Minutes: Kennedy Henderson 240
- Box 4: Top Raised: Ms. Spencer $1,866 | Top Minutes: Mr. Reynolds 1,651
- Box 5: Data Integrity status

---

### Prototype 3: Participation Metrics Display
**File:** `ui_prototype_participation.html`

**Requirements:**
- Show enhanced participation metrics
- Multiple layout options:

  **Layout A: Expanded Blue Box**
  ```
  ┌─────────────────────────────────────────────┐
  │ Students Participating: 205 of 411 (49.9%) │
  │ ├─ Participated ALL days: 180 (43.8%)      │
  │ ├─ Met goal ≥1 day: 195 (47.4%)            │
  │ └─ Met goal ALL days: 150 (36.5%)          │
  │                                             │
  │ Days of Data: 3                             │
  └─────────────────────────────────────────────┘
  ```

  **Layout B: Side-by-Side Boxes**
  ```
  ┌───────────────────────┬───────────────────────┐
  │ Participation         │ Goal Achievement      │
  │ 205/411 (49.9%)      │ ≥1 day: 195 (47.4%)   │
  │ All days: 180 (43.8%)│ All days: 150 (36.5%) │
  └───────────────────────┴───────────────────────┘
  ```

  **Layout C: Stat Cards Row**
  ```
  ┌────────┬────────┬────────┬────────┐
  │ Total  │ All    │ Goal   │ Goal   │
  │ 49.9%  │ 43.8%  │ 47.4%  │ 36.5%  │
  └────────┴────────┴────────┴────────┘
  ```

- Use Bootstrap styling
- Demonstrate with sample data
- Include icons where appropriate

---

## DATABASE SCHEMA CHANGES

### Upload_History Table
```sql
-- Add columns for error/warning tracking
ALTER TABLE Upload_History ADD COLUMN warnings TEXT;
ALTER TABLE Upload_History ADD COLUMN errors TEXT;
ALTER TABLE Upload_History ADD COLUMN details TEXT;
```

### New Queries/Views
No new tables needed, but consider creating views for:
- Combined student report (Feature 4)
- Enhanced participation metrics (Feature 8)
- Data validation checks (P1.2)

---

## IMPLEMENTATION ORDER

### Phase 1: Core Enhancements (Week 1)
1. Feature 18: Save error/warning messages ✓
2. Feature 19: Improve delete confirmations ✓
3. Feature 9: Add Reader_Cumulative to stats ✓
4. Feature 12: Move export buttons to top ✓
5. Feature 7: Font consistency (using finalized prototype) ✓

### Phase 2: Admin & Database (Week 1-2)
6. Feature 16: Year-based database system ✓
7. Feature 17: Admin tab with all sections ✓
8. Feature 15: Table selection capability ✓

### Phase 3: Reports & UI (Week 2)
9. Feature 4: Combined reader report ✓
10. Feature 8: Enhanced participation metrics (using finalized prototype) ✓
11. Feature 13: Report options improvements ✓
12. Feature 14: Multiple report selection ✓
13. Feature 10: Run all reports ✓
14. Feature 11: Slide column indicators ✓

### Phase 4: Documentation & Uploads (Week 2)
15. Feature 1: Improve help page ✓
16. Feature 2: Add ReadAThon images/links ✓
17. Feature 3: Video tutorial link ✓
18. Feature 6: Requirements document ✓
19. Feature 5: Upload screen redesign ✓
20. Feature 20: Automated installation script ✓

### Phase 5: Priority Features (Week 3)
21. P1.1: Export all data (ZIP) ✓
22. P1.2: Data validation report ✓
23. P2.1: Year-over-year comparison ✓

### Phase 6: Future Features (As time permits)
24. P3.1: Student detail page
25. P3.2: Bulk name correction
26. P4-P5: Email reports, charts, leaderboards, etc.

---

## TESTING CHECKLIST

### Functional Testing
- [ ] All new reports generate correctly
- [ ] Multi-select reports works
- [ ] Table selection works
- [ ] Export all data creates valid ZIP
- [ ] Database cloning works
- [ ] Admin uploads work (Roster, Class_Info, Grade_Rules)
- [ ] Delete confirmations accept case-insensitive input
- [ ] Year-based database switching works
- [ ] Error/warning messages saved correctly
- [ ] Report options display and function correctly

### UI/UX Testing
- [ ] Font sizes consistent across verification boxes
- [ ] Participation metrics display clearly
- [ ] Home screen layout is clean and scannable
- [ ] Export/copy buttons visible at top
- [ ] Upload screen side-by-side layout works
- [ ] Messages appear in shared area (no scrolling)
- [ ] Mobile responsive (test on small screens)

### Data Integrity
- [ ] Combined reader report matches source data
- [ ] Participation calculations correct
- [ ] Year comparison calculations correct
- [ ] Data validation report finds known issues
- [ ] Database clone preserves schema

### Performance
- [ ] Run all reports completes in reasonable time
- [ ] Export all data doesn't timeout
- [ ] Multiple report selection responsive
- [ ] Large datasets don't cause memory issues

---

## NOTES FOR IMPLEMENTATION

### Code Style
- Follow existing patterns in codebase
- Use Bootstrap 5 classes for styling
- Keep database operations in `database.py`
- Keep routes in `app.py`
- Keep templates in `templates/` folder

### Error Handling
- Wrap all database operations in try/except
- Return user-friendly error messages
- Log errors for debugging
- Don't expose internal errors to users

### Security
- Validate all file uploads (type, size)
- Sanitize all user inputs
- Use parameterized SQL queries (already doing this)
- Admin functions should have warnings/confirmations

### Configuration
- Database paths should be configurable
- Year range should be configurable
- Max file sizes should be configurable
- Consider adding `config.py` for settings

---

## FUTURE CONSIDERATIONS

### Scalability
- Consider pagination for large reports
- Consider caching for frequently-run reports
- Consider background jobs for slow operations (ZIP export, etc.)

### Features for Next Year
- Mobile app integration
- Parent portal (read-only access for parents)
- Integration with Google Sheets
- Automated email reports
- Real-time dashboard refresh
- API for external tools

### Maintenance
- Database backup/restore functionality
- Data archival for old years
- Audit log for admin actions
- User management (if multi-user)

---

## QUESTIONS TO RESOLVE DURING IMPLEMENTATION

1. **Slide Column Indicators:** Exact columns for each report (need to be provided)
2. **Home Screen Design:** Final choice after reviewing prototypes
3. **Participation Display:** Final layout after reviewing prototype
4. **Font Sizes:** May need iteration after seeing in practice
5. **Admin Permissions:** Any access control needed?

---

## CONCLUSION

This document provides comprehensive requirements for enhancing the Read-a-Thon system. Implementation should follow the phased approach, starting with core functionality and progressing to advanced features.

**Estimated Total Implementation Time:** 3-4 weeks (full-time)

**Ready to begin implementation after:**
1. UI prototypes reviewed and design finalized
2. Any outstanding questions resolved
3. Current read-a-thon event concluded
4. Backup of current working system created

---

## DEPLOYMENT GUIDE: Setting Up on Another MacBook Air

### Overview
This guide provides step-by-step instructions for deploying the Read-a-Thon system on a new MacBook Air that doesn't have Python or Homebrew installed.

---

### Prerequisites Check
Before starting, check what's already installed:

```bash
# Check for Homebrew
brew --version

# Check for Python
python3 --version

# Check for pip
pip3 --version
```

If any of these commands return "command not found", follow the installation steps below.

---

### Step 1: Install Homebrew (Package Manager)

Homebrew is a package manager for macOS that makes installing software easy.

**Installation:**
1. Open Terminal (Applications → Utilities → Terminal)
2. Run this command:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Follow the prompts (may require admin password)
4. After installation, you may need to add Homebrew to your PATH:
   ```bash
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```
5. Verify installation:
   ```bash
   brew --version
   ```
   Should show version like: `Homebrew 4.x.x`

**Reference:** https://brew.sh/

---

### Step 2: Install Python 3

**Installation via Homebrew:**
```bash
brew install python3
```

**Verify Installation:**
```bash
python3 --version
# Should show: Python 3.11.x or similar

pip3 --version
# Should show: pip 24.x.x or similar
```

**Note:** Python 3 comes bundled with pip3 (Python package installer).

---

### Step 3: Transfer Application Files

**Option A: Using USB Drive**
1. On your Mac, copy entire project folder: `/Users/stevesouza/my/data/readathon`
2. Insert USB drive and copy folder to drive
3. On new Mac, create similar directory structure:
   ```bash
   mkdir -p ~/my/data
   ```
4. Copy folder from USB to `~/my/data/readathon`

**Option B: Using AirDrop**
1. Right-click project folder
2. Share → AirDrop → Select new MacBook Air
3. On new Mac, move folder to `~/my/data/readathon`

**Option C: Using Git (if you use version control)**
```bash
cd ~/my/data
git clone <repository-url> readathon
```

**Files/Folders to Transfer:**
```
readathon/
├── app.py
├── database.py
├── requirements.txt
├── readathon_prod.db
├── readathon_sample.db
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── reports.html
│   ├── workflows.html
│   ├── tables.html
│   ├── help.html
│   └── admin.html (if created)
├── static/ (if exists)
└── prototypes/ (optional)
```

---

### Step 4: Install Python Dependencies

Navigate to project directory and install required packages:

```bash
cd ~/my/data/readathon

# Install all required packages
pip3 install -r requirements.txt
```

**If requirements.txt doesn't exist**, manually install:
```bash
pip3 install flask pandas
```

**Verify Installation:**
```bash
pip3 list
# Should show: Flask, pandas, and their dependencies
```

---

### Step 5: Verify Database Files

Ensure database files are present and have correct permissions:

```bash
cd ~/my/data/readathon

# List database files
ls -lh *.db

# Should see:
# readathon_prod.db
# readathon_sample.db
# (and any year-based databases if implemented)

# Verify database integrity (optional)
sqlite3 readathon_prod.db "SELECT name FROM sqlite_master WHERE type='table';"
# Should list: Roster, Class_Info, Grade_Rules, Daily_Logs, Reader_Cumulative, Upload_History
```

**Fix Permissions (if needed):**
```bash
chmod 644 *.db
```

---

### Step 6: Test Run the Application

**Start the Flask server:**
```bash
cd ~/my/data/readathon
python3 app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

**Access the Application:**
1. Open web browser (Safari, Chrome, Firefox)
2. Navigate to: `http://127.0.0.1:5000`
3. You should see the Read-a-Thon Dashboard

**Test Basic Functionality:**
- [ ] Dashboard loads correctly
- [ ] Environment switcher works (Production ↔ Sample)
- [ ] Navigation menu works
- [ ] Reports page loads
- [ ] Upload page displays
- [ ] Tables page shows data

---

### Step 7: Create Desktop Shortcut (Optional)

**Option A: Create Shell Script**
1. Create a startup script:
   ```bash
   nano ~/Desktop/start_readathon.sh
   ```
2. Add these lines:
   ```bash
   #!/bin/bash
   cd ~/my/data/readathon
   python3 app.py
   ```
3. Save (Ctrl+O, Enter, Ctrl+X)
4. Make executable:
   ```bash
   chmod +x ~/Desktop/start_readathon.sh
   ```
5. Double-click `start_readathon.sh` on desktop to start

**Option B: Create Alias**
Add to `~/.zshrc`:
```bash
alias readathon='cd ~/my/data/readathon && python3 app.py'
```
Then run: `readathon` from any terminal window

---

### Step 8: Stopping the Application

**To stop the server:**
- In Terminal window where server is running, press: **Ctrl+C**

**To fully quit:**
- Close Terminal window (or exit with `exit` command)

---

### Troubleshooting

#### Problem: "python3: command not found"
**Solution:**
```bash
# Reinstall Python
brew install python3

# Check PATH
echo $PATH
# Should include: /opt/homebrew/bin or /usr/local/bin
```

#### Problem: "Module not found: flask" or "Module not found: pandas"
**Solution:**
```bash
# Reinstall dependencies
pip3 install --upgrade flask pandas

# Or use full path
/opt/homebrew/bin/pip3 install flask pandas
```

#### Problem: "Address already in use"
**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill that process
kill -9 <PID>

# Or change port in app.py:
# app.run(debug=True, port=5001)
```

#### Problem: "Permission denied" when accessing database
**Solution:**
```bash
cd ~/my/data/readathon
chmod 644 *.db
chmod 755 .
```

#### Problem: Browser shows "This site can't be reached"
**Solution:**
1. Verify Flask server is running (check Terminal output)
2. Try alternative address: `http://localhost:5000`
3. Try IP address shown in Terminal output: `http://192.168.x.x:5000`
4. Check firewall settings (System Preferences → Security → Firewall)

#### Problem: Database is empty
**Solution:**
- Verify correct database file was transferred
- Check environment selector (Production vs Sample)
- Upload setup data via Admin tab

---

### Configuration Changes for New Machine

**Update File Paths (if needed):**
If your directory structure differs, update paths in `app.py`:

```python
# Example: Change database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'readathon_prod.db')
```

**Configure Port (if needed):**
Change default port in `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```

**Set Debug Mode:**
For production use, disable debug mode:
```python
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1')
```

---

### Network Access (Optional)

**To access from other devices on same network:**

1. Find your Mac's IP address:
   ```bash
   ifconfig | grep "inet "
   # Look for line like: inet 192.168.1.100
   ```

2. Ensure Flask binds to all interfaces (in `app.py`):
   ```python
   app.run(debug=True, host='0.0.0.0')
   ```

3. On other device, navigate to: `http://192.168.1.100:5000`

**Security Note:** Only use this on trusted networks (home/school network, not public WiFi).

---

### Backup and Data Management

**Create Backup:**
```bash
# Backup entire project
cp -r ~/my/data/readathon ~/my/data/readathon_backup_$(date +%Y%m%d)

# Backup just databases
cp readathon_*.db ~/Desktop/db_backup_$(date +%Y%m%d)/
```

**Restore from Backup:**
```bash
# Restore database
cp ~/Desktop/db_backup_20250113/readathon_prod.db ~/my/data/readathon/
```

---

### Quick Reference Commands

```bash
# Start application
cd ~/my/data/readathon && python3 app.py

# Check if running
lsof -i :5000

# View logs (if running in background)
tail -f nohup.out

# Stop application
# Press Ctrl+C in terminal, or:
kill $(lsof -t -i:5000)

# Update dependencies
pip3 install --upgrade -r requirements.txt

# Check database
sqlite3 readathon_prod.db ".tables"
sqlite3 readathon_prod.db "SELECT COUNT(*) FROM Roster;"
```

---

### System Requirements

**Minimum:**
- macOS 11.0 (Big Sur) or later
- 4 GB RAM
- 500 MB free disk space
- Internet connection (for initial setup only)

**Recommended:**
- macOS 13.0 (Ventura) or later
- 8 GB RAM
- 1 GB free disk space

**Tested On:**
- MacBook Air M1/M2 (2020-2024)
- macOS 13.x (Ventura) and 14.x (Sonoma)

---

### Annual Setup Checklist

**Before Each Read-a-Thon:**
- [ ] Update macOS to latest version
- [ ] Update Python: `brew upgrade python3`
- [ ] Update dependencies: `pip3 install --upgrade -r requirements.txt`
- [ ] Create new year database (via Admin tab)
- [ ] Upload Roster, Class_Info, Grade_Rules
- [ ] Test all functionality with sample data
- [ ] Create backup of working system

**After Each Read-a-Thon:**
- [ ] Export all data to ZIP
- [ ] Backup database files
- [ ] Archive reports/exports
- [ ] Review and implement enhancements
- [ ] Update documentation

---

### Getting Help

**Documentation:**
- Flask: https://flask.palletsprojects.com/
- Python: https://docs.python.org/3/
- Pandas: https://pandas.pydata.org/docs/
- SQLite: https://www.sqlite.org/docs.html

**Common Resources:**
- Homebrew: https://brew.sh/
- Terminal basics: https://support.apple.com/guide/terminal/welcome/mac

---

### Security Best Practices

1. **Don't expose to public internet** - Run only on local network
2. **Regular backups** - Before and after each upload
3. **Test on Sample first** - Use sample database to test changes
4. **Verify uploads** - Always check data after uploading
5. **Use delete confirmations** - Don't bypass confirmation prompts
6. **Keep software updated** - Update Python, Flask, and dependencies annually

---

**Deployment Guide Version:** 1.0
**Created:** 2025-01-13
**Tested On:** MacBook Air (M1/M2, 2020-2024), macOS 13.x-14.x

---

---

## NEW FEATURES - SLIDES TAB & DESIGN DECISIONS



---

**[← Back to Index](../00-INDEX.md)**
