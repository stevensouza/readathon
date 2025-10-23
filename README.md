# Read-a-Thon Management System

A complete web-based data analysis and reporting system for managing elementary school read-a-thon events. **Built entirely with [Claude Code](https://claude.ai/code)** - see [how it was built](#-built-with-claude-code) below.

## 📸 Screenshots

![School Dashboard](docs/screenshots/school_tab_sample.png)
*School Overview dashboard showing team competition, top performers, and participation metrics*

## 📤 Data Source

This application processes data from **[Read-A-Thon.com](https://www.read-a-thon.com/)**, the official platform where:
- Parents log their children's daily reading minutes
- Sponsors make donation pledges
- Schools download CSV exports for local analysis

This system imports those CSV files and provides comprehensive reporting and analytics.

## 💡 Why We Built This

While Read-A-Thon.com provides the core platform for tracking reading and donations, it doesn't support all the reporting and rules our school needed:

**What Read-A-Thon.com Doesn't Provide:**
- **Team Competition**: We organize classes into competing teams and need team-based leaderboards
- **Grade-Specific Goals**: Each grade level has different daily reading minimums (K-1: 20min, 2-3: 25min, 4-5: 30min)
- **Daily Reading Caps**: We impose a 2-hour (120 minute) maximum per day for contest fairness
- **Participation Tracking**: We track whether students participated at all each day (read any amount)
- **Random Prize Drawings**: We select random students daily for prizes if they've read that day
- **Detailed Daily Reports**: Their cumulative reports don't include our daily caps or grade-specific goals
- **Team Color Bonus**: We award bonus minutes for team spirit participation

**Our Solution:** Import the raw CSV data from Read-A-Thon.com and apply our school's custom business rules on top of it. This gives us the flexibility to generate exactly the reports and metrics we need while still using their excellent platform for parent data entry and sponsor management.

## 🎯 What This System Tracks

**Entity Relationships:**
- **Students** belong to **Classes**
- **Classes** belong to **Teams**
- **Teams** belong to the **School**
- **Classes** have assigned **Teachers**

**Metrics of Interest:**
- **Reading Minutes** (daily and cumulative, with configurable daily cap)
- **Participation** (did student read each day?)
- **Donations Raised** (total fundraising per student)
- **Number of Sponsors** (sponsor count per student)
- **Team Color Bonus** (bonus minutes for team spirit events)

**Reporting:** Per-day and full-contest views with 20+ pre-configured reports

## ✨ Features

- **Modern Dashboard**: Clean Bootstrap 5 interface with multiple tabs (School, Teams, Classes, Students)
- **Local SQLite Database**: All data stored locally - no server needed
- **Multi-File CSV Upload**: Upload multiple daily files at once with automatic date extraction
- **20+ Pre-configured Reports**: Comprehensive analysis covering all metrics
- **Enhanced Report Metadata**: Column descriptions, data sources, automated analysis
- **Workflow Automation**: Run multiple reports in sequence for daily updates
- **Team Competition Tracking**: Real-time team standings with color bonus support
- **Data Integrity Reports**: Reconciliation reports for validation
- **Upload Audit Trail**: Track every file upload with detailed history
- **Export Capabilities**: Copy to clipboard or download as CSV
- **Multi-Database Support**: Switch between production and sample data

## Quick Start

### 1. Install Dependencies

```bash
# Install Flask (only dependency)
pip3 install -r requirements.txt
```

### 2. Initialize Database

**Option A: Use Sample Data (for testing)**
```bash
# The repo includes a sample database with fake data
# Just run the app - it will use readathon_sample.db automatically
python3 app.py
```

**Option B: Use Your Own Data (for production)**
```bash
# Create three CSV files with your school's roster data:
# - class_info.csv
# - grade_rules.csv
# - roster.csv
# Then run the initialization script:
python3 init_data.py
```

**CSV Format Requirements:**
- `class_info.csv`: `class_name,home_room,teacher_name,grade_level,team_name,total_students`
- `grade_rules.csv`: `grade_level,min_daily_minutes,max_daily_minutes_credit`
- `roster.csv`: `student_name,class_name,home_room,teacher_name,grade_level,team_name`

See the `sample_*.csv` files in the repository for examples.

**Note:** The sample database (`readathon_sample.db`) and sample CSV files are included in the repository for testing. Your CSV files with real student data should NOT be committed to version control for privacy reasons - they are automatically excluded by `.gitignore`.

### 3. Start the Application

```bash
python3 app.py
```

Open your browser to: **http://localhost:5000**

Press `CTRL+C` to stop the server.

## Daily Workflow

1. **Upload Data**
   - Navigate to "Upload Data" page
   - Select the date
   - Upload your minutes CSV file (columns: `Reader Name`, `Minutes`)
   - Upload your donations CSV file (columns: `Reader Name`, `Donations`)
   - Click "Upload Data"

2. **Run Reports**
   - Navigate to "Reports" page
   - Select a report from the list
   - Configure options if needed
   - Click "Run Report"
   - Use "Copy to Clipboard" or "Export CSV" buttons

3. **Run Workflows**
   - Navigate to "Workflows" page
   - Choose "Daily Slide Update" or "Cumulative Workflow"
   - Click to run all reports in sequence

## 📊 Reports & Workflows

The system includes 20+ pre-configured reports covering:
- **Daily metrics** - Day-by-day performance tracking
- **Cumulative stats** - Full contest summaries and leaderboards
- **Team competitions** - Team standings and comparisons
- **Data integrity** - Reconciliation and validation reports
- **Prize drawings** - Random winner selection by grade
- **Export formats** - Denormalized logs for external analysis

### Automated Workflows

Group multiple reports to run in sequence:
- **Daily Slide Update** - Reports for daily announcements and presentations
- **Final Prize Workflow** - All prize-related reports for award ceremonies
- **Data Reconciliation** - Validation reports to verify data accuracy

## 📊 Database Structure

### Core Tables
1. **Roster** - Student roster with grade, teacher, team assignments
2. **Daily_Logs** - Daily reading minutes per student (stores both capped and uncapped values)
3. **Reader_Cumulative** - Cumulative donations and sponsor counts per student
4. **Class_Info** - Teacher assignments and grade levels for each class
5. **Grade_Rules** - Grade-specific reading goals (daily minimums and caps)
6. **Upload_History** - Audit trail for all CSV uploads with timestamps and row counts
7. **Team_Color_Bonus** - Bonus minutes for team spirit participation events

### Entity Relationships
- Students → Classes → Teams → School
- Classes have Teachers
- Students accumulate daily reading minutes and total donations
- Teams compete based on aggregated student performance

### Reading Goals
Configurable by grade level:
- Daily minimum reading minutes (varies by grade)
- Daily maximum credited minutes (typically 120 min/day cap)
- Actual minutes read are stored even if they exceed the cap

## File Structure

```
readathon/
├── app.py                  # Flask web application
├── database.py             # Database and report logic
├── init_data.py            # Initialize database with roster
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── readathon.db           # SQLite database (created on first run)
└── templates/             # HTML templates
    ├── base.html
    ├── index.html
    ├── upload.html
    ├── reports.html
    └── workflows.html
```

## Troubleshooting

### Database Issues
If you need to reset the database:
```bash
rm readathon.db
python3 init_data.py
```

### Port Already in Use
If port 5000 is already in use, edit `app.py` line 197:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Change to 5001 or other port
```

### Upload Warnings
If you see "Student not found in roster" warnings:
- Check that student names match exactly (case-sensitive)
- Verify CSV column names are correct: `Reader Name` and `Minutes` or `Donations`
- Make sure CSV file is properly formatted

## Business Logic

- **Participation:** A student "participated" if they read more than 0 minutes that day
- **Meeting Goal:** A student "met their goal" if they read at least their grade's minimum daily minutes
- **Credited Minutes:** Maximum 120 minutes per day counts toward totals (actual minutes are still tracked)
- **Tie-Breaking:** When multiple entities tie for first place, all tied winners are shown

## Technical Details

- **Framework**: Flask 3.0.0
- **Database**: SQLite 3
- **Frontend**: Bootstrap 5.3.0, Bootstrap Icons
- **No Internet Required**: All assets served from CDN but system works offline after first load

## 🔒 Data Privacy

This application is designed to run locally and keep student data private:

**Included in Repository (Safe to Share):**
- Application code (`app.py`, `database.py`, templates)
- Sample database with fake data (`readathon_sample.db`)
- Documentation and screenshots

**NOT Included (Protected by .gitignore):**
- Production databases (`*.db` except sample)
- Initialization file with real student data (`init_data.py`)
- CSV files with real student information
- Any files containing real student or teacher names

**Important:** Before pushing to public repositories, verify that `.gitignore` is properly configured to exclude all files containing personally identifiable information.

## Support

For issues or questions about this system, check:
1. The troubleshooting section above
2. Error messages in the browser console (F12)
3. Terminal output when running `python3 app.py`

## Contest Duration
- **Typical Contest Period**: 10 days (configurable)
- Minutes read outside the official contest period are tracked but don't count toward the competition
- Contest dates are configurable per school year

## 📋 Versioning

This project uses **School Year Calendar Versioning**: `vYYYY.MINOR.PATCH`

**Current Version:** v2026.1.0 (see [VERSION](VERSION) file)

### Versioning Format
- **YYYY**: School year (e.g., 2026 = 2025-2026 school year)
- **MINOR**: Feature additions and improvements
- **PATCH**: Bug fixes and minor updates

### Examples
- `v2026.1.0` → `v2026.1.1`: Bug fix or small update
- `v2026.1.0` → `v2026.2.0`: New feature or major update
- `v2026.1.0` → `v2027.1.0`: Next school year

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.

---

## 🤖 Built with Claude Code

This entire application was developed using **[Claude Code](https://claude.ai/code)**, Anthropic's AI assistant for software development.

### Development Process

I provided high-level requirements and business logic. Claude Code:
- Recommended the technology stack (Flask, SQLite, Bootstrap)
- Designed the database architecture
- Wrote all Python and HTML code
- Created 23 SQL reports with complex business logic
- Implemented UI/UX with responsive design
- Built data validation and integrity checks

**Total Development**: ~35 features across multiple sessions using collaborative iteration.

### Learn How It Was Built

To see the actual development process, example prompts, and lessons learned:

1. **Run the application** and navigate to **Help → How I Used Claude Code to Develop this Application**
2. Or view the documentation directly: [templates/claude_development.html](templates/claude_development.html)

**Key topics covered:**
- The 3-phase development workflow (ASCII → HTML → Production)
- Real collaborative prompt examples (high-level requirements → Claude suggests solutions)
- Token & cost management tips ($20 vs $100/month plans)
- Common challenges and best practices
- Security concerns with local AI file access

### Why This Matters

This project demonstrates that complex, production-ready applications can be built entirely with AI assistance through:
- **Collaborative iteration** (not detailed instructions)
- **Rapid prototyping** (ASCII mockups before coding)
- **Incremental refinement** (review, adjust, repeat)

The complete 3,723-line specification document is available in the app at **Help → Application Requirements**.

---

Good luck with your read-a-thon! 📚
