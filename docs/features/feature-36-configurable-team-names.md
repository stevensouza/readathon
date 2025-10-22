# Feature 36: Configurable Team Names

**[← Back to Index](../00-INDEX.md)**

---

## Feature 36: Configurable Team Names

**Status:** NEW
**Priority:** Medium
**Type:** Enhancement - Configuration

---

## Current State (Hardcoded)

Team names "Kitsko" and "Staub" are currently hardcoded throughout the codebase:
- Database queries
- UI templates (base.html, school.html, reports.html, etc.)
- Report generation logic
- Team competition calculations

**Problem:** Cannot reuse this application for other schools or events without code changes.

---

## Requirements

### 1. Configuration File
Create a configuration system for team names:
- Store team names in a config file (`config.json` or `teams_config.json`)
- Default to "Kitsko" and "Staub" if no config exists
- Support 2+ teams (flexible for future expansion)

**Example config.json:**
```json
{
  "teams": [
    {
      "id": 1,
      "name": "Kitsko",
      "display_name": "Team Kitsko",
      "color": "#f59e0b",
      "emoji": "🟡"
    },
    {
      "id": 2,
      "name": "Staub",
      "display_name": "Team Staub",
      "color": "#1e3a5f",
      "emoji": "🔵"
    }
  ],
  "event_name": "Read-a-Thon 2025",
  "school_name": "Your School Name"
}
```

### 2. Database Schema Update
Add a `Teams` configuration table:
```sql
CREATE TABLE Teams (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT NOT NULL,
    display_name TEXT,
    color_code TEXT,
    emoji TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Update `Roster` table foreign key to reference `Teams.team_id` instead of hardcoded names.

### 3. Code Refactoring
Replace hardcoded strings with configuration lookups:
- `database.py` - All SQL queries with team filters
- Templates - All team name references
- Reports - Dynamic team name display

### 4. Admin UI for Configuration
Add admin page section for:
- View current team configuration
- Edit team names, colors, emojis
- Preview changes before applying
- Reset to defaults

### 5. Migration Strategy
For existing databases with "Kitsko" and "Staub":
- Automatic migration script to populate Teams table
- Update Roster.team foreign key references
- Preserve historical data

---

## Benefits

1. **Reusability**: Other schools can use this system with their team names
2. **Flexibility**: Support more than 2 teams in future
3. **Customization**: Schools can set colors, emojis, display names
4. **Maintainability**: Changes to team names don't require code edits

---

## Implementation Steps

1. Create configuration schema and default config file
2. Add Teams table to database
3. Update database.py queries to use config
4. Update all templates with Jinja2 template variables
5. Build admin configuration UI
6. Create migration script for existing data
7. Test with sample and production databases
8. Update documentation

---

## Related Features
- Feature 17: Admin Tab & Functions (where configuration UI would live)
- Feature 16: Flexible Multi-Database System (ensures config works across environments)

---

**Status:** NEW
**Priority:** Medium
**Created:** 2025-10-22

---

**[← Back to Index](../00-INDEX.md)**
