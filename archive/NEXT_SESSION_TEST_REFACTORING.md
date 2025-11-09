# Next Session: Test Refactoring

**Created:** 2025-11-09 (Session 4)
**Status:** Ready to start
**Estimated Time:** 1-2 hours

---

## 🎯 Quick Start

When you start the next session, say:

> "Continue with test refactoring from TEST_REFACTORING_NEEDED.md. Refactor the 4 test files to remove sys.exit() patterns."

---

## 📋 Task Overview

**Goal:** Convert 4 standalone validation scripts to proper pytest test functions

**Files to Refactor:**
1. `tests/test_db_comparison_all_49_queries.py`
2. `tests/test_db_comparison_complete_validation.py`
3. `tests/test_db_comparison_data_validation.py`
4. `tests/test_db_comparison_queries.py`

**Problem:** These files call `sys.exit()` at module level, causing pytest collection failures

**Solution:** Convert to proper pytest test functions with assertions

---

## 🔧 Refactoring Pattern

**Before (Brittle):**
```python
if __name__ == "__main__":
    # ... validation logic ...
    failed = 0

    for query_name, query_func in queries:
        result = query_func()
        if result != expected:
            print(f"❌ FAILED: {query_name}")
            failed += 1
        else:
            print(f"✅ PASSED: {query_name}")

    sys.exit(0 if failed == 0 else 1)  # ❌ Causes pytest collection error
```

**After (Proper pytest):**
```python
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

    for query_name, query_func, expected_value in queries:
        result = query_func()
        if result != expected_value:
            failed.append(f"{query_name}: expected {expected_value}, got {result}")

    # ✅ Use pytest assertion instead of sys.exit()
    assert len(failed) == 0, f"{len(failed)} queries failed:\n" + "\n".join(failed)
```

---

## ✅ Success Criteria

- [ ] All 4 test files refactored to use pytest assertions
- [ ] `pytest -xvs` runs without collection errors
- [ ] All 49 queries still validate correctly
- [ ] Can run individual test functions
- [ ] Test output is clear and shows which queries failed (if any)
- [ ] Pre-commit hook passes (all tests run successfully)
- [ ] No changes to actual query logic or validation criteria

---

## 📝 Testing Commands

**Before refactor (current workaround):**
```bash
pytest -v --ignore=tests/test_db_comparison_all_49_queries.py \
          --ignore=tests/test_db_comparison_complete_validation.py \
          --ignore=tests/test_db_comparison_data_validation.py \
          --ignore=tests/test_db_comparison_queries.py
```

**After refactor (should work):**
```bash
# Run all tests including the refactored ones
pytest -xvs

# Run specific test
pytest tests/test_db_comparison_all_49_queries.py::test_all_49_database_comparison_queries -v
```

---

## 🎯 Implementation Order

**Recommended approach:**
1. Start with `test_db_comparison_all_49_queries.py` (most complex)
2. Test it: `pytest tests/test_db_comparison_all_49_queries.py -v`
3. Move to `test_db_comparison_complete_validation.py`
4. Test it: `pytest tests/test_db_comparison_complete_validation.py -v`
5. Refactor remaining 2 files
6. Run full test suite: `pytest -xvs`
7. Verify pre-commit hook passes

---

## 📚 Reference Files

**Complete details:** See `TEST_REFACTORING_NEEDED.md`
**Context:** All test files validate database comparison functionality (Feature 32)

---

## 🚀 After Completion

When done, commit with:

```bash
git add tests/test_db_comparison_*.py
git commit -m "Refactor database comparison tests to remove sys.exit() patterns

- Converted 4 standalone validation scripts to proper pytest test functions
- Replaced sys.exit() calls with pytest assertions
- No changes to validation logic or criteria
- All 49 database comparison queries still validated correctly
- Pre-commit hook now passes without --ignore flags

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
"
```

---

**Last Updated:** 2025-11-09 (Session 4)
