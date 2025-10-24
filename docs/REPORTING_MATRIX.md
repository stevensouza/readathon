# Read-a-Thon Reporting Matrix & Gap Analysis

## Framework

**Metrics:**
- Donations (total $)
- Sponsors (count)
- Participation (% or count)
- Minutes - Goals Met (days met goal)
- Minutes - Capped (120/day max)
- Minutes - Actual (uncapped)
- Minutes - Max Single Day

**Entities:**
- School (totals)
- Team (Phoenix vs Dragons)
- Class (individual classrooms)
- Student (individual students)
- Grade Level (K-5)

**Reporting Periods:**
- Full Contest (all dates)
- By Specific Day (single date)
- Date Range (custom range)

**Result Types:**
- All Data (complete list)
- Top N (leaderboard)
- Single Number (summary stat)
- Breakdown (by category)

---

## Master Reporting Matrix

### 1. DONATIONS Reports

| Entity | Period | Result Type | Report Exists? | Query ID | Description | Gap? |
|--------|--------|-------------|----------------|----------|-------------|------|
| **School** | Full Contest | Single Number | ✅ YES | Dashboard | Total donations school-wide | - |
| **School** | By Day | Single Number | ❌ NO | - | Daily donation total | ⚠️ GAP |
| **Team** | Full Contest | All Data | ✅ YES | Q20 | Team donations breakdown | - |
| **Team** | Full Contest | Single Number | ✅ YES | Dashboard | Per-team donation totals | - |
| **Team** | By Day | Single Number | ❌ NO | - | Daily donations by team | ⚠️ GAP |
| **Class** | Full Contest | All Data | ❌ NO | - | All classes with donations | ⚠️ GAP |
| **Class** | Full Contest | Top N | ✅ YES | Q12/Q13 | Top fundraising classes (indirect) | - |
| **Class** | By Day | All Data | ❌ NO | - | Class donations by day | ⚠️ GAP |
| **Student** | Full Contest | All Data | ✅ YES | Q3/Q5 | All students with donations | - |
| **Student** | Full Contest | Top N | ✅ YES | Q5 (sorted) | Top fundraisers | - |
| **Student** | By Day | All Data | ❌ NO | - | Student donations by day | ⚠️ GAP |
| **Grade** | Full Contest | Top N | ✅ YES | Q9 | Most donations by grade | - |
| **Grade** | Full Contest | All Data | ❌ NO | - | All grades donation summary | ⚠️ GAP |

### 2. SPONSORS Reports

| Entity | Period | Result Type | Report Exists? | Query ID | Description | Gap? |
|--------|--------|-------------|----------------|----------|-------------|------|
| **School** | Full Contest | Single Number | ✅ YES | Dashboard | Total sponsors school-wide | - |
| **Team** | Full Contest | Breakdown | ✅ YES | Q20 | Sponsors by team | - |
| **Class** | Full Contest | All Data | ❌ NO | - | Sponsors by class | ⚠️ GAP |
| **Student** | Full Contest | All Data | ✅ YES | Q3/Q5 | All students with sponsors | - |
| **Student** | Full Contest | Top N | ✅ YES | Q5 (sorted) | Top sponsor count | - |
| **Grade** | Full Contest | Top N | ✅ YES | Q11 | Most sponsors by grade | - |

### 3. PARTICIPATION Reports

| Entity | Period | Result Type | Report Exists? | Query ID | Description | Gap? |
|--------|--------|-------------|----------------|----------|-------------|------|
| **School** | Full Contest | Single Number | ✅ YES | Dashboard | Overall participation % | - |
| **School** | By Day | Single Number | ❌ NO | - | Daily participation count | ⚠️ GAP |
| **Team** | Full Contest | Breakdown | ✅ YES | Q14 | Team participation rates | - |
| **Team** | By Day | Breakdown | ❌ NO | - | Daily team participation | ⚠️ GAP |
| **Class** | Full Contest | All Data | ✅ YES | Q6 | All classes participation | - |
| **Class** | Full Contest | Top N | ✅ YES | Q12/Q13 | Best participating classes | - |
| **Class** | By Day | All Data | ✅ YES | Q2 (by date) | Daily class participation | - |
| **Student** | Full Contest | All Data | ✅ YES | Q5/Q8 | All student participation | - |
| **Student** | Full Contest | Top N | ✅ YES | Q15 | Goal getters (perfect participation) | - |
| **Student** | By Day | All Data | ✅ YES | Q4 | Prize drawing (met goal on date) | - |
| **Grade** | Full Contest | All Data | ❌ NO | - | Participation by grade | ⚠️ GAP |

### 4. MINUTES (Goals Met) Reports

| Entity | Period | Result Type | Report Exists? | Query ID | Description | Gap? |
|--------|--------|-------------|----------------|----------|-------------|------|
| **School** | Full Contest | Single Number | ❌ NO | - | Total students who met goal all days | ⚠️ GAP |
| **Team** | Full Contest | Breakdown | ✅ YES | Q14 (indirect) | Goal getters by team | - |
| **Class** | Full Contest | All Data | ✅ YES | Q2 | Classes with goal achievement | - |
| **Student** | Full Contest | All Data | ✅ YES | Q15 | All goal getters | - |
| **Student** | Full Contest | Top N | ✅ YES | Q5 (sorted) | Top by days met goal | - |
| **Student** | By Day | All Data | ✅ YES | Q4 | Students who met goal on date | - |
| **Grade** | Full Contest | All Data | ❌ NO | - | Goal achievement by grade | ⚠️ GAP |

### 5. MINUTES (Capped 120/day) Reports

| Entity | Period | Result Type | Report Exists? | Query ID | Description | Gap? |
|--------|--------|-------------|----------------|----------|-------------|------|
| **School** | Full Contest | Single Number | ✅ YES | Dashboard | Total capped minutes | - |
| **School** | By Day | Single Number | ❌ NO | - | Daily capped minutes total | ⚠️ GAP |
| **Team** | Full Contest | Breakdown | ✅ YES | Q19 | Team minutes (capped) | - |
| **Team** | By Day | Breakdown | ❌ NO | - | Daily team minutes | ⚠️ GAP |
| **Class** | Full Contest | All Data | ✅ YES | Q2 | All classes total minutes | - |
| **Class** | Full Contest | Top N | ✅ YES | Q13 | Top reading classes | - |
| **Class** | By Day | All Data | ✅ YES | Q2 (by date) | Daily class minutes | - |
| **Student** | Full Contest | All Data | ✅ YES | Q5/Q8 | All student minutes | - |
| **Student** | Full Contest | Top N | ✅ YES | Q5 (sorted) | Top readers | - |
| **Student** | By Day | All Data | ✅ YES | Q7 | Complete daily log | - |
| **Grade** | Full Contest | Top N | ✅ YES | Q10 | Most minutes by grade | - |
| **Grade** | Full Contest | All Data | ❌ NO | - | All grades minutes summary | ⚠️ GAP |

### 6. MINUTES (Actual/Uncapped) Reports

| Entity | Period | Result Type | Report Exists? | Query ID | Description | Gap? |
|--------|--------|-------------|----------------|----------|-------------|------|
| **School** | Full Contest | Single Number | ✅ YES | Q21 | Total uncapped minutes (integrity) | - |
| **Team** | Full Contest | Breakdown | ❌ NO | - | Team uncapped minutes | ⚠️ GAP |
| **Class** | Full Contest | All Data | ❌ NO | - | Class uncapped minutes | ⚠️ GAP |
| **Student** | Full Contest | All Data | ✅ YES | Q21 | Uncapped vs capped comparison | - |
| **Student** | By Day | All Data | ❌ NO | - | Daily uncapped minutes | ⚠️ GAP |

### 7. MINUTES (Max Single Day) Reports

| Entity | Period | Result Type | Report Exists? | Query ID | Description | Gap? |
|--------|--------|-------------|----------------|----------|-------------|------|
| **School** | Full Contest | Single Number | ❌ NO | - | Highest single-day total | ⚠️ GAP |
| **Team** | Full Contest | Breakdown | ❌ NO | - | Best single day by team | ⚠️ GAP |
| **Class** | Full Contest | Top N | ❌ NO | - | Classes with best single day | ⚠️ GAP |
| **Student** | Full Contest | Top N | ❌ NO | - | Students with highest single day | ⚠️ GAP |
| **Student** | By Day | All Data | ❌ NO | - | All students on specific day | ⚠️ PARTIAL (Q7 has this) |

---

## Summary of Gaps by Category

### HIGH PRIORITY GAPS (Most Valuable)

1. **Daily Trend Reports**
   - ❌ School totals by day (donations, minutes, participation)
   - ❌ Team comparison by day
   - ❌ Daily progress tracking

2. **Grade-Level Summaries**
   - ❌ All grades participation summary
   - ❌ All grades minutes summary
   - ❌ All grades donations summary
   - ❌ Goal achievement by grade

3. **Class-Level Donations**
   - ❌ All classes ranked by donations
   - ❌ Daily class donations

4. **Max Single Day Performance**
   - ❌ Best single-day performance reports (all entities)

### MEDIUM PRIORITY GAPS

5. **Uncapped Minutes Analysis**
   - ❌ Team uncapped vs capped comparison
   - ❌ Class uncapped vs capped comparison

6. **Trend Analysis**
   - ❌ Growth/decline over time
   - ❌ Momentum indicators

### LOW PRIORITY GAPS (Already Covered Elsewhere)

7. **Student-Day Detail** - Partially covered by Q7 (Complete Log)

---

## Recommended New Reports

### New Report: Q24 - Daily Progress Dashboard
**Purpose:** Track day-by-day totals for school
**Columns:** Date | Total Minutes | Total Donations | Students Participated | New Readers | New Donors

### New Report: Q25 - Grade Level Summary
**Purpose:** Complete grade-level breakdown
**Columns:** Grade | Students | Avg Participation | Avg Minutes/Student | Avg Donation/Student | Goal Getters

### New Report: Q26 - Class Donations Leaderboard
**Purpose:** Rank all classes by fundraising
**Columns:** Rank | Class | Teacher | Grade | Team | Total Donations | Avg/Student | Total Sponsors

### New Report: Q27 - Best Single Day Performance
**Purpose:** Identify peak performance days
**Columns:** Entity Type | Entity Name | Date | Minutes Read | Students Participated

### New Report: Q28 - Team Daily Comparison
**Purpose:** Day-by-day team competition
**Columns:** Date | Phoenix Minutes | Dragons Minutes | Phoenix Participation | Dragons Participation | Daily Winner

### New Report: Q29 - Uncapped Minutes Analysis
**Purpose:** See impact of 120-min cap by entity
**Columns:** Entity | Capped Minutes | Uncapped Minutes | Difference | Students Affected

---

## Current Report Coverage Summary

| Metric Category | Coverage | Gaps |
|----------------|----------|------|
| **Donations** | 70% | Missing: Daily breakdowns, Class donations detail |
| **Sponsors** | 80% | Missing: Class-level detail |
| **Participation** | 85% | Missing: Grade summaries, Daily trends |
| **Minutes (Goals)** | 75% | Missing: School/Grade summaries |
| **Minutes (Capped)** | 90% | Missing: Daily school totals, Grade summaries |
| **Minutes (Uncapped)** | 40% | Missing: Team/Class comparisons |
| **Minutes (Max Day)** | 20% | Missing: All top-performance reports |

**Overall Coverage:** ~73% of possible reporting combinations

---

## Existing Reports Quick Reference

| ID | Name | Primary Metric | Entity | Period | Result Type |
|----|------|---------------|--------|--------|-------------|
| Q1 | Table Counts | Various | School | Full | Single Numbers |
| Q2 | Daily Summary | Participation, Minutes | Class/Team | By Day/Full | All Data |
| Q3 | Reader Cumulative Enhanced | Minutes, Donations | Student | Full | All Data |
| Q4 | Prize Drawing | Goals Met | Student | By Day | All Data |
| Q5 | Student Cumulative | Minutes, Donations, Goals | Student | Full | All Data/Top N |
| Q6 | Class Participation | Participation | Class | Full | All Data |
| Q7 | Complete Log | Minutes | Student | By Day/Full | All Data |
| Q8 | Student Reading Details | Minutes, Goals | Student | Full | All Data |
| Q9 | Most Donations by Grade | Donations | Grade | Full | Top N |
| Q10 | Most Minutes by Grade | Minutes (Capped) | Grade | Full | Top N |
| Q11 | Most Sponsors by Grade | Sponsors | Grade | Full | Top N |
| Q12 | Best Class by Grade | Participation | Class | Full | Top N |
| Q13 | Overall Best Class | Participation | Class | Full | Top N |
| Q14 | Team Participation | Participation, Goals | Team | Full | Breakdown |
| Q15 | Goal Getters | Goals Met | Student | Full | All Data |
| Q16 | Top Earner Per Team | Donations | Team | Full | Top N |
| Q18 | Lead Class by Grade | Participation | Class | Full | Top N |
| Q19 | Team Minutes | Minutes (Capped) | Team | Full | Breakdown |
| Q20 | Team Donations | Donations, Sponsors | Team | Full | Breakdown |
| Q21 | Minutes Integrity | Minutes (Capped vs Uncapped) | Student | Full | All Data |
| Q22 | Student Name Sync | Data Integrity | Student | Full | All Data |
| Q23 | Roster Integrity | Data Integrity | Student | Full | All Data |

---

## Recommendations

### For Dashboard Tabs (Teams, Classes, Students):

**Teams Tab Should Include:**
- Q14 (Team Participation) ✅
- Q19 (Team Minutes) ✅
- Q20 (Team Donations) ✅
- **NEW: Q28 (Team Daily Comparison)** ⚠️

**Classes Tab Should Include:**
- Q6 (Class Participation) ✅
- Q12/Q13 (Best Classes) ✅
- **NEW: Q26 (Class Donations Leaderboard)** ⚠️
- **NEW: Q25 (Grade Summary)** ⚠️

**Students Tab Should Include:**
- Q5 (Student Cumulative - Top Readers/Fundraisers) ✅
- Q15 (Goal Getters) ✅
- Q8 (Student Reading Details) ✅
- Individual student lookup with Q3/Q5 data ✅

### Priority Implementation Order:

1. **Q25 - Grade Level Summary** (fills major gap)
2. **Q24 - Daily Progress Dashboard** (trending/momentum)
3. **Q26 - Class Donations Leaderboard** (completes class reporting)
4. **Q28 - Team Daily Comparison** (enhances team competition)
5. **Q27 - Best Single Day Performance** (interesting stats)
6. **Q29 - Uncapped Minutes Analysis** (data integrity enhancement)
