#!/bin/bash
# Read-a-Thon Application Installation Script
# Idempotent installation for macOS
# Safe to run as many times as you like: completed steps are skipped, Desktop shortcuts
# are refreshed if outdated, and every run reports the current state of the install.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Icons
CHECK="✅"
CROSS="❌"
WARN="⚠️"
INFO="ℹ️"
ROCKET="🚀"

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}${ROCKET}  Read-a-Thon Application Installer${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}${CHECK}${NC} $1"
}

print_error() {
    echo -e "${RED}${CROSS}${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}${WARN}${NC} $1"
}

print_info() {
    echo -e "${BLUE}${INFO}${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

# Detect existing ReadAThon installation
print_header "Checking Existing Installation"

if [ -f "$SCRIPT_DIR/VERSION" ]; then
    CURRENT_VERSION=$(cat "$SCRIPT_DIR/VERSION")
    print_status "Found existing Read-a-Thon installation: $CURRENT_VERSION"
    EXISTING_INSTALL=true
else
    print_info "No existing installation detected (fresh install)"
    EXISTING_INSTALL=false
fi

# Check macOS version
print_header "System Requirements"

OS_VERSION=$(sw_vers -productVersion)
print_info "macOS Version: $OS_VERSION"

MAJOR_VERSION=$(echo $OS_VERSION | cut -d. -f1)
if [ "$MAJOR_VERSION" -lt 11 ]; then
    print_warning "macOS 11 (Big Sur) or later recommended. You have: $OS_VERSION"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Installation aborted"
        exit 1
    fi
else
    print_status "macOS version compatible"
fi

# Check available disk space
DISK_SPACE=$(df -h "$SCRIPT_DIR" | awk 'NR==2 {print $4}')
print_info "Available disk space: $DISK_SPACE"

# Check/Install Homebrew
print_header "Homebrew Package Manager"

if command -v brew &> /dev/null; then
    BREW_VERSION=$(brew --version | head -n1)
    print_status "Homebrew already installed: $BREW_VERSION"
else
    print_warning "Homebrew not found - required for dependency management"
    read -p "Install Homebrew now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        print_status "Homebrew installed successfully"
    else
        print_error "Homebrew is required. Installation aborted."
        exit 1
    fi
fi

# Check/Install Python 3
print_header "Python 3"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python 3 already installed: $PYTHON_VERSION"

    # Check if Python version is adequate (3.8+)
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
    if [ "$PYTHON_MINOR" -lt 8 ]; then
        print_warning "Python 3.8+ recommended. Upgrading..."
        brew upgrade python3
        print_status "Python 3 upgraded"
    fi
else
    print_warning "Python 3 not found - installing via Homebrew..."
    brew install python3
    print_status "Python 3 installed successfully"
fi

# Check pip3
if command -v pip3 &> /dev/null; then
    print_status "pip3 available"
else
    print_error "pip3 not found. Please install Python 3 properly."
    exit 1
fi

# Install Python dependencies
# Homebrew's Python refuses system-wide pip installs (PEP 668, "externally-managed-environment"),
# so dependencies live in a project virtualenv (venv/, gitignored). run.sh uses it automatically.
print_header "Python Dependencies"

cd "$SCRIPT_DIR"

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found in $SCRIPT_DIR"
    exit 1
fi

if [ -x "venv/bin/python3" ]; then
    print_status "Virtual environment already exists: venv/"
else
    print_info "Creating virtual environment in venv/ ..."
    python3 -m venv venv
    print_status "Virtual environment created"
fi

print_info "Installing dependencies from requirements.txt (Flask, pytest, beautifulsoup4)..."
venv/bin/python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt
print_status "Dependencies installed: Flask $(venv/bin/python3 -c 'from importlib.metadata import version; print(version("flask"))'), pytest $(venv/bin/python3 -c 'import pytest; print(pytest.__version__)'), beautifulsoup4 $(venv/bin/python3 -c 'from importlib.metadata import version; print(version("beautifulsoup4"))')"

# Database Setup
print_header "Database Setup"

if [ -d "$SCRIPT_DIR/db" ]; then
    print_status "Database directory exists"

    # Check for existing databases
    if [ -f "$SCRIPT_DIR/db/readathon_registry.db" ]; then
        print_status "Registry database found: readathon_registry.db"
    fi

    # Year databases (readathon_2025.db, readathon_2026.db, ...) are gitignored - they exist only locally
    for YEAR_DB in "$SCRIPT_DIR"/db/readathon_[0-9][0-9][0-9][0-9].db; do
        if [ -f "$YEAR_DB" ]; then
            print_status "Contest database found: $(basename "$YEAR_DB")"
        fi
    done

    if [ -f "$SCRIPT_DIR/db/readathon_sample.db" ]; then
        print_status "Sample database found: readathon_sample.db"
    else
        print_warning "Sample database not found - restore it with: git checkout db/readathon_sample.db"
    fi
else
    print_warning "Database directory not found - restore it with: git checkout db/"
fi

print_info "To create a new year's database: Admin -> Database Registry -> Create New Database"
print_info "  (or from the command line: venv/bin/python3 init_data.py <year>)"

# Desktop shortcuts are generated files: rewrite them whenever they don't match
# this install (e.g. an old copy pointing to a different folder), so reruns fix them.
print_header "Desktop Shortcuts"

DESKTOP_DIR="$HOME/Desktop"

# install_shortcut <file> <description> <content>
install_shortcut() {
    local file="$1" desc="$2" content="$3"
    local name
    name="$(basename "$file")"
    if [ -f "$file" ] && [ "$(cat "$file")" == "$content" ]; then
        print_status "$name is up to date ($desc)"
    else
        if [ -f "$file" ]; then
            print_warning "$name was out of date - replacing it. Old version:"
            sed 's/^/      /' "$file"
        fi
        printf '%s\n' "$content" > "$file"
        print_status "$name written to Desktop ($desc)"
    fi
    if [ ! -x "$file" ]; then
        chmod +x "$file"
        print_status "$name made executable"
    fi
}

if [ -d "$DESKTOP_DIR" ]; then
    install_shortcut "$DESKTOP_DIR/Start Read-a-Thon.command" \
        "runs ./run.sh in $SCRIPT_DIR" \
        "#!/bin/bash
cd \"$SCRIPT_DIR\"
./run.sh"

    install_shortcut "$DESKTOP_DIR/Stop Read-a-Thon.command" \
        "stops the app on port 5001" \
        "#!/bin/bash
echo \"🛑 Stopping Read-a-Thon Application...\"
lsof -ti:5001 | xargs kill -9 2>/dev/null
echo \"✅ Application stopped\"
sleep 2"

    # Report (but don't touch) other Read-a-Thon shortcuts, e.g. from older versions
    for OTHER in "$DESKTOP_DIR"/*[Rr]ead*[Tt]hon*.command; do
        case "$(basename "$OTHER")" in
            "Start Read-a-Thon.command"|"Stop Read-a-Thon.command") ;;
            *) [ -f "$OTHER" ] && print_warning "Other shortcut found (not managed by this installer, delete it if unused): $(basename "$OTHER")" ;;
        esac
    done
else
    print_warning "Desktop directory not found - skipping shortcuts"
fi

# Validate Installation
print_header "Installation Validation"

print_info "Running validation checks..."

# Test 1: Python imports
if venv/bin/python3 -c "import flask, pytest, bs4" 2>/dev/null; then
    print_status "Python dependencies working"
else
    print_error "Python dependency import failed"
    exit 1
fi

# Test 2: Database access
if [ -f "$SCRIPT_DIR/db/readathon_sample.db" ]; then
    if python3 -c "import sqlite3; sqlite3.connect('$SCRIPT_DIR/db/readathon_sample.db').close()" 2>/dev/null; then
        print_status "Database access working"
    else
        print_error "Database access failed"
        exit 1
    fi
fi

# Test 3: Check critical files
CRITICAL_FILES=("app.py" "database.py" "queries.py" "templates/base.html")
ALL_FILES_PRESENT=true

for file in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        print_error "Critical file missing: $file"
        ALL_FILES_PRESENT=false
    fi
done

if $ALL_FILES_PRESENT; then
    print_status "All critical files present"
else
    print_error "Some critical files are missing"
    exit 1
fi

# Final Summary
print_header "Installation Summary"

echo ""
if $EXISTING_INSTALL; then
    echo -e "${GREEN}${CHECK} Existing installation validated and updated${NC}"
    echo -e "   Version: ${BLUE}$CURRENT_VERSION${NC}"
else
    echo -e "${GREEN}${CHECK} Fresh installation completed successfully${NC}"
fi

echo ""
echo -e "${BLUE}Installation Location:${NC} $SCRIPT_DIR"
echo "(Safe to rerun ./install.sh anytime - it re-checks everything and fixes outdated Desktop shortcuts.)"
echo ""
echo -e "${BLUE}Quick Start:${NC}"
echo "  1. Double-click 'Start Read-a-Thon.command' on Desktop"
echo "  2. Open browser: http://127.0.0.1:5001"
echo "  3. To stop: Double-click 'Stop Read-a-Thon.command'"
echo ""
echo -e "${BLUE}Manual Start:${NC}"
echo "  cd $SCRIPT_DIR"
echo "  ./run.sh                               # last database you used"
echo "  ./run.sh --db sample                   # sample data"
echo "  ./run.sh --db \"2026 Read-a-Thon\"        # a specific year"
echo ""
echo -e "${BLUE}Run Tests:${NC}"
echo "  cd $SCRIPT_DIR"
echo "  venv/bin/pytest"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  • User Manual: Open app → Help menu → User Manual"
echo "  • Installation Guide: Open app → Help menu → Installation Guide"
echo "  • README: $SCRIPT_DIR/README.md"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${ROCKET}  Installation Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

exit 0
