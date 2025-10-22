# Read-a-Thon System Development

## 📋 IMPORTANT: Before Starting Any Work
1. **READ** `/IMPLEMENTATION_PROMPT.md` - This is the SOURCE OF TRUTH for all requirements
2. Check which features are marked as completed (✓) vs. pending
3. Confirm requirements with user before implementing
4. Update IMPLEMENTATION_PROMPT.md if requirements change during work

## When Compacting Conversations
- IMPLEMENTATION_PROMPT.md must be preserved
- Reference it in summary: "See IMPLEMENTATION_PROMPT.md for complete requirements"
- Include link to this file in summary

## Session Startup Protocol
1. Read IMPLEMENTATION_PROMPT.md
2. Ask user: "Is IMPLEMENTATION_PROMPT.md up to date, or have requirements changed?"
3. Confirm which feature to work on
4. Proceed with implementation

## Development Directories
- `/v2026_development` - Active development for 2026 enhancements
- `/v2025_stable` - Stable 2025 production version
- Desktop - Contains sample/test data files

## Key Files
- `IMPLEMENTATION_PROMPT.md` - Complete requirements documentation
- `database.py` - Database layer (SQLite operations)
- `app.py` - Flask application (routes, API endpoints)
- `templates/` - Jinja2 HTML templates
- `static/` - CSS, JS, images

## Running the Application
```bash
cd ~/my/data/readathon/v2026_development
python3 app.py
```
Access at: http://localhost:5000

## Testing
- Automated tests in `test_*.py` files
- Manual testing checklist in IMPLEMENTATION_PROMPT.md
- Use sample data from Desktop for testing
