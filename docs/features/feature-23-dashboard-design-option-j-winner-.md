# Feature 23: Dashboard Design - Option J Winner 🏆

**[← Back to Index](../00-INDEX.md)**

---

## Overview

**Decision:** Option J: Refined Zen is the selected design for the Dashboard.

**Status:** ✅ Complete - School Tab Production Deployed

**Last Updated:** 2025-10-18

**Design Model Status:** 🎯 School tab is the **reference implementation** for all future dashboard tabs (Teams, Classes, Students)

---

## Design Standards (Application-Wide)

### Color Scheme
- **Navy:** `#1e3a5f` (primary - navigation active states, headlines, card borders)
- **Teal:** `#17a2b8` (accent - headline values, emphasis)
- **Gold:** `#f59e0b` (Team Kitsko branding)
- **Coral:** `#ff6b6b` (data integrity alerts, errors)
- **Blue background:** `#e3f2fd` (Team Staub cards, leader cards)
- **Yellow background:** `#fffbeb` (Team Kitsko cards)

### Typography
- **Headers:** 1-1.1rem, bold (700-900 weight)
- **Main numbers:** 1.5-2rem, bold (900 weight)
- **Labels:** 0.65-0.75rem, uppercase, letter-spacing: 0.5-0.8px
- **Body text:** 0.85-0.9rem, regular weight

### Terminology Standards
**Money:**
- ✅ **USE:** "Fundraising" (all contexts)
- ❌ **AVOID:** "Donations", "Total Raised" (except in specific narrative contexts)
- **Examples:** "Total Fundraising", "Fundraising Leader", "Top Fundraisers"

**People:**
- ✅ **USE:** "Students" (default, 90% of cases)
- ✅ **USE:** "Readers" (only for reading-specific performance contexts)
- ❌ **AVOID:** Mixing them randomly
- **Examples:** "230 Students participating", "Top Readers by minutes"

**Formatting:**
- **Student counts:** "X of Y Students (Z%)" - e.g., "230 of 411 Students (56%)"
- **Time metrics:** "N hours (M min)" - e.g., "385 hours (23,094 min)"
- **Ties:** Comma-delimited names + "X-way tie for 1st place" note

---

## Navigation Structure

### Top-Level Navigation (Option C: Flat Dashboards + Grouped Utilities)

```
🏫 School | ⚔️ Teams | 🎓 Classes | 👤 Students | 📤 Upload | 📊 Reports & Data ▾ | ❓ Help | ⚙️ Admin
```

**Primary Views (Top-level, one-click access):**
1. 🏫 **School** - Whole-school overview and totals
2. ⚔️ **Teams** - Staub vs Kitsko competition
3. 🎓 **Classes** - Class-level performance
4. 👤 **Students** - Individual student metrics
5. 📤 **Upload** - CSV data import (daily workflow)

**Grouped Under "Reports & Data" Dropdown:**
- 📊 Reports (Q1-Q23 query reports)
- 🔄 Workflows (guided multi-step processes)
- 📋 Tables (raw database data viewer)

**Utilities (Top-level):**
- ❓ Help
- ⚙️ Admin

**Rationale:** Dashboard entity views are prominent and immediately accessible. Technical/advanced features grouped to reduce clutter. Upload stays top-level as critical daily workflow.

---

## School Tab Specification

### 1. Page Header
- **Title:** "🏫 SCHOOL OVERVIEW"
- **Right side:** "📊 Data Info" button (opens metadata modal)
- **Layout:** Flex row, space-between alignment

### 2. Five-Metric Headline Banner

**Metrics (left to right):**

| Position | Metric | Top Value | Bottom Subtitle |
|----------|--------|-----------|-----------------|
| 1 | 📅 Campaign Day | "3 of 6" | "Oct 10-15" |
| 2 | 💰 Fundraising | "$15,236" | "230 of 411<br>Students (56%)" |
| 3 | 📚 Minutes Read | "385 hours" | "(23,094 min)" |
| 4 | 👥 Participation | "56%" | "230 of 411<br>Students" |
| 5 | 🎯 Goals Met | "37%" | "150 of 411<br>Students" |

**Styling:**
- Background: Navy (#1e3a5f)
- Top value: Teal (#17a2b8), 1.8rem, bold
- Labels/subtitles: White with 70% opacity, 0.7rem
- Vertical separators: White with 20% opacity

### 3. Date Filter Section

**Components:**
- Label: "📅 Filter Period:"
- Dropdown: Full Contest (default) + 6 individual days (Oct 10-15)
- Note: "(auto-updates data)" in italic, gray text

**Behavior:**
- **No "Apply" button** - dropdown change immediately triggers page refresh/update
- All metrics, cards, and data update to reflect selected period
- Top Performers show leaders for that specific day (if day selected) or overall contest (if Full Contest selected)

### 4. Three-Column Content Grid

#### Left Column: Team Competition

**Content:**
- **Team Staub card** (blue background #e3f2fd)
  - Classes count
  - Fundraising total
  - Reading: "N hrs (M min)" format
  - Student count
- **VS divider**
- **Team Kitsko card** (yellow background #fffbeb)
  - Same metrics as Staub
- **Lead summary box**
  - Shows which team is ahead and by how much
  - Displays both fundraising and reading gaps

**Styling:**
- Card title: "⚔️ TEAM COMPETITION"
- Border-top: 4px solid Navy
- Team cards: 4px left border (Staub: navy, Kitsko: gold)

#### Center Column: Top Performers

**Content (4 sections):**

1. **💰 Fundraising Leader**
   - Shows #1 leader only (not Top 3)
   - Name(s) - comma-delimited if tie
   - Grade level or "Various grades" if tie
   - Dollar amount
   - If tie: "* X-way tie for 1st place" note

2. **📚 Reading Leader**
   - Same format as Fundraising Leader
   - Shows minutes

3. **🎓 Top Class (Fundraising)**
   - Teacher name + "Class"
   - Grade level
   - Dollar amount

4. **🎓 Top Class (Reading)**
   - Same format as Top Class Fundraising
   - Shows minutes

**Tie Handling:**
- **2-3 names:** Show all comma-delimited
- **4+ names:** Show first 3 + "and X others"
- Always include "* X-way tie for 1st place" note
- Grade becomes "Various grades" if tied students from different grades

#### Right Column: Student Participation

**Content (table format):**
- Total Participating: "X of Y (Z%)"
- All 6 Days Active: "X of Y (Z%)"
- Met Goal ≥1 Day: "X of Y (Z%)"
- Met Goal All Days: "X of Y (Z%)"
- *(separator line)*
- Total Roster: "X Students (100%)"

**Styling:**
- Labels: Gray (#7f8c8d), left-aligned
- Values: Bold black, right-aligned
- Percentages: Light gray, smaller font
- Bottom row: Border-top separator

### 5. Data Integrity Alert

**Placement:** Below the 3-column grid

**Display:** Conditional - only shows if validation errors exist

**Content:**
- ⚠️ icon
- Title: "Data Integrity Issues Detected"
- Subtitle: "X validation errors found - immediate attention required"
- Button: "Review Issues" (red background #ff6b6b)

**Styling:**
- White background, red left border (6px)
- Flex layout: content left, button right
- Box shadow for elevation

### 6. Data Source Metadata

**Implementation:** Hybrid approach (two access points to same modal)

**Access Point 1: Button in Header**
- Button label: "📊 Data Info"
- Location: Top-right of page header
- Opens metadata modal on click

**Access Point 2: Collapsible Footer**
- Title: "Data Sources & Last Updated"
- Default state: Collapsed (▶ icon)
- Expands to show same content as modal inline
- Location: Bottom of page

**Modal/Footer Content:**
```
• Reading minutes, Participation:
  Daily_Logs table (Updated: MM/DD/YYYY HH:MM AM/PM)

• Fundraising, Sponsors:
  Reader_Cumulative table (Updated: MM/DD/YYYY HH:MM AM/PM)

• Student counts:
  Roster table (Updated: MM/DD/YYYY HH:MM AM/PM)
```

**Rationale:** Two entry points maximize discoverability. Button for explicit action, footer for persistent reminder.

---

## Prototype Files

### Current (Original)
- **File:** `/Users/stevesouza/my/data/readathon/prototypes/ui_prototype_home_options.html`
- **Section:** Option J (Lines 2631-2868 approx)
- **Status:** Reference only - original design winner

### New (v2 - School Tab Redesign)
- **File:** `/Users/stevesouza/my/data/readathon/v2026_development/prototypes/dashboard_school_tab_v2.html`
- **Status:** Active HTML prototype for School tab
- **Created:** 2025-10-18
- **Features:**
  - New navigation structure
  - 5-metric headline banner
  - Auto-updating date filter
  - 3-column layout (Team | Performers | Participation)
  - Hybrid metadata access (button + footer)
  - Fully functional dropdowns and modals
  - Option J color scheme

---

## Implementation Workflow

### Prototype Development Process (Approved by User)

1. **ASCII Prototype** - Fast iteration on structure, layout, content
   - Use for initial design discussions
   - Quick to modify and review
   - Focus on information architecture

2. **HTML Prototype** - Visual refinement of approved ASCII design
   - Implement actual colors, spacing, typography
   - Test interactions (dropdowns, modals, filters)
   - User reviews in browser

3. **Production Code** - Deploy approved HTML prototype
   - Update Flask templates (base.html, index.html or new school.html)
   - Implement API routes (app.py)
   - Create database queries (database.py)

**Flexibility:** Can return to ASCII for concept changes, stay in HTML for styling tweaks.

---

## School Tab as Design Model 🎯

**Status:** School tab is now the **reference implementation** for all future dashboard tabs.

**Use School tab as model for:**
1. ⚔️ **Teams Tab** - Competition view with team breakdowns
2. 🎓 **Classes Tab** - Class-level performance metrics
3. 👤 **Students Tab** - Individual student data

**Design Patterns to Replicate:**
- **Headline Banner:** 5-metric summary with navy background, teal values
- **Date Filtering:** Auto-updating dropdown (no Apply button)
- **Visual Indicators:** ◐ icons with tooltips for date-filtered cumulative metrics
- **Three-Column Layout:** Cards with navy top borders, consistent spacing
- **Typography:** Same font sizes, weights, and letter-spacing
- **Color Scheme:** Navy/Teal/Gold/Coral as defined in Option J
- **Responsive Design:** Bootstrap grid system with proper mobile breakpoints

**Reference Files:**
- **Production Template:** `templates/school.html`
- **Production Routes:** `app.py` (school_tab() function)
- **Filter Indicator Prototype:** `prototypes/school_tab_filter_indicators.html`

---

## Future Enhancements

### Priority Enhancements for School Tab
1. **Database-Driven Team Names** 🔧
   - **Issue:** Team names "Staub" and "Kitsko" are currently hardcoded in templates and queries
   - **Solution:** Create `Teams` or `Config` table to store team names dynamically
   - **Benefit:** Allows annual changes without code modifications
   - **Affected Files:** `templates/school.html`, `app.py`, `database.py`

### General Dashboard Enhancements
- Add export functionality to School tab metrics
- Implement printable/PDF view
- Add historical comparison (current year vs. prior years)

---

## Next Steps

### Remaining Tabs to Design (Priority Order)
1. ⚔️ **Teams Tab** - Use School tab as design model
2. 🎓 **Classes Tab** - Use School tab as design model
3. 👤 **Students Tab** - Use School tab as design model

### Production Deployment (After HTML Approval)
1. Update `templates/base.html` with new navigation
2. Create/update School tab template
3. Add Flask routes in `app.py`
4. Implement database queries in `database.py`
5. Add table update timestamp tracking

---

## Design Decisions Summary

### Navigation
✅ Option C: Flat dashboards (School/Teams/Classes/Students) + grouped "Reports & Data"
✅ Upload stays top-level
✅ Help and Admin stay top-level

### School Tab Layout
✅ 5-metric headline banner (detailed format with context)
✅ Auto-filtering dropdown (no Apply button)
✅ 3-column grid: Teams (left), Performers (center), Participation (right)
✅ Data Integrity Alert below grid (conditional display)
✅ Hybrid metadata access (button + collapsible footer)

### Formatting Standards
✅ Fundraising (not Donations)
✅ Students (default), Readers (reading-specific only)
✅ "X of Y Students (Z%)" format
✅ "N hours (M min)" format
✅ Comma-delimited ties + note

### Color Scheme
✅ Option J maintained (Navy/Teal/Gold)
✅ Team Staub: Blue cards
✅ Team Kitsko: Gold cards
✅ Data alerts: Coral/red

---

## Session Context (For Continuity)

### ✅ Completed (Session 1 - 2025-10-18)
- School tab ASCII design → HTML prototype
- HTML prototype: `/prototypes/dashboard_school_tab_v2.html`
- All vertical space optimizations applied
- Git repository initialized
- Initial commit created on `main` branch
- Feature branch created: `feature/dashboard-school-tab-redesign`

### ✅ Completed (Session 2 - 2025-10-18)
- **Production Implementation:** School tab deployed to production
- **Date Filtering:** Fixed cumulative filtering (single-day to through-date)
- **Visual Indicators:** Added ◐ icons with tooltips for date-filtered metrics
- **Bug Fixes:**
  - Reading leader N/A issue (SQL subquery alias)
  - Text alignment issues (icon placement)
  - CSS visibility on light backgrounds
- **Commits:**
  - `78a4028` - Fix date filtering and cumulative participation metrics
  - `a474dc5` - Preserve date filter selection after page reload
  - `2af41f0` - Resolve School tab data display issues
  - `759b71b` - Implement School tab with Option J design
  - `5aa4236` - Add visual indicators for date-filtered metrics

### 🔄 Current Status
- ✅ School tab complete and deployed on `feature/dashboard-school-tab-redesign`
- 🎯 School tab designated as reference model for future tabs
- 📝 Ready to begin Teams/Classes/Students tabs using School as model

### 📋 To Resume in Next Session

**Say to Claude:**
```
Resume dashboard redesign - Feature 23.

We completed:
- HTML prototype approved (dashboard_school_tab_v2.html)
- Git initialized with baseline commit
- Feature branch: feature/dashboard-school-tab-redesign

Next steps:
1. Implement School tab in production (base.html + routes + queries)
2. School tab should be landing page (both / and /school routes)
3. Use prototype as exact design reference

All specs in Feature 23 documentation.
```

### 🎯 Next Implementation Tasks
1. Update `base.html` with new navigation (Option C structure)
2. Create School tab template with prototype design
3. Add Flask routes: `/` and `/school` → same school_tab() function
4. Implement database queries for School metrics
5. Test functionality
6. Commit to feature branch
7. Merge to main (after user approval)

### 📁 Key Files to Reference
- Design spec: This file (feature-23)
- Prototype: `/prototypes/dashboard_school_tab_v2.html`
- Current templates: `templates/base.html`, `templates/index.html`
- Routes: `app.py`
- Queries: `database.py`

---

**[← Back to Index](../00-INDEX.md)**
