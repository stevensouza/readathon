# Changelog

All notable changes to the Read-a-Thon Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project uses **School Year Calendar Versioning** (vYYYY.MINOR.PATCH).

## [v2026.1.0] - 2025-10-22

### First Stable Release for 2025-2026 School Year

This is the baseline release with core functionality complete for managing the 2025-2026 school year read-a-thon event.

### Features
- Complete read-a-thon tracking system for 411 students
- 22 comprehensive reports (Q1-Q23) covering all metrics
- Enhanced metadata for all reports (column descriptions, data sources, key terms, automated analysis)
- Team competition tracking (2 teams with color bonus support)
- Daily and cumulative metrics tracking
- Prize drawing support with random selection
- Multi-file CSV upload with automatic date extraction
- Upload audit trail for data integrity
- Workflow automation for running multiple reports in sequence
- Data integrity reconciliation reports (Q21, Q22, Q23)
- Modern responsive UI with Bootstrap 5
- Local SQLite database (no server required)

### Technical
- Flask 3.0.0 web framework
- SQLite 3 database with 7 core tables
- Bootstrap 5.3.0 frontend
- SQL queries extracted to `queries.py` module
- Analysis modal for enhanced report insights
- Privacy-focused: Sanitized sample data and screenshots

### Privacy & Security
- Git history cleaned of sensitive school data
- Team names anonymized in public files (Phoenix/Dragons)
- Sample database with fictitious data included
- Real student data excluded from version control

---

## Versioning Scheme

This project uses **School Year Calendar Versioning**: `vYYYY.MINOR.PATCH`

- **YYYY**: School year (e.g., 2026 = 2025-2026 school year)
- **MINOR**: Feature additions and improvements (increments for each significant update)
- **PATCH**: Bug fixes and small updates (increments for each release)

### Examples
- `v2026.1.0` → `v2026.1.1`: Bug fix
- `v2026.1.0` → `v2026.2.0`: New feature or major update
- `v2026.1.0` → `v2027.1.0`: Next school year version

### When to Increment
- **Year**: New school year or major redesign
- **Minor**: When adding features, reports, or significant improvements
- **Patch**: For bug fixes, documentation updates, or minor tweaks
