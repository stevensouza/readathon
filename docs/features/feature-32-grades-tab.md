# Feature 32: Grades Tab

**[← Back to Index](../00-INDEX.md)**

---

### Feature 32: Grades Tab
**Requirement:** Add a new "Grades" tab to the Dashboard to display grade-level data and metrics.

**Purpose:**
- View read-a-thon metrics grouped by grade level (K, 1, 2, 3, 4, 5)
- Compare performance across grades
- Identify grade-level trends and leaders

**Tab Location:** Dashboard section (alongside School, Teams, Classes, Students)

**Data to Display:**

1. **Grade-Level Summary Table:**
   - Grade level
   - Total students in grade
   - Total reading minutes (capped)
   - Average minutes per student
   - Participation rate (% with any reading)
   - Total donations raised
   - Average donation per student

2. **Grade Competition Metrics:**
   - Highest average minutes per student
   - Highest participation rate
   - Most total minutes
   - Most total donations

3. **Grade-Level Details (Collapsible Cards):**
   - For each grade (K-5):
     - List of classes in that grade
     - Top readers in that grade
     - Grade-specific goals (from Grade_Rules table)
     - Progress toward grade goals

**Design:**
- Follow Feature 24: Design Consistency (use School tab as model)
- Use Option J color scheme (Navy, Teal, Gold, Coral)
- Responsive card layout
- Sortable tables
- Collapsible sections for each grade

**Data Sources:**
- `Roster` table (student grade levels)
- `Class_Info` table (class-grade relationships)
- `Reader_Cumulative` table (student totals)
- `Daily_Logs` table (daily reading data)
- `Grade_Rules` table (grade-specific goals)

**Implementation Notes:**
- Create new route: `/dashboard/grades`
- Create new template: `templates/grades.html`
- Add database method: `get_grades_summary()` in `database.py`
- Update navigation in `base.html` to include Grades tab

**Related Features:**
- Feature 23: Dashboard Design (parent feature)
- Feature 24: Design Consistency (styling model)

---

**Status:** NEW
**Priority:** Medium
**Dependencies:** Feature 24 (Design Consistency)

---

**[← Back to Index](../00-INDEX.md)**
