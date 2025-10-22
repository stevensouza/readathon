# Feature 10: "Run All Reports" Feature

**[← Back to Index](../00-INDEX.md)**

---

### Feature 10: "Run All Reports" Feature
**Requirements:**
- New page: `/run_all_reports`
- Add link in Reports page header: "Run All Reports"
- Display all reports on one page:
  - Each report in a collapsible section (Bootstrap accordion or similar)
  - All sections expanded by default
  - User can collapse any section
- Include at top:
  - "Copy All to Clipboard" button (copies all visible data)
  - "Expand All" / "Collapse All" buttons
  - Total reports count
- Format each report section:
  ```
  ┌─ Q1: Table Row Counts ─────────────────────────────┐
  │ [Collapse] [Copy] [Export CSV]                     │
  │ Description: Database table row counts             │
  │ [Table data here]                                  │
  └────────────────────────────────────────────────────┘
  ```

**Implementation:**
- Use Bootstrap accordion: `<div class="accordion">`
- Generate all reports server-side in one route
- Use JavaScript for "Copy All" functionality
- Consider performance with many reports (lazy load or pagination if needed)

---



---

**[← Back to Index](../00-INDEX.md)**
