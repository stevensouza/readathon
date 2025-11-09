# Documentation Updates Needed

**Created:** 2025-11-09
**Status:** In Progress
**Priority:** High

This document tracks all documentation inconsistencies discovered during review of help pages. Use this as a checklist for future documentation improvement sessions.

---

## 🔴 Critical Issues (Must Fix)

### 1. School Page Banner Section (help.html lines 90-167)
**Current State:** Describes 5 separate colored boxes (Green, Blue, Orange, Purple, Red)
**Actual State:** Single dark blue banner with 6 metrics in a horizontal row

**Actual Banner Metrics (school.html lines 441-473):**
1. 📅 Campaign Day - Current day of total days + date
2. 💰 Fundraising - Total $ + student count + percentage
3. 📚 Minutes Read - Hours + minutes (with 120/day cap) + ◐ icon when filtered
4. 🎁 Sponsors - Count + student count + percentage
5. 👥 Avg. Participation (With Color) - Percentage + student count + ◐ icon when filtered
6. 🎯 Goal Met (≥1 Day) - Percentage + student count + ◐ icon when filtered

**Action Required:**
- Replace entire "Dashboard Verification Boxes" section with accurate "School Page Headline Banner" section
- Document the ◐ filter indicator that appears on certain metrics when date-filtered
- Remove references to colored boxes
- Add information about the date filter dropdown

### 2. Reports & Data Section (help.html - section needs review)
**Issues to verify:**
- Report list may be outdated
- Report types and descriptions need verification against current state
- Enhanced metadata features (column descriptions, terms, analysis) should be documented

**Action Required:**
- Review actual Reports & Data page structure (3 accordion sections)
- Update report list to match current 22 reports
- Document metadata features (Column Descriptions, Data Sources, Key Terms, Automated Analysis)
- Document table views and workflows sections

### 3. Admin Section (help.html - section needs review)
**Current State:** May describe old structure
**Actual State:** 5 tabs in Admin page

**Actual Admin Tabs:**
1. **Actions** - Selective table clearing, upload history, database integrity
2. **Data Management** - View tables, export CSV, table statistics
3. **Database Creation** - Create new read-a-thon databases for future years
4. **Database Registry** - Manage all databases across years (switch active, view metadata)
5. **Database Comparison** - Year-over-year analysis with 50 metrics

**Action Required:**
- Update Admin section to accurately describe all 5 tabs
- Document Database Registry functionality (v2026.11.0)
- Document Database Comparison feature (v2026.12.0) with 50 metrics
- Document only ONE database is active at a time

### 4. Workflows Section (help.html - needs verification)
**Current Workflows:**
- **QD: Daily Slide Update** - Runs 5 daily reports (Slides 2-6)
- **QC: Cumulative Workflow** - Runs 6 cumulative reports (Q5, Q6, Q14, Q18, Q19, Q20)

**Action Required:**
- Verify workflow names and report lists match current state
- Document purpose of each workflow
- Add any new workflows that may have been added

---

## 🟡 Medium Priority Issues

### 5. Broken IMPLEMENTATION_PROMPT.md Link (help/requirements page)
**Issue:** Page tries to read `IMPLEMENTATION_PROMPT.md` but file doesn't exist
**Error:** "IMPLEMENTATION_PROMPT.md not found"

**Action Required:**
- Either create the file with comprehensive build instructions OR
- Update the route to read from `md/IMPLEMENTATION_PROMPT.md` if it exists there OR
- Remove this help page if not needed

**Context:** This was intended to be a comprehensive prompt that could be used to rebuild the application from scratch, including:
- All features and tabs (School, Teams, Grade, Students, Upload, Reports, Admin)
- Database schema and queries
- Styling and UI patterns
- Interactive features (sorting, filtering, etc.)
- Testing requirements

### 6. Add Table of Contents to All Help Pages
**Pages needing TOC:**
- `/help` - User Manual (816 lines, very long - TOC essential)
- `/help/installation` - Installation Guide (TOC would be helpful)
- `/help/claude` - Claude Code documentation (needs review and expansion)
- `/help/requirements` - Application requirements (currently has broken link)

**TOC Implementation Options:**
- **Option A:** Sticky sidebar TOC (like modern documentation sites)
- **Option B:** Top-of-page jump links with "Back to Top" buttons
- **Option C:** Bootstrap scrollspy navigation

**Recommended:** Option A (sticky sidebar) for best UX

### 7. Upload Page Documentation
**Action Required:**
- Document the two-file upload process (daily logs + cumulative stats)
- Document CSV format requirements
- Document date selection
- Document upload history/audit trail
- Link to ReadAThon.com for where to get files

---

## 🟢 Low Priority / Enhancements

### 8. Students Page Documentation
**Recently Added:** Students tab with master-detail view
**Documentation Status:** Partially covered in Quick Start

**Action Required:**
- Add dedicated section for Students page
- Document master table with search functionality
- Document detail view (if implemented)
- Document search capabilities (searches all columns)

### 9. Help Page Cross-References
**Enhancement:** Add internal links between help sections

Examples:
- Link from ReadAThon.com section to Upload section
- Link from Reports section to Workflows section
- Link from School Page section to date filtering

### 10. Screenshots/Visual Aids
**Enhancement:** Consider adding screenshots to help pages

**Candidates for screenshots:**
- School page banner showing 6 metrics
- Database Registry interface
- Database Comparison side-by-side view
- Report metadata modal (Analysis button)
- Workflow execution results

---

## 📋 Implementation Checklist

### Phase 1: Critical Fixes (Do First)
- [ ] Fix School Page Banner section completely
- [ ] Fix broken IMPLEMENTATION_PROMPT.md link
- [ ] Add basic TOC to help.html

### Phase 2: Major Updates
- [ ] Update Reports & Data section
- [ ] Update Admin section (5 tabs)
- [ ] Update Workflows section
- [ ] Review and expand Claude Code development page

### Phase 3: Polish
- [ ] Add Students page section
- [ ] Add Upload page section
- [ ] Add cross-references
- [ ] Consider adding screenshots

---

## 🔍 Verification Commands

**Check current School page banner:**
```bash
curl -s http://127.0.0.1:5001 | grep -A 50 "headline-banner"
```

**Check Reports page:**
```bash
curl -s http://127.0.0.1:5001/reports | grep -A 100 "Reports Section"
```

**Check Admin page tabs:**
```bash
curl -s http://127.0.0.1:5001/admin | grep -A 10 "nav-tabs"
```

**Check Workflows:**
```bash
curl -s http://127.0.0.1:5001/workflows | grep -A 50 "QD:\|QC:"
```

---

## 📝 Notes for Next Session

### Search Enhancement (COMPLETED in previous session)
- ✅ Enhanced Students page search to search ALL columns (text and numeric)
- ✅ Added 20 comprehensive search tests to test_students_page.py
- ✅ All 398 tests passing (393 passed, 5 skipped)
- ✅ Updated pre-commit hook with per-module test reporting

### Installation & ReadAThon.com Integration (COMPLETED this session)
- ✅ Created idempotent install.sh (380+ lines)
- ✅ Added 4th help menu item: Installation Guide
- ✅ Created comprehensive templates/installation.html
- ✅ Added ReadAThon.com data dependency notices in 5+ places
- ✅ Added GitHub repository links throughout docs
- ✅ Updated README.md with badges and notices
- ✅ Expanded Feature 02 documentation (23 → 245 lines)

### Current Session Context Loss Prevention
This file was created to prevent context loss during conversation compaction. All documentation issues discovered during review are captured here for future sessions.

---

## 🎯 Quick Start for Next Documentation Session

1. Start Flask app: `python3 app.py --db sample`
2. Open help pages in browser:
   - http://127.0.0.1:5001/help
   - http://127.0.0.1:5001/help/installation
   - http://127.0.0.1:5001/help/claude
   - http://127.0.0.1:5001/help/requirements
3. Review this file (DOCUMENTATION_UPDATES_NEEDED.md)
4. Pick issues from Phase 1 checklist
5. Test changes in browser
6. Update this file as issues are resolved

---

**Last Updated:** 2025-11-09
**Next Review:** After major feature additions
