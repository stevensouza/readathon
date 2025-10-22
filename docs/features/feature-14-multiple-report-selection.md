# Feature 14: Multiple Report Selection

**[← Back to Index](../00-INDEX.md)**

---

### Feature 14: Multiple Report Selection
**Requirements:**
- Add checkboxes to each report in list
- Add action buttons at top:
  - [Select All] [Deselect All] [Run Selected]
- When "Run Selected" clicked:
  - Open results in single page (like "Run All Reports")
  - Each checked report shows as collapsible section
  - All expanded by default
  - Include "Copy All" button

**Implementation:**
- Add `<input type="checkbox" class="report-checkbox" data-report-id="q2">` to each report item
- JavaScript to handle selection state
- POST to `/run_multiple_reports` with selected report IDs
- Return accordion-style results page

---



---

**[← Back to Index](../00-INDEX.md)**
