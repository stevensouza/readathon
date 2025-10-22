# Feature 26: File Upload Validation 🛡️ HIGH PRIORITY

**[← Back to Index](../00-INDEX.md)**

---

### Feature 26: File Upload Validation 🛡️ HIGH PRIORITY
**Feature:** Comprehensive file validation before uploads to prevent uploading wrong file types.

**Status:** ✅ **CORE FUNCTIONALITY COMPLETE** - File type detection and rejection implemented
- Daily upload rejects cumulative files (checks for Raised & Sponsors columns)
- Cumulative upload rejects daily files (checks for missing Raised & Sponsors)
- Column detection with case-insensitive matching (`_detect_columns()` method)
- Clear error messages indicating correct upload section

**Optional Enhancements Not Yet Implemented:**
- Client-side validation endpoint (`/api/validate_upload`)
- Preview validation before upload
- Success messages showing detected columns
- Row count preview

**Problem Being Solved:**
- User accidentally uploads Daily Minutes file using Cumulative Stats uploader
- System accepts invalid file, corrupts data
- No early warning about column mismatches
- Difficult to recover from wrong upload

**Requirements:**

**A. Column Specifications:**
Define required and optional columns for each upload type:

```python
UPLOAD_SPECS = {
    'daily': {
        'required': ['student_name', 'class_name', 'minutes_read'],
        'optional': ['log_date', 'teacher_name', 'grade_level', 'team_name'],
        'display_name': 'Daily Minutes'
    },
    'cumulative': {
        'required': ['student_name', 'donation_amount', 'sponsors', 'cumulative_minutes'],
        'optional': ['class_name', 'teacher_name', 'team_name', 'grade_level'],
        'display_name': 'Cumulative Stats'
    },
    'roster': {
        'required': ['student_name', 'class_name', 'teacher_name', 'grade_level'],
        'optional': ['team_name', 'student_id'],
        'display_name': 'Roster'
    },
    'class_info': {
        'required': ['class_name', 'teacher_name', 'grade_level'],
        'optional': ['team_name', 'room_number'],
        'display_name': 'Class Info'
    },
    'grade_rules': {
        'required': ['grade_level', 'min_daily_minutes'],
        'optional': ['max_daily_minutes', 'description'],
        'display_name': 'Grade Rules'
    }
}
```

**B. Validation Function:**
```python
def validate_upload_file(file_path, upload_type):
    """
    Validate CSV file has correct columns for upload type.

    Returns:
        dict with keys:
        - valid: bool (True if all required columns present)
        - errors: list of error messages
        - warnings: list of warning messages
        - missing_required: list of missing required columns
        - unknown_columns: list of unexpected columns
        - suggested_type: str (guessed correct upload type if wrong)
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'missing_required': [],
        'unknown_columns': [],
        'suggested_type': None
    }

    # Read CSV headers only (don't load entire file)
    df = pd.read_csv(file_path, nrows=0)
    file_columns = set(df.columns)

    spec = UPLOAD_SPECS[upload_type]
    required = set(spec['required'])
    optional = set(spec['optional'])
    expected = required.union(optional)

    # Check 1: Missing required columns
    missing = required - file_columns
    if missing:
        result['valid'] = False
        result['missing_required'] = list(missing)
        result['errors'].append(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

        # Try to guess correct file type
        suggested = guess_upload_type(file_columns)
        if suggested and suggested != upload_type:
            result['suggested_type'] = suggested
            result['errors'].append(
                f"This appears to be a {UPLOAD_SPECS[suggested]['display_name']} file. "
                f"Please use the {UPLOAD_SPECS[suggested]['display_name']} upload instead."
            )

    # Check 2: Unknown/unexpected columns
    unknown = file_columns - expected
    if unknown:
        result['unknown_columns'] = list(unknown)
        result['warnings'].append(
            f"File contains unexpected columns (will be ignored): {', '.join(sorted(unknown))}"
        )

    return result

def guess_upload_type(file_columns):
    """Try to guess what type of file this is based on columns"""
    file_columns = set(file_columns)

    # Check each upload type to see if all required columns are present
    for upload_type, spec in UPLOAD_SPECS.items():
        required = set(spec['required'])
        if required.issubset(file_columns):
            return upload_type

    return None
```

**C. Validation Endpoint:**
Add new API endpoint for client-side validation:

```python
@app.route('/api/validate_upload', methods=['POST'])
def validate_upload():
    """Validate uploaded file before processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    upload_type = request.form.get('upload_type')

    if not upload_type or upload_type not in UPLOAD_SPECS:
        return jsonify({'error': 'Invalid upload type'}), 400

    # Save to temp location
    temp_path = tempfile.mktemp(suffix='.csv')
    file.save(temp_path)

    try:
        # Validate
        validation_result = validate_upload_file(temp_path, upload_type)
        return jsonify(validation_result)
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

**D. Client-Side Integration (JavaScript):**
Update upload page to validate before upload:

```javascript
// Add to upload.html
async function validateBeforeUpload(fileInput, uploadType) {
    const file = fileInput.files[0];
    if (!file) return false;

    // Show loading indicator
    showValidationSpinner();

    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_type', uploadType);

    try {
        const response = await fetch('/api/validate_upload', {
            method: 'POST',
            body: formData
        });

        const validation = await response.json();
        hideValidationSpinner();

        // Show validation results
        if (!validation.valid) {
            showValidationError(validation.errors);
            return false;
        }

        if (validation.warnings.length > 0) {
            return await showValidationWarning(validation.warnings);
        }

        return true;

    } catch (error) {
        hideValidationSpinner();
        showValidationError(['Failed to validate file. Please try again.']);
        return false;
    }
}

function showValidationError(errors) {
    const html = `
        <div class="alert alert-danger alert-dismissible fade show">
            <h5><i class="bi bi-exclamation-triangle"></i> File Validation Failed</h5>
            <ul>
                ${errors.map(err => `<li>${err}</li>`).join('')}
            </ul>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.getElementById('validation-messages').innerHTML = html;
}

async function showValidationWarning(warnings) {
    const message = `
        File validation successful, but contains unexpected columns:\n\n
        ${warnings.join('\n\n')}

        These columns will be ignored during upload.

        Do you want to proceed?
    `;

    return confirm(message);
}

// Update upload button handlers
document.getElementById('daily-upload-btn').addEventListener('click', async function(e) {
    e.preventDefault();

    const fileInput = document.getElementById('daily-file');
    const isValid = await validateBeforeUpload(fileInput, 'daily');

    if (isValid) {
        // Proceed with original upload logic
        uploadDailyMinutes();
    }
});

document.getElementById('cumulative-upload-btn').addEventListener('click', async function(e) {
    e.preventDefault();

    const fileInput = document.getElementById('cumulative-file');
    const isValid = await validateBeforeUpload(fileInput, 'cumulative');

    if (isValid) {
        // Proceed with original upload logic
        uploadCumulativeStats();
    }
});
```

**E. Enhanced Upload UI:**
Add validation message area to upload page:

```html
<!-- Add to templates/upload.html -->
<div class="container mt-4">
    <!-- Validation Messages Area (shared) -->
    <div id="validation-messages" class="mb-3"></div>

    <div class="row">
        <!-- Daily Upload Column -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Daily Minutes Upload</h5>
                </div>
                <div class="card-body">
                    <!-- File input -->
                    <input type="file" id="daily-file" accept=".csv">

                    <!-- Expected columns help text -->
                    <small class="text-muted d-block mt-2">
                        <strong>Required columns:</strong> student_name, class_name, minutes_read
                        <br>
                        <strong>Optional columns:</strong> log_date, teacher_name, grade_level
                    </small>

                    <button id="daily-upload-btn" class="btn btn-primary mt-3">
                        <span class="spinner-border spinner-border-sm d-none" id="daily-spinner"></span>
                        Upload Daily Minutes
                    </button>
                </div>
            </div>
        </div>

        <!-- Cumulative Upload Column -->
        <div class="col-md-6">
            <!-- Similar structure -->
        </div>
    </div>
</div>
```

**F. Validation Messages - Examples:**

**Example 1: Wrong File Type**
```
❌ File Validation Failed

• Missing required columns: donation_amount, sponsors, cumulative_minutes

This appears to be a Daily Minutes file. Please use the Daily Minutes upload instead.
```

**Example 2: Unknown Columns**
```
⚠️ File Validation Warning

File contains unexpected columns (will be ignored):
• internal_id
• processing_timestamp
• exported_date

These columns are not recognized and will be ignored during upload.

Do you want to proceed?
[Cancel] [Proceed Anyway]
```

**Example 3: Success**
```
✓ File Validation Successful

Found all required columns:
• student_name
• donation_amount
• sponsors
• cumulative_minutes

Optional columns found:
• class_name
• teacher_name

Ready to upload 245 rows.
```

**G. Server-Side Validation (Defense in Depth):**
Even after client-side validation, validate again server-side before processing:

```python
def upload_daily_minutes(file_path, log_date):
    """Upload daily minutes with validation"""

    # Validate file structure first
    validation = validate_upload_file(file_path, 'daily')
    if not validation['valid']:
        raise ValueError(f"Invalid file: {', '.join(validation['errors'])}")

    # Proceed with upload
    df = pd.read_csv(file_path)

    # Use only expected columns (ignore unknown)
    expected_columns = UPLOAD_SPECS['daily']['required'] + UPLOAD_SPECS['daily']['optional']
    df = df[[col for col in df.columns if col in expected_columns]]

    # Rest of upload logic...
```

**Implementation Priority:** 🔴 HIGH
- Prevents data corruption from wrong uploads
- Saves significant cleanup/recovery time
- Low implementation effort, high value

**Testing Scenarios:**
- [ ] Upload correct Daily file to Daily uploader → Success
- [ ] Upload Daily file to Cumulative uploader → Error with suggestion
- [ ] Upload Cumulative file to Daily uploader → Error with suggestion
- [ ] Upload file with extra unknown columns → Warning, allow proceed
- [ ] Upload file missing required columns → Error, block upload
- [ ] Upload file with both missing and extra columns → Show both issues

**Files to Modify:**
- `database.py` - Add validation functions
- `app.py` - Add `/api/validate_upload` endpoint
- `templates/upload.html` - Add validation UI and JavaScript
- Update existing upload functions to use validation

---



---

**[← Back to Index](../00-INDEX.md)**
