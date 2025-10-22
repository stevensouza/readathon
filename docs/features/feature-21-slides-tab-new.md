# Feature 21: Slides Tab ✨ NEW

**[← Back to Index](../00-INDEX.md)**

---

### Feature 21: Slides Tab ✨ NEW
**Feature:** Dedicated "Slides" tab for presentation-ready output that can be copied directly to Google Slides.

**Requirements:**
- Add new navigation tab: "Slides" (between Workflows and Tables)
- Single page with two sections:
  - **Daily Slides** - Updated throughout campaign
  - **Final Slides** - Run at campaign end
- Add "Jump to:" quick navigation links at top for Daily/Final sections

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Slides                                           │
│ Jump to: [Daily Slides] [Final Slides]           │
├─────────────────────────────────────────────────┤
│ Daily Slides (Updated: Jan 15, 2:45 PM)         │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│ │ Slide 2:     │ │ Slide 3:     │ │ Slide 4: │ │
│ │ Grade Level  │ │ Top Students │ │ Teams    │ │
│ │ Participation│ │              │ │          │ │
│ │              │ │              │ │          │ │
│ │ [Copy] [CSV] │ │ [Copy] [CSV] │ │ [Copy]   │ │
│ └──────────────┘ └──────────────┘ └──────────┘ │
│                                                   │
│ Final/End of Contest Slides                      │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│ │ Final Slide 1│ │ Final Slide 2│ │ Winners  │ │
│ │ Overall      │ │ Record       │ │          │ │
│ │ Results      │ │ Breakers     │ │          │ │
│ │ [Copy] [CSV] │ │ [Copy] [CSV] │ │ [Copy]   │ │
│ └──────────────┘ └──────────────┘ └──────────┘ │
└─────────────────────────────────────────────────┘
```

**Key Characteristics:**
- **Box-based layout** - Similar to Dashboard design (white cards with shadows)
- **Presentation-ready** - Show ONLY data that appears in actual Google Slides
- **No extra columns** - Remove debugging info, technical details, extra metadata
- **Clean formatting** - Optimized for copy-paste workflow
- **Slide metadata** - Each box shows slide number, title/concept, data table
- **Copy buttons** - Easy copy-to-clipboard for each slide

**Example Slide Box:**
```
┌─────────────────────────────────────────────────┐
│ Slide 2: Grade Level Participation               │
│ As of October 6, 2024                            │
│                                                   │
│ Grade Level | Class            | % Participation │
│ ──────────────────────────────────────────────── │
│ Kindergarten| Mrs. Brown - PM|           33.3%│
│ 1st Grade   | Mrs. Porter       |           40.0%│
│ 2nd Grade   | Mrs. Wilson       |           47.4%│
│ ...                                               │
│                                                   │
│ [Copy to Clipboard] [Export CSV]                 │
└─────────────────────────────────────────────────┘
```

**Implementation:**
- Create `/slides` route in `app.py`
- Create `templates/slides.html`
- Query slide-specific reports (slide2, slide3, etc.)
- Filter columns to only those needed for presentation
- Group queries into Daily vs Final sections
- Use same card/box styling as Dashboard (Option J design)

**Mapping Queries to Slides:**
- Daily Slides:
  - Slide 2: Grade Level Participation (query: slide2)
  - Slide 3: Top Fundraising Students (query: slide3)
  - Slide 4: Team Competition (query: slide4)
  - [Additional slides as needed]
- Final Slides:
  - Final Results Summary (query: final_slide1)
  - Record Breakers (query: final_slide2)
  - Winners Announcement (query: final_slide3)
  - [Additional final slides as needed]

**User Workflow:**
1. Navigate to Slides tab
2. Scroll to desired slide box (or use Jump to navigation)
3. Click "Copy to Clipboard" button
4. Open Google Slides presentation
5. Paste data into slide
6. Format/style as needed in Google Slides

**Notes:**
- Slides page should NOT include extra analysis columns present in Reports
- Focus is on clean, presentation-ready output
- Similar to Dashboard in visual design, but organized by slide number
- This is separate from Reports tab (which can have technical columns)

---



---

**[← Back to Index](../00-INDEX.md)**
