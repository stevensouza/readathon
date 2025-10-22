# Feature 19: Improve Delete Confirmations

**[← Back to Index](../00-INDEX.md)**

---

### Feature 19: Improve Delete Confirmations
**Current Issues:**
- Cumulative deletion requires typing "DELETE" (case-sensitive)
- Daily log deletion has no confirmation prompt

**Requirements:**

**A. Case-Insensitive Confirmation:**
- Accept: "DELETE", "delete", "Delete", "DEL", "del", "Del"
- Use `.toLowerCase()` or `.toUpperCase()` in JavaScript

**B. Add Confirmation to Daily Delete:**
```javascript
async function deleteDay(logDate) {
    const userInput = prompt(
        `⚠️ DELETE DATA WARNING!\n\n` +
        `You are about to permanently delete ALL data for ${logDate}.\n\n` +
        `This action CANNOT be undone!\n\n` +
        `Type "DELETE" or "DEL" to confirm:`
    );

    if (!userInput) return;

    const confirmed = ['delete', 'del'].includes(userInput.toLowerCase());

    if (!confirmed) {
        alert('Deletion cancelled. You must type "DELETE" or "DEL" to confirm.');
        return;
    }

    // Proceed with deletion...
}
```

**C. Add Same to Cumulative Delete:**
- Apply same logic to cumulative data deletion
- Update `/api/delete_cumulative` endpoint
- Show similar warning message

**Files to Modify:**
- `templates/upload.html` (upload history delete button scripts)
- `templates/index.html` (if delete available from dashboard)
- Both JavaScript `deleteDay()` and `deleteCumulative()` functions

---



---

**[← Back to Index](../00-INDEX.md)**
