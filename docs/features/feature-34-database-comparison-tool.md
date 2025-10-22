# Feature 34: Database Comparison Tool

**[← Back to Index](../00-INDEX.md)**

---

### Feature 34: Database Comparison Tool
**Requirement:** Compare metrics between two databases (e.g., 2025 vs 2026, prod vs demo, before vs after).

**Purpose:**
- Year-over-year comparison (2025 campaign vs 2026 campaign)
- Production vs demo/test data validation
- Before/after analysis when testing new features
- Historical trend analysis

**Use Cases:**

1. **Year-Over-Year Analysis:**
   - "How did 2026 compare to 2025?"
   - "Did participation improve from last year?"
   - "Which classes improved the most year-over-year?"

2. **Data Validation:**
   - "Does my demo database have realistic numbers compared to prod?"
   - "Did that data import work correctly?"

3. **What-If Scenarios:**
   - "What if we had 10% more participation?"
   - Compare actual results to projected/test scenarios

---

## Proposed UI Design

### A. Comparison Page Location
New tab or Admin section feature: **"Compare Databases"**

### B. Database Selection Interface

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Database Comparison Tool                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Compare:                                                │
│  ┌──────────────────────┐       ┌──────────────────────┐│
│  │ Database A           │  vs   │ Database B           ││
│  │                      │       │                      ││
│  │ ▼ readathon_2025.db │       │ ▼ readathon_2026.db ││
│  │   readathon_prod.db  │       │   readathon_prod.db  ││
│  │   readathon_sample.db│       │   readathon_sample.db││
│  │   readathon_demo.db  │       │   readathon_demo.db  ││
│  └──────────────────────┘       └──────────────────────┘│
│                                                          │
│  Label (optional):                                       │
│  [2025 Campaign      ]         [2026 Campaign      ]     │
│                                                          │
│  [Compare Databases]                                     │
└─────────────────────────────────────────────────────────┘
```

### C. Comparison Report Sections

#### **1. High-Level Metrics Comparison**

```
┌────────────────────────────────────────────────────────────────┐
│ Campaign Overview                                              │
├─────────────────┬──────────────┬──────────────┬───────────────┤
│ Metric          │ 2025         │ 2026         │ Δ Change      │
├─────────────────┼──────────────┼──────────────┼───────────────┤
│ Total Students  │ 405          │ 411          │ +6 (+1.5%)    │
│ Participation   │ 92.3%        │ 95.1%        │ +2.8pp ▲      │
│ Total Minutes   │ 245,680 min  │ 289,430 min  │ +43,750 (+18%)│
│ Avg Min/Student │ 606 min      │ 704 min      │ +98 (+16%)    │
│ Total Raised    │ $12,450      │ $15,220      │ +$2,770 (+22%)│
│ Avg Donation    │ $30.74       │ $37.03       │ +$6.29 (+20%) │
│ Goal Met (≥1d)  │ 85.4%        │ 88.7%        │ +3.3pp ▲      │
└─────────────────┴──────────────┴──────────────┴───────────────┘

Legend: pp = percentage points, ▲ = improvement, ▼ = decline
```

#### **2. Team Competition Comparison**

```
┌────────────────────────────────────────────────────────────────┐
│ Team Performance                                               │
├──────────┬──────────────┬──────────────┬──────────────────────┤
│ Team     │ 2025         │ 2026         │ Δ Change             │
├──────────┼──────────────┼──────────────┼──────────────────────┤
│ Kitsko   │ 125,340 min  │ 148,920 min  │ +23,580 (+18.8%)     │
│          │ (51.0%)      │ (51.4%)      │ +0.4pp               │
├──────────┼──────────────┼──────────────┼──────────────────────┤
│ Staub    │ 120,340 min  │ 140,510 min  │ +20,170 (+16.8%)     │
│          │ (49.0%)      │ (48.6%)      │ -0.4pp               │
└──────────┴──────────────┴──────────────┴──────────────────────┘
```

#### **3. Grade-Level Comparison**

```
┌────────────────────────────────────────────────────────────────┐
│ Grade Level Performance                                        │
├───────┬──────────────┬──────────────┬────────────────────────┤
│ Grade │ 2025 Avg Min │ 2026 Avg Min │ Δ Change               │
├───────┼──────────────┼──────────────┼────────────────────────┤
│ K     │ 420 min      │ 485 min      │ +65 (+15.5%) ▲         │
│ 1     │ 540 min      │ 620 min      │ +80 (+14.8%) ▲         │
│ 2     │ 615 min      │ 710 min      │ +95 (+15.4%) ▲         │
│ 3     │ 680 min      │ 780 min      │ +100 (+14.7%) ▲        │
│ 4     │ 720 min      │ 820 min      │ +100 (+13.9%) ▲        │
│ 5     │ 745 min      │ 805 min      │ +60 (+8.1%) ▲          │
└───────┴──────────────┴──────────────┴────────────────────────┘
```

#### **4. Top Performers Comparison**

```
┌────────────────────────────────────────────────────────────────┐
│ Top 10 Readers                                                 │
├─────┬──────────────────┬──────────────────┬───────────────────┤
│ Rank│ 2025             │ 2026             │ Notes             │
├─────┼──────────────────┼──────────────────┼───────────────────┤
│ #1  │ Sarah J: 2,880   │ Michael K: 3,120 │ New top reader    │
│ #2  │ Michael K: 2,760 │ Emma S: 3,005    │                   │
│ #3  │ Emma S: 2,650    │ Liam T: 2,940    │                   │
│ ... │ ...              │ ...              │                   │
└─────┴──────────────────┴──────────────────┴───────────────────┘
```

#### **5. Class Winners Comparison**

```
┌────────────────────────────────────────────────────────────────┐
│ Winning Classes by Grade                                       │
├───────┬─────────────────┬─────────────────┬──────────────────┤
│ Grade │ 2025 Winner     │ 2026 Winner     │ Change?          │
├───────┼─────────────────┼─────────────────┼──────────────────┤
│ K     │ Hansen (92%)  │ Hansen (95%)  │ Same (improved)  │
│ 1     │ Harper (89%)     │ Harrison (93%)      │ Different        │
│ 2     │ Harrison (91%)      │ Harrison (94%)      │ Same (improved)  │
│ 3     │ Stone (88%)     │ Evans (90%)     │ Different        │
│ 4     │ Evans (93%)     │ Evans (96%)     │ Same (improved)  │
│ 5     │ Henderson (87%)    │ Henry (91%)    │ Different        │
└───────┴─────────────────┴─────────────────┴──────────────────┘
```

---

## Implementation Details

### A. Backend (database.py)

```python
def compare_databases(self, db_path_a: str, db_path_b: str, label_a: str = None, label_b: str = None):
    """
    Compare metrics between two databases

    Args:
        db_path_a: Path to first database (e.g., 'readathon_2025.db')
        db_path_b: Path to second database (e.g., 'readathon_2026.db')
        label_a: Optional label for DB A (e.g., '2025 Campaign')
        label_b: Optional label for DB B (e.g., '2026 Campaign')

    Returns:
        dict with comparison data for all metrics
    """
    # Open both databases
    db_a = ReadathonDB(db_path_a)
    db_b = ReadathonDB(db_path_b)

    # Get metrics from both
    metrics_a = get_campaign_metrics(db_a)
    metrics_b = get_campaign_metrics(db_b)

    # Calculate deltas
    comparison = {
        'labels': {
            'a': label_a or db_path_a,
            'b': label_b or db_path_b
        },
        'overview': calculate_delta(metrics_a['overview'], metrics_b['overview']),
        'teams': calculate_delta(metrics_a['teams'], metrics_b['teams']),
        'grades': calculate_delta(metrics_a['grades'], metrics_b['grades']),
        'top_readers': compare_top_readers(db_a, db_b),
        'class_winners': compare_class_winners(db_a, db_b)
    }

    return comparison

def calculate_delta(values_a, values_b):
    """Calculate change between two sets of values"""
    deltas = {}
    for key in values_a.keys():
        a = values_a[key]
        b = values_b[key]

        # Calculate absolute and percentage change
        abs_change = b - a
        pct_change = ((b - a) / a * 100) if a != 0 else 0

        deltas[key] = {
            'a': a,
            'b': b,
            'abs_change': abs_change,
            'pct_change': pct_change,
            'direction': 'up' if abs_change > 0 else 'down' if abs_change < 0 else 'same'
        }

    return deltas
```

### B. Flask Route (app.py)

```python
@app.route('/compare_databases')
def compare_databases_page():
    """Database comparison page"""
    # Get list of all available databases
    db_files = [f for f in os.listdir('.') if f.endswith('.db') and f.startswith('readathon_')]

    return render_template('compare.html', databases=db_files)

@app.route('/api/compare', methods=['POST'])
def run_comparison():
    """Run database comparison"""
    db_a = request.form.get('db_a')
    db_b = request.form.get('db_b')
    label_a = request.form.get('label_a', '')
    label_b = request.form.get('label_b', '')

    if not db_a or not db_b:
        return jsonify({'error': 'Both databases must be specified'}), 400

    if db_a == db_b:
        return jsonify({'error': 'Cannot compare database to itself'}), 400

    # Run comparison
    db = get_current_db()
    comparison = db.compare_databases(db_a, db_b, label_a, label_b)

    return jsonify(comparison)
```

### C. Template (templates/compare.html)

```html
{% extends "base.html" %}

{% block title %}Compare Databases - Read-a-Thon System{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1 class="mb-4">
            <i class="bi bi-graph-up-arrow"></i> Database Comparison
        </h1>
    </div>
</div>

<!-- Database Selection -->
<div class="card mb-4">
    <div class="card-body">
        <div class="row">
            <div class="col-md-5">
                <label class="form-label fw-bold">Database A</label>
                <select class="form-select" id="db_a">
                    {% for db in databases %}
                    <option value="{{ db }}">{{ db }}</option>
                    {% endfor %}
                </select>
                <input type="text" class="form-control mt-2" id="label_a" placeholder="Label (e.g., '2025 Campaign')">
            </div>

            <div class="col-md-2 text-center d-flex align-items-center justify-content-center">
                <h3 class="text-muted">vs</h3>
            </div>

            <div class="col-md-5">
                <label class="form-label fw-bold">Database B</label>
                <select class="form-select" id="db_b">
                    {% for db in databases %}
                    <option value="{{ db }}">{{ db }}</option>
                    {% endfor %}
                </select>
                <input type="text" class="form-control mt-2" id="label_b" placeholder="Label (e.g., '2026 Campaign')">
            </div>
        </div>

        <div class="d-grid gap-2 mt-3">
            <button class="btn btn-primary btn-lg" onclick="runComparison()">
                <i class="bi bi-graph-up"></i> Compare Databases
            </button>
        </div>
    </div>
</div>

<!-- Comparison Results (populated by JavaScript) -->
<div id="comparisonResults" style="display: none;">
    <!-- Overview metrics -->
    <!-- Team comparison -->
    <!-- Grade comparison -->
    <!-- Top readers -->
    <!-- Class winners -->
</div>
{% endblock %}
```

---

## Metrics to Compare

### Core Metrics:
- Total students (roster count)
- Total reading minutes (capped)
- Average minutes per student
- Participation rate (% with any reading)
- Goal achievement rate (% meeting ≥1 day goal)
- Total fundraising
- Average donation per student
- Students with sponsors

### Team Metrics:
- Team total minutes
- Team participation rate
- Team average per student
- Winning team

### Grade Metrics:
- Students per grade
- Average minutes per grade
- Participation rate per grade
- Top performing grade

### Class Metrics:
- Winning class per grade
- Class participation rates
- Class average minutes

### Individual Metrics:
- Top 10 readers (with minutes)
- Top fundraisers
- Students who improved most (if comparing same roster)

---

## Advanced Features (Future)

### A. Multi-Database Comparison
Compare 3+ databases: 2024 vs 2025 vs 2026 trend analysis

### B. Visual Charts
- Line charts showing year-over-year trends
- Bar charts comparing grades/teams
- Pie charts for participation rates

### C. Export Comparison Report
- Export to CSV
- Generate PDF report
- Copy formatted comparison to clipboard

### D. Smart Insights
```
🎉 WINS:
- Participation increased by 2.8 percentage points
- Average minutes per student up 16%
- Grade 2 showed biggest improvement (+15.4%)

⚠️ AREAS FOR IMPROVEMENT:
- Grade 5 growth slowed (only +8.1%)
- Staub team lost ground to Kitsko (-0.4pp)
```

---

**Status:** NEW
**Priority:** Medium-High
**Type:** Analytics Feature
**Effort:** 2-3 sessions

**Dependencies:**
- Feature 35: Database Creation Tool (to create databases to compare)
- Multiple database support (already exists via Feature 16)

**Testing Scenarios:**
- [ ] Compare readathon_prod.db to readathon_sample.db
- [ ] Compare 2025 database to 2026 database
- [ ] Verify all delta calculations are correct
- [ ] Test with databases of different sizes
- [ ] Export comparison report

---

**[← Back to Index](../00-INDEX.md)**
