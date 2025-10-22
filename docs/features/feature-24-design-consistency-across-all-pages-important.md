# Feature 24: Design Consistency Across All Pages ✨ IMPORTANT

**[← Back to Index](../00-INDEX.md)**

---

### Feature 24: Design Consistency Across All Pages ✨ IMPORTANT
**Requirement:** ALL pages should follow the Option J: Refined Zen design language.

**Reference Implementation:** 🎯 **School Tab** (`templates/school.html`) is the model for all pages.

**Apply To:**
- **Dashboard Tabs:**
  - ✅ School (complete - reference implementation)
  - ⚔️ Teams (use School tab as model)
  - 🎓 Classes (use School tab as model)
  - 👤 Students (use School tab as model)
- **Other Tabs:**
  - **Slides** tab (use same box/card styling)
  - **Workflows** tab (use same card/button styling)
  - **Reports** tab (use same table styling, buttons)
  - **Tables** tab (use same table styling)
  - **Upload** tab (use same card styling)
  - **Help** tab (use same section styling)
  - **Admin** tab (use same card/section styling)

**Consistent Elements:**
- **Cards/Boxes:** White background, rounded corners (0.5rem), subtle shadow
- **Colors:** Navy, Teal, Gold, Coral (as defined in Option J)
- **Typography:** Same font sizes and weights
- **Tables:** Alternating row backgrounds, black numbers
- **Buttons:** Consistent styling (size, colors, hover states)
- **Spacing:** Consistent padding, margins, gaps
- **Top bars/headers:** Navy background with teal accents
- **Error/warning messages:** Coral color (#ff6b6b)

**Implementation Notes:**
- Extract common CSS from Option J into `base.html` styles
- Create reusable CSS classes for cards, tables, buttons
- Ensure all templates inherit from `base.html`
- Test responsive behavior on all pages

---



---

**[← Back to Index](../00-INDEX.md)**
