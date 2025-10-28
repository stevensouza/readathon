#!/bin/bash
# Pre-commit hook to run tests before allowing commit
#
# To install this hook, run:
#   chmod +x pre-commit.sh
#   cp pre-commit.sh .git/hooks/pre-commit
#
# Or create a symbolic link:
#   ln -s ../../pre-commit.sh .git/hooks/pre-commit

echo "🧪 Running school page tests..."
python3 -m pytest test_school_page.py -v

# If tests fail, prevent commit
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ School page tests failed! Commit aborted."
    echo "Fix the failing tests before committing, or use 'git commit --no-verify' to skip tests."
    exit 1
fi

echo ""
echo "🧪 Running grade level page tests..."
python3 test_grade_level_page.py

# If tests fail, prevent commit
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Grade level tests failed! Commit aborted."
    echo "Fix the failing tests before committing, or use 'git commit --no-verify' to skip tests."
    exit 1
fi

echo ""
echo "🧪 Running teams page tests..."
python3 -m pytest test_teams_page.py -v

# If tests fail, prevent commit
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Teams page tests failed! Commit aborted."
    echo "Fix the failing tests before committing, or use 'git commit --no-verify' to skip tests."
    exit 1
fi

echo ""
echo "✅ All tests passed!"
exit 0
