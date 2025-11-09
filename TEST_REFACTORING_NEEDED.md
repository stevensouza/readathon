# Test Refactoring: Remove Brittle sys.exit() Patterns

**Created:** 2025-11-09
**Priority:** Medium (improves test reliability, not blocking)
**Status:** Documented, ready to implement

---

## 🔴 Problem

Several test files call `sys.exit()` at module level, causing pytest collection failures:

```bash
pytest -xvs
# ERROR tests/test_db_comparison_all_49_queries.py - SystemExit: 0
# ERROR tests/test_db_comparison_complete_validation.py - SystemExit: 0
# ERROR tests/test_db_comparison_data_validation.py - SystemExit: 0
# ERROR tests/test_db_comparison_queries.py - SystemExit: 0
```

These files were written as **standalone validation scripts** (not proper pytest tests) and call `sys.exit(0)` after printing their results. While the actual validation passes (all queries return correct data), pytest fails during collection.

**Current Workaround:**
```bash
pytest -v --ignore=tests/test_db_comparison_all_49_queries.py \
          --ignore=tests/test_db_comparison_complete_validation.py \
          --ignore=tests/test_db_comparison_data_validation.py \
          --ignore=tests/test_db_comparison_queries.py
```

This works but is brittle and requires manually excluding these files.

---

## 🎯 Solution: Convert to Proper Pytest Tests

**Current Pattern (Brittle):**
```python
# test_db_comparison_all_49_queries.py
if __name__ == "__main__":
    # ... validation logic ...
    failed = 0

    # Run 49 database comparison queries
    for query_name, query_func in queries:
        result = query_func()
        if result != expected:
            print(f"❌ FAILED: {query_name}")
            failed += 1
        else:
            print(f"✅ PASSED: {query_name}")

    # Print summary
    print(f"\nTotal: {len(queries)}")
    print(f"Passed: {len(queries) - failed}")
    print(f"Failed: {failed}")

    sys.exit(0 if failed == 0 else 1)  # ❌ Causes pytest collection error
```

**Better Pattern (Proper pytest):**
```python
# test_db_comparison_all_49_queries.py
import pytest

def test_all_49_database_comparison_queries():
    """
    Validate all 49 database comparison queries return correct data.

    Tests:
    - School Level: 10 queries
    - Student Level: 9 queries
    - Team Level: 10 queries
    - Grade Level: 10 queries
    - Class Level: 10 queries

    Total: 49 queries
    """
    failed = []

    # Run 49 database comparison queries
    for query_name, query_func, expected_value in queries:
        result = query_func()
        if result != expected_value:
            failed.append(f"{query_name}: expected {expected_value}, got {result}")

    # ✅ Use pytest assertion instead of sys.exit()
    assert len(failed) == 0, f"{len(failed)} queries failed:\n" + "\n".join(failed)
```

**Benefits:**
- ✅ No pytest collection errors
- ✅ Integrates with pytest reporting (shows in test summary)
- ✅ Can use pytest features (fixtures, parametrize, markers)
- ✅ Can run individual tests: `pytest test_db_comparison.py::test_school_level_queries`
- ✅ Works with pytest plugins (coverage, parallel execution, etc.)

---

## 📋 Files to Refactor

### 1. `test_db_comparison_all_49_queries.py`
**Current:** Runs all 49 database comparison queries and calls sys.exit()
**Refactor to:** Single test function that validates all 49 queries with pytest assertions

### 2. `test_db_comparison_complete_validation.py`
**Current:** Comprehensive validation of all 49 queries with detailed output
**Refactor to:** Test function that validates schema and data for all queries

### 3. `test_db_comparison_data_validation.py`
**Current:** Validates data accuracy for all 49 queries
**Refactor to:** Test function or parametrized tests for each query type

### 4. `test_db_comparison_queries.py`
**Current:** Tests query execution and schema
**Refactor to:** Test function that validates query structure and results

---

## 🔧 Implementation Plan

### Step 1: Refactor test_db_comparison_all_49_queries.py
```python
def test_all_49_database_comparison_queries():
    """Validate all 49 database comparison queries return correct data."""
    db = get_database()
    failed = []

    # School Level (10 queries)
    school_queries = [
        ("School Fundraising", db.get_school_fundraising, 31758.00),
        ("School Minutes", db.get_school_minutes, 110093),
        # ... 8 more queries
    ]

    for name, func, expected in school_queries:
        result = func()
        if result != expected:
            failed.append(f"{name}: expected {expected}, got {result}")

    # Student Level (9 queries)
    # Team Level (10 queries)
    # Grade Level (10 queries)
    # Class Level (10 queries)

    assert len(failed) == 0, f"{len(failed)} queries failed:\n" + "\n".join(failed)
```

### Step 2: Refactor test_db_comparison_complete_validation.py
```python
def test_database_comparison_complete_validation():
    """Comprehensive validation of all 49 database comparison queries."""
    db = get_database()

    # Validate schema
    for query_name, query_func in all_queries:
        result = query_func()
        assert result is not None, f"{query_name} returned None"
        assert isinstance(result, (int, float, str, list, dict)), f"{query_name} returned unexpected type"

    # Validate data accuracy
    # ... assertions for each query
```

### Step 3: Refactor test_db_comparison_data_validation.py
```python
@pytest.mark.parametrize("query_name,query_func,expected_value", [
    ("School Fundraising", db.get_school_fundraising, 31758.00),
    ("School Minutes", db.get_school_minutes, 110093),
    # ... all 49 queries as test parameters
])
def test_database_comparison_query(query_name, query_func, expected_value):
    """Validate individual database comparison query."""
    result = query_func()
    assert result == expected_value, f"{query_name}: expected {expected_value}, got {result}"
```

### Step 4: Refactor test_db_comparison_queries.py
Similar to Step 3, but focused on query execution and schema validation.

---

## ✅ Acceptance Criteria

- [ ] All 4 test files refactored to use pytest assertions instead of sys.exit()
- [ ] `pytest -xvs` runs without collection errors
- [ ] All 49 queries still validate correctly
- [ ] Can run individual test functions: `pytest test_db_comparison.py::test_all_49_database_comparison_queries`
- [ ] Test output is clear and shows which queries failed (if any)
- [ ] Pre-commit hook passes (all tests run successfully)
- [ ] No changes to actual query logic or validation criteria

---

## 📝 Notes

**Why these files were written this way:**
- They were created as standalone validation scripts to verify database comparison accuracy
- The `sys.exit()` pattern was appropriate for standalone scripts but incompatible with pytest
- They print detailed output to console (useful for debugging)

**Backward compatibility:**
- Keep the detailed output format (helps with debugging)
- Maintain the same validation criteria (don't change what's being tested)
- Add pytest-friendly assertions without losing the detailed validation logic

**Testing the refactor:**
```bash
# Before refactor (current workaround)
pytest -v --ignore=tests/test_db_comparison_*.py

# After refactor (should work)
pytest -xvs

# Run specific test
pytest test_db_comparison_all_49_queries.py::test_all_49_database_comparison_queries -v
```

---

**Last Updated:** 2025-11-09
**Ready to implement:** Yes
**Estimated Time:** 1-2 hours (straightforward refactoring, no logic changes)
