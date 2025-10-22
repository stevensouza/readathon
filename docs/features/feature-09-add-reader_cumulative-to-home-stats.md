# Feature 9: Add Reader_Cumulative to Home Stats

**[← Back to Index](../00-INDEX.md)**

---

### Feature 9: Add Reader_Cumulative to Home Stats
**Status:** ✅ **OBSOLETE** - Table counts are now on Admin → Reports → Q1 instead of home page

**Original Request:** Add Reader_Cumulative count to home page table stats

**Current Implementation:**
- Admin page → Reports tab → Q1: Table Row Counts shows all table counts
- Includes: Roster, Class_Info, Grade_Rules, Daily_Logs, Reader_Cumulative, Team_Color_Bonus
- `index.html` is not the active home page (School tab is the landing page)

**No action needed** - functionality exists in better location (Admin Reports)

---

## Original Spec (Archived)

**Original Request:**
**Current:** Home page shows counts for Roster, Class_Info, Grade_Rules, Daily_Logs

**Add:**
```html
<div class="col-md-3">
    <div class="card stat-card">
        <div class="card-body">
            <h5 class="card-title text-muted">Reader Cumulative Entries</h5>
            <h2 class="mb-0">{{ counts.Reader_Cumulative }}</h2>
            <p class="text-muted mb-0" style="font-size: 0.7rem;">Source: Reader_Cumulative table</p>
        </div>
    </div>
</div>
```

**Implementation:**
- Modify `app.py` index route: `counts = db.get_table_counts()` already includes this
- Add to `templates/index.html` after Daily_Logs stat card
- Adjust grid to 5 columns or 2 rows

---



---

**[← Back to Index](../00-INDEX.md)**
