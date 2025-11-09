# Feature 2: ReadAThon.com Website Links & Data Integration

**[← Back to Index](../00-INDEX.md)**

---

## Overview

This feature documents the integration between this application and the official [ReadAThon.com](https://www.read-a-thon.com/) platform, including data dependencies, links, and potential future enhancements.

---

## Data Dependency

### Critical Context

**This application is completely dependent on data from ReadAThon.com.**

- **ReadAThon.com** is the official platform where:
  - Parents log their children's daily reading minutes
  - Sponsors make donation pledges online
  - Schools manage their read-a-thon campaigns
  - Data is stored and can be exported as CSV files

- **This Application** enhances that data by:
  - Applying school-specific rules (120 min/day cap)
  - Organizing students into competing teams
  - Calculating grade-specific participation metrics
  - Generating custom reports not available on ReadAThon.com
  - Tracking team color bonus days
  - Providing offline analysis capabilities

### Data Flow

```
ReadAThon.com Platform
    ↓ (CSV Export)
Daily Logs CSV + Cumulative Stats CSV
    ↓ (Upload via this app)
Local SQLite Database
    ↓ (Processing with school rules)
Custom Reports & Analytics
```

---

## Implementation Status

### ✅ Completed (v2026.12.0)

1. **Help Documentation (templates/help.html)**
   - Added prominent "About ReadAThon.com Data" section at top
   - Explains data dependency clearly
   - Links to https://www.read-a-thon.com/
   - Lists additional features this app provides
   - Shows how to download data from ReadAThon.com

2. **Installation Guide (templates/installation.html)**
   - New help menu item (4th item)
   - Includes "About ReadAThon.com Data" section
   - Explains data dependency for new users
   - Links to ReadAThon.com with clear instructions

3. **README.md**
   - Added prominent data dependency notice at top
   - Badges showing Python/Flask versions
   - Comprehensive "Data Source" section
   - "Why We Built This" section explaining the relationship

4. **Feature Documentation**
   - This document (feature-02) fully expanded
   - Data flow documented
   - Implementation status tracked

### 📋 Planned Future Enhancements

The following could be added in future versions:

1. **Screenshots & Visual Guides**
   - Annotated screenshots showing where to click on ReadAThon.com
   - Step-by-step visual guide: "How to Download Daily Minutes CSV"
   - Step-by-step visual guide: "How to Download Cumulative Stats CSV"
   - Screenshots would go in `/static/images/readathon_guide/`

2. **Interactive Tutorial**
   - First-time user walkthrough
   - Highlight Upload button after installation
   - Show sample CSV format requirements
   - Guide users through first data import

3. **Upload Page Enhancement**
   - Add "Need Data?" link on Upload page
   - Direct link to ReadAThon.com from upload interface
   - Show last upload timestamp
   - Quick reference: "Where to get CSV files"

4. **Validation Helpers**
   - Pre-upload CSV validation
   - Check for required columns
   - Warn about common formatting issues
   - Suggest ReadAThon.com format if mismatched

---

## ReadAThon.com Links

### Primary URL
- **Official Site:** https://www.read-a-thon.com/
- **Purpose:** Main platform for managing read-a-thon campaigns

### Data Export
Schools can export data from their ReadAThon.com dashboard:
- **Daily Logs:** Reading minutes per student per day
- **Cumulative Stats:** Total donations, sponsor counts, total minutes
- **Format:** CSV files compatible with this application

---

## Technical Implementation

### Where Links Appear

1. **Help Menu → User Manual**
   - Line 18: "About ReadAThon.com Data" section
   - Prominent warning-styled card (yellow header)
   - Multiple links to https://www.read-a-thon.com/

2. **Help Menu → Installation Guide**
   - "About ReadAThon.com Data" section
   - Explains dependency for new users
   - Links in multiple places

3. **README.md**
   - Line 10-13: DATA DEPENDENCY NOTICE (blockquote)
   - Line 20: "Data Source" section
   - Line 32: "Why We Built This" explanation

### Code References

**Templates:**
- `templates/help.html` - Main user manual with ReadAThon.com section
- `templates/installation.html` - Installation guide with data dependency notice

**Documentation:**
- `README.md` - Project readme with prominent notice
- `docs/features/feature-02-add-readathon-website-imageslinks.md` - This document

---

## CSV Format Requirements

### Expected Files from ReadAThon.com

**1. Daily Logs CSV**
Expected columns:
- `student_id` or `student_name`
- `date` (format: YYYY-MM-DD)
- `minutes_read` (integer)

**2. Cumulative Stats CSV**
Expected columns:
- `student_id` or `student_name`
- `total_minutes` (integer)
- `total_donations` (decimal)
- `sponsor_count` (integer)

### Upload Process

1. User downloads CSVs from ReadAThon.com
2. User navigates to Upload tab in application
3. User selects date and CSV files
4. Application imports data into SQLite database
5. Application applies school-specific rules (caps, team scoring)

---

## User Guidance

### For New Users

When setting up the application for the first time:

1. **Install the application** (use `install.sh` or manual setup)
2. **Visit ReadAThon.com** to download your school's data
3. **Import the data** via the Upload tab
4. **Start using** the School, Teams, Grade, and Reports tabs

### For Daily Operations

During the read-a-thon event:

1. **Each morning:** Download updated CSV from ReadAThon.com
2. **Upload via Upload tab:** Select today's date and CSV files
3. **View reports:** Use Reports tab or Workflows for daily updates
4. **Share results:** Export to clipboard or CSV for distribution

---

## Future Screenshots (Planned)

If screenshots are added in the future, they should show:

1. **ReadAThon.com Login Screen**
   - Where to log in
   - Which credentials to use

2. **Dashboard Navigation**
   - Where to find export/download options
   - Which menu items to click

3. **CSV Export Dialog**
   - Which date range to select
   - Which export format to choose
   - Where the download button is located

4. **Sample CSV Format**
   - What the CSV should look like
   - Column headers to expect
   - Example data rows

**Storage Location:** `/static/images/readathon_guide/`
**Naming Convention:** `step-01-login.png`, `step-02-navigate.png`, etc.

---

## Related Features

- **Feature 20:** Automated Installation Script (includes ReadAThon.com notices)
- **Feature 23:** Database Creation (mentions data import from ReadAThon.com)
- **Feature 24:** Export All Data (includes README referencing data source)

---

## Version History

- **v2026.12.0** - Added comprehensive ReadAThon.com links and documentation
- **v2026.2.0** - Initial data source mention in README
- **v2026.1.0** - Original application launch

---

**Status:** ✅ Documentation Complete (screenshots deferred to future enhancement)

**[← Back to Index](../00-INDEX.md)**
