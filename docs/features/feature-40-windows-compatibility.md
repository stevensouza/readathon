# Feature 40: Windows Compatibility

**[← Back to Index](../00-INDEX.md)**

---

**Status:** FUTURE — not needed yet. The app has only been run on macOS.
**Priority:** Low until someone needs to run it on Windows; then High.
**Type:** Tooling / portability

---

## Why

Windows compatibility may become an issue later, for example if a volunteer or the PTA wants to run the app on a
Windows laptop. If that happens, fix the problems below and then take the further steps at the end.

## Where things stand (checked 2026-09-23, v2026.16.0)

**The app itself should mostly work on Windows.** Python, Flask, SQLite and Bootstrap (from a CDN) are cross-platform,
and file paths like `db/...` are accepted by Windows. The one known Python problem (date formats using `%-d`, which
Windows `strftime` doesn't support) was fixed in `scoreboards.py` in v2026.16.0.

**The tooling around the app is Mac-only:**

| Mac-only piece | What it does | Windows equivalent needed |
|---|---|---|
| `install.sh` | Creates `venv/`, installs `requirements.txt`, makes Desktop `.command` shortcuts | `install.bat` / PowerShell, or a cross-platform `install.py`; shortcuts as `.bat` or `.lnk` files |
| `run.sh` | Starts the app with `venv/bin/python3`, checks the port with `lsof`, opens the browser with `open` | `run.bat`: `venv\Scripts\python.exe app.py`, `start http://127.0.0.1:5001`, port check with `netstat` |
| `package_data.sh` | Zips `db/` to move data between computers | PowerShell `Compress-Archive`, or Python `zipfile` |
| `pre-commit.sh` | Runs page tests before a commit | Works under Git for Windows' bash; otherwise run `venv\Scripts\python -m pytest` |
| Docs | README, `templates/installation.html` and `CLAUDE.md` give Mac commands (`./run.sh`, `venv/bin/pytest`) | Add Windows equivalents |

**Workaround today (no changes):** install Python from python.org, then in the project folder:

```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python app.py
```

and open http://127.0.0.1:5001.

## What to do if Windows is needed

1. **Replace the bash scripts with small Python scripts** (`install.py`, `run.py`, `package_data.py`) that work on
   both systems; keep `run.sh` / `install.sh` as thin wrappers so the Mac workflow doesn't change.
2. **Add a GitHub Actions job running `pytest` on `windows-latest`** (and macOS), so portability problems like the
   `%-d` date format are caught automatically.
3. **Check for other Windows-only differences** while testing on a real Windows machine:
   - text files opened without `encoding=` use the Windows code page (cp1252) instead of UTF-8 (CSV uploads are
     already decoded as UTF-8; config and `VERSION` are plain ASCII);
   - emoji in startup `print()` messages in older Windows consoles;
   - Desktop shortcut creation and the "Copy as image" clipboard permission in Windows browsers.
4. **Update the docs** (README, Installation Guide, `CLAUDE.md`) with the Windows commands.
