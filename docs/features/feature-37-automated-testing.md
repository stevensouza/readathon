# Feature 37: Automated Testing

**[← Back to Index](../00-INDEX.md)**

---

## Overview

Automated testing framework to ensure core functionality remains intact as changes are made to the codebase. Prevents regressions and maintains data integrity.

## Current Implementation

### School Page Integration Tests

**File:** `test_school_page.py`

Comprehensive test suite for the school dashboard (`/school` route) with 9 test cases:

1. **test_page_loads_successfully** - Verifies page loads without HTTP errors
2. **test_headline_metrics_present** - Checks all headline metrics are displayed (Campaign Day, Fundraising, Minutes Read, Participation, Goal Met)
3. **test_team_competition_structure** - Validates team competition section structure
4. **test_top_performers_present** - Ensures top performers section exists
5. **test_participation_statistics_present** - Verifies participation statistics section
6. **test_sample_data_integrity** - Validates calculations match sample database values
7. **test_no_error_messages** - Checks page doesn't contain error messages
8. **test_total_minutes_display** - Verifies minutes/hours metrics are displayed
9. **test_percentage_formats** - Validates percentage formatting

### Test Framework

**Framework:** pytest 7.4.3
- Industry-standard Python testing framework
- Simple, readable syntax
- Excellent error reporting
- Easy to expand for future tests

**Test Approach:**
- Uses Flask test client for integration testing
- Tests against sample database (`readathon_sample.db`)
- Validates both data structure and sample data integrity
- Flexible assertions to handle various display formats

## Running Tests

### Manual Execution

```bash
# Run all tests with verbose output
python3 -m pytest test_school_page.py -v

# Run specific test
python3 -m pytest test_school_page.py::TestSchoolPage::test_page_loads_successfully -v

# Run with detailed failure output
python3 -m pytest test_school_page.py -vv
```

### Pre-Commit Hook (Optional)

Automatically run tests before each commit:

```bash
# Install the pre-commit hook
cp pre-commit.sh .git/hooks/pre-commit

# Or create a symbolic link
ln -s ../../pre-commit.sh .git/hooks/pre-commit
```

**Hook behavior:**
- Runs all school page tests before allowing commit
- If tests fail, commit is aborted
- Provides clear error messages
- Can be bypassed with `git commit --no-verify` if needed

## Dependencies

Added to `requirements.txt`:
```
Flask==3.0.0
pytest==7.4.3
```

## Future Enhancements

### Phase 2: Expand Test Coverage

**Additional Page Tests:**
- Teams page (`/teams`)
- Classes page (`/classes`)
- Students page (`/students`)
- Upload page (`/upload`)
- Reports pages (Q1-Q23)
- Admin page (`/admin`)

**Report-Specific Tests:**
- Verify report calculations for all 22 reports
- Test data integrity checks (Q21-Q23)
- Validate report metadata rendering
- Test CSV export functionality

### Phase 3: Unit Tests

**Database Layer:**
- Test `ReadathonDB` class methods
- Test `ReportGenerator` class
- Validate SQL query generation
- Test data sanitization

**Utility Functions:**
- Date filtering logic
- Calculation functions
- Data transformation utilities

### Phase 4: End-to-End Tests

**User Workflows:**
- Complete upload workflow (CSV → database → reports)
- Database switching (prod ↔ sample)
- Report generation and export
- Multi-step workflows

### Phase 5: Performance Testing

**Load Testing:**
- Test with larger datasets (1000+ students)
- Measure report generation time
- Identify bottlenecks
- Optimize slow queries

### Phase 6: Continuous Integration

**GitHub Actions:**
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest test_school_page.py -v
```

**Benefits:**
- Automatic testing on every push
- Test across multiple Python versions
- Prevent broken code from being merged
- Build status badges for README

### Phase 7: Test Data Management

**Fixtures and Mocking:**
- Create comprehensive test fixtures
- Mock external dependencies
- Parameterized tests for multiple scenarios
- Snapshot testing for HTML output

## Technical Notes

### Sandbox Violations

When running tests, you may see sandbox violations like:
```
python3.11(80635) deny(1) file-write-create
/opt/anaconda3/lib/.../anyio/__pycache__/...
```

**These are harmless** - the sandbox blocks Python from writing bytecode cache files to system directories, which is correct security behavior. Tests run successfully despite these blocks.

### Test Design Philosophy

- **Structure over exact values:** Tests verify that sections exist rather than exact content
- **Flexible assertions:** Handle various display formats (hours vs minutes, decimal vs integer)
- **Sample database:** Always test against `readathon_sample.db` for consistency
- **Integration focus:** Test full request→response cycle, not just isolated functions

---

**Status:** ✅ Implemented (Phase 1: School Page Tests)
**Version:** Added in v2026.2.1
**Related Files:**
- `test_school_page.py` - Test suite
- `pre-commit.sh` - Optional pre-commit hook
- `requirements.txt` - Added pytest dependency

---

**[← Back to Index](../00-INDEX.md)**
