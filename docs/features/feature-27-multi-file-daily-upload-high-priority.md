# Feature 27: Multi-File Daily Upload 📁 HIGH PRIORITY

**[← Back to Index](../00-INDEX.md)**

---

### Feature 27: Multi-File Daily Upload 📁 HIGH PRIORITY
**Feature:** Upload multiple daily report files simultaneously with automatic date extraction from filenames.

**Status:** ✅ COMPLETED - Multi-file upload with date extraction, preview table, and batch processing implemented

**Modifications from Original Requirements:**
1. **No confirmation prompts** - Re-uploading same date automatically replaces data (like cumulative upload behavior)
2. **Audit trail added** - All uploads tracked in Upload_History with detailed audit information (see Feature 28)
3. **Two deletion concepts** implemented:
   - **Data deletion** (Daily_Logs) - automatic during re-upload via ON CONFLICT DO UPDATE
   - **History deletion** (Upload_History audit records) - manual only via UI checkboxes
4. **Upload_History records are permanent** - Only manually deletable for complete audit trail

**Problem Being Solved:**
- Parents can enter data for previous days at any time
- Workflow requires re-uploading all previous days' files daily
- By day 10, user must upload 10 separate files (one at a time)
- Current system only supports single file upload
- Manual, time-consuming process prone to errors

**Requirements:**

**A. Multiple File Selection:**
```html
<!-- Upload page daily section -->
<div class="card">
    <div class="card-header">
        <h5>Daily Minutes Upload</h5>
    </div>
    <div class="card-body">
        <input type="file"
               id="daily-files"
               accept=".csv"
               multiple
               onchange="previewDailyFiles()">

        <small class="text-muted d-block mt-2">
            Select multiple CSV files to upload at once.
            Dates will be extracted from filenames automatically.
        </small>

        <!-- Preview Table (appears after file selection) -->
        <div id="file-preview" class="mt-3" style="display: none;">
            <h6>Files to Upload (Ready to upload: <span id="upload-count">0</span> of <span id="total-count">0</span>)</h6>

            <!-- Bulk Actions -->
            <div class="btn-group mb-2" role="group">
                <button type="button" class="btn btn-sm btn-outline-primary" onclick="selectAllFiles()">
                    Select All
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="deselectAllFiles()">
                    Deselect All
                </button>
            </div>

            <table class="table table-sm table-bordered">
                <thead>
                    <tr>
                        <th style="width: 50px;">
                            <input type="checkbox" id="select-all-checkbox"
                                   onchange="toggleAllCheckboxes()"
                                   checked>
                        </th>
                        <th>Filename</th>
                        <th>Extracted Date</th>
                        <th style="width: 150px;">Override Date</th>
                        <th style="width: 100px;">Status</th>
                    </tr>
                </thead>
                <tbody id="file-preview-tbody">
                    <!-- Populated by JavaScript -->
                </tbody>
            </table>

            <button id="upload-multiple-btn" class="btn btn-primary" onclick="uploadMultipleFiles()">
                Upload Selected Files
            </button>
        </div>
    </div>
</div>
```

**B. Filename Pattern & Date Extraction:**

**Pattern:** `Donations+Report+For+2025-10-09+-+Readathon+68289 (1).csv`

**Extraction Logic:**
```javascript
function extractDateFromFilename(filename) {
    // Pattern: Look for YYYY-MM-DD format anywhere in filename
    const datePattern = /(\d{4})-(\d{2})-(\d{2})/;
    const match = filename.match(datePattern);

    if (match) {
        const year = match[1];
        const month = match[2];
        const day = match[3];

        // Validate date is reasonable
        const date = new Date(year, month - 1, day);
        if (date && date.getFullYear() == year) {
            return `${year}-${month}-${day}`;
        }
    }

    return null; // Date not found or invalid
}
```

**C. File Preview Table (JavaScript):**
```javascript
function previewDailyFiles() {
    const fileInput = document.getElementById('daily-files');
    const files = fileInput.files;

    if (files.length === 0) {
        document.getElementById('file-preview').style.display = 'none';
        return;
    }

    const tbody = document.getElementById('file-preview-tbody');
    tbody.innerHTML = '';

    let readyCount = 0;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const extractedDate = extractDateFromFilename(file.name);
        const hasDate = extractedDate !== null;

        if (hasDate) readyCount++;

        const row = document.createElement('tr');
        row.className = hasDate ? '' : 'table-warning';
        row.dataset.fileIndex = i;

        row.innerHTML = `
            <td class="text-center">
                <input type="checkbox"
                       class="file-checkbox"
                       data-file-index="${i}"
                       ${hasDate ? 'checked' : ''}
                       onchange="updateUploadCount()">
            </td>
            <td>
                <small>${file.name}</small>
            </td>
            <td class="text-center">
                ${hasDate
                    ? `<span class="badge bg-success">${extractedDate}</span>`
                    : `<span class="badge bg-warning text-dark">Not found</span>`}
            </td>
            <td>
                <input type="date"
                       class="form-control form-control-sm date-override"
                       data-file-index="${i}"
                       value="${extractedDate || ''}"
                       ${!hasDate ? 'required' : ''}>
            </td>
            <td class="text-center">
                <span class="status-badge" data-file-index="${i}">
                    ${hasDate
                        ? '<span class="badge bg-secondary">Ready</span>'
                        : '<span class="badge bg-warning text-dark">Need Date</span>'}
                </span>
            </td>
        `;

        tbody.appendChild(row);
    }

    // Update counters
    document.getElementById('total-count').textContent = files.length;
    document.getElementById('upload-count').textContent = readyCount;

    // Show duplicate date warning
    checkDuplicateDates();

    // Show preview
    document.getElementById('file-preview').style.display = 'block';
}

function updateUploadCount() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    const checked = Array.from(checkboxes).filter(cb => cb.checked);
    document.getElementById('upload-count').textContent = checked.length;
}

function toggleAllCheckboxes() {
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const fileCheckboxes = document.querySelectorAll('.file-checkbox');

    fileCheckboxes.forEach(cb => {
        cb.checked = selectAllCheckbox.checked;
    });

    updateUploadCount();
}

function selectAllFiles() {
    document.querySelectorAll('.file-checkbox').forEach(cb => cb.checked = true);
    document.getElementById('select-all-checkbox').checked = true;
    updateUploadCount();
}

function deselectAllFiles() {
    document.querySelectorAll('.file-checkbox').forEach(cb => cb.checked = false);
    document.getElementById('select-all-checkbox').checked = false;
    updateUploadCount();
}

function checkDuplicateDates() {
    const dateInputs = document.querySelectorAll('.date-override');
    const dates = Array.from(dateInputs).map(input => input.value).filter(d => d);
    const duplicates = dates.filter((date, index) => dates.indexOf(date) !== index);

    if (duplicates.length > 0) {
        const warningDiv = document.getElementById('duplicate-warning') ||
                          createDuplicateWarning();
        warningDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i>
                <strong>Warning:</strong> Multiple files have the same date: ${[...new Set(duplicates)].join(', ')}
                <br>
                Later uploads will overwrite earlier ones for the same date.
            </div>
        `;
        warningDiv.style.display = 'block';
    }
}
```

**D. Upload Logic (Sequential with Progress):**
```javascript
async function uploadMultipleFiles() {
    const fileInput = document.getElementById('daily-files');
    const files = fileInput.files;
    const checkboxes = document.querySelectorAll('.file-checkbox:checked');

    if (checkboxes.length === 0) {
        alert('No files selected for upload.');
        return;
    }

    // Disable upload button
    const uploadBtn = document.getElementById('upload-multiple-btn');
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Uploading...';

    let successCount = 0;
    let errorCount = 0;
    const results = [];

    // Upload files sequentially (one at a time)
    for (const checkbox of checkboxes) {
        const fileIndex = checkbox.dataset.fileIndex;
        const file = files[fileIndex];
        const dateInput = document.querySelector(`.date-override[data-file-index="${fileIndex}"]`);
        const logDate = dateInput.value;

        if (!logDate) {
            errorCount++;
            updateFileStatus(fileIndex, 'error', 'Missing date');
            results.push({file: file.name, status: 'error', message: 'Missing date'});
            continue;
        }

        // Update status to "uploading"
        updateFileStatus(fileIndex, 'uploading', 'Uploading...');

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('log_date', logDate);

            const response = await fetch('/upload_daily', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                successCount++;
                updateFileStatus(fileIndex, 'success', `✓ ${result.rows_added || 0} rows`);
                results.push({file: file.name, status: 'success', rows: result.rows_added});
            } else {
                errorCount++;
                updateFileStatus(fileIndex, 'error', result.error || 'Upload failed');
                results.push({file: file.name, status: 'error', message: result.error});
            }

        } catch (error) {
            errorCount++;
            updateFileStatus(fileIndex, 'error', 'Network error');
            results.push({file: file.name, status: 'error', message: error.message});
        }
    }

    // Show summary
    showUploadSummary(successCount, errorCount, results);

    // Re-enable button
    uploadBtn.disabled = false;
    uploadBtn.innerHTML = 'Upload Selected Files';

    // Refresh page data if any succeeded
    if (successCount > 0) {
        setTimeout(() => location.reload(), 2000);
    }
}

function updateFileStatus(fileIndex, status, message) {
    const statusBadge = document.querySelector(`.status-badge[data-file-index="${fileIndex}"]`);
    const row = document.querySelector(`tr[data-file-index="${fileIndex}"]`);

    if (status === 'uploading') {
        statusBadge.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Uploading...';
        row.classList.add('table-info');
    } else if (status === 'success') {
        statusBadge.innerHTML = `<span class="badge bg-success">${message}</span>`;
        row.classList.remove('table-info');
        row.classList.add('table-success');
    } else if (status === 'error') {
        statusBadge.innerHTML = `<span class="badge bg-danger">${message}</span>`;
        row.classList.remove('table-info');
        row.classList.add('table-danger');
    }
}

function showUploadSummary(successCount, errorCount, results) {
    const summary = document.createElement('div');
    summary.className = 'alert alert-info alert-dismissible fade show mt-3';
    summary.innerHTML = `
        <h5>Upload Complete</h5>
        <p>
            <strong>Success:</strong> ${successCount} file(s) uploaded<br>
            <strong>Errors:</strong> ${errorCount} file(s) failed
        </p>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.getElementById('file-preview').insertBefore(
        summary,
        document.getElementById('upload-multiple-btn')
    );
}
```

**E. Server-Side Changes:**

**Modify existing `/upload_daily` endpoint:**
```python
@app.route('/upload_daily', methods=['POST'])
def upload_daily():
    """Upload daily minutes (single or part of multi-file upload)"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        log_date = request.form.get('log_date')

        if not log_date:
            return jsonify({'success': False, 'error': 'No date provided'}), 400

        # Validate file first (Feature 26)
        temp_path = tempfile.mktemp(suffix='.csv')
        file.save(temp_path)

        validation = validate_upload_file(temp_path, 'daily')
        if not validation['valid']:
            os.remove(temp_path)
            return jsonify({
                'success': False,
                'error': '; '.join(validation['errors'])
            }), 400

        # Upload to database
        db = get_current_db()
        result = db.upload_daily_minutes(temp_path, log_date)

        # Clean up
        os.remove(temp_path)

        return jsonify({
            'success': True,
            'rows_added': result.get('rows_added', 0),
            'message': f"Successfully uploaded {result.get('rows_added', 0)} rows for {log_date}"
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**F. UI Improvements:**

**Checkbox vs "Skip" Button - RECOMMENDED APPROACH:**
- ✅ **Use checkboxes (default checked)**
- Reasons:
  1. More intuitive - checked = will upload
  2. Clear visual state at a glance
  3. Allows bulk selection controls (Select All / Deselect All)
  4. Standard UI pattern users expect
  5. Less clicking required to exclude files
  6. Easier keyboard navigation

**Additional Features:**
1. **Duplicate Date Detection** - Warn if multiple files have same date
2. **Validation Preview** - Show estimated records per file
3. **Progress Indicator** - Visual feedback during batch upload
4. **Upload Summary** - Show success/error counts after completion
5. **Status Badges** - Color-coded status for each file (Ready/Uploading/Success/Error)
6. **Bulk Actions** - Select All / Deselect All buttons
7. **Upload Count** - "Ready to upload X of Y files"
8. **Missing Date Warning** - Highlight files without extractable dates (yellow row)
9. **Date Override** - Allow manual date entry for each file
10. **Sequential Upload** - Upload one at a time with clear progress

**G. Visual Design:**

**Row States:**
- **Default (white):** File ready, date extracted successfully, checkbox checked
- **Warning (yellow):** Date not extracted, needs manual date entry
- **Info (light blue):** Currently uploading
- **Success (light green):** Upload completed successfully
- **Error (light red):** Upload failed
- **Grayed (unchecked):** File deselected, will not upload

**Example Preview Table:**
```
┌───┬─────────────────────────────────┬──────────────┬──────────────┬─────────┐
│ ☑ │ Filename                        │ Extract Date │ Override     │ Status  │
├───┼─────────────────────────────────┼──────────────┼──────────────┼─────────┤
│ ☑ │ Donations+...+2025-10-06.csv   │ 2025-10-06   │ [2025-10-06] │ Ready   │
│ ☑ │ Donations+...+2025-10-07.csv   │ 2025-10-07   │ [2025-10-07] │ Ready   │
│ ☑ │ Donations+...+2025-10-08.csv   │ 2025-10-08   │ [2025-10-08] │ Ready   │
│ ☐ │ Donations+...+2025-10-09.csv   │ 2025-10-09   │ [2025-10-09] │ Ready   │
│ ☑ │ some_old_file.csv              │ Not found    │ [required]   │ Need Dt │
└───┴─────────────────────────────────┴──────────────┴──────────────┴─────────┘

[Select All] [Deselect All]          Ready to upload 4 of 5 files

[Upload Selected Files]
```

**Implementation Priority:** 🔴 HIGH
- Saves significant time during daily workflow
- Reduces human error (forgetting to upload a file)
- User is currently uploading 10+ files daily by end of campaign
- Major quality-of-life improvement

**Testing Scenarios:**
- [ ] Select 3 files with valid dates → All 3 upload successfully
- [ ] Select 5 files, uncheck 2 → Only 3 checked files upload
- [ ] Upload file without date in filename → User enters date manually
- [ ] Upload 2 files with same date → Warning shown, later overwrites earlier
- [ ] Upload fails for one file → Other files continue, error shown
- [ ] Select All / Deselect All → All checkboxes toggle correctly
- [ ] Upload counter → Shows correct count as checkboxes change

**Files to Modify:**
- `templates/upload.html` - Add multi-file UI, preview table, JavaScript
- `app.py` - Ensure `/upload_daily` endpoint supports multi-file workflow
- `static/js/upload.js` (optional) - Extract JavaScript to separate file

**Backward Compatibility:**
- Keep existing single-file upload working
- Multi-file is optional enhancement, not replacement
- Users can still upload one file at a time if preferred

---



---

**[← Back to Index](../00-INDEX.md)**
