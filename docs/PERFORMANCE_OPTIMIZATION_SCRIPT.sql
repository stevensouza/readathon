-- Performance Optimization: Add Missing Indexes
-- Execute this on both readathon_sample.db and readathon_2025.db
-- Estimated improvement: 60-84% faster queries

-- =============================================================================
-- HIGH PRIORITY INDEXES (Execute First)
-- =============================================================================

-- Daily_Logs indexes (most frequently joined table)
CREATE INDEX IF NOT EXISTS idx_daily_logs_student ON Daily_Logs(student_name);
CREATE INDEX IF NOT EXISTS idx_daily_logs_date ON Daily_Logs(log_date);
CREATE INDEX IF NOT EXISTS idx_daily_logs_student_date ON Daily_Logs(student_name, log_date);

-- Reader_Cumulative indexes (second most frequently joined)
CREATE INDEX IF NOT EXISTS idx_reader_cumulative_student ON Reader_Cumulative(student_name);

-- Roster indexes (used in class/grade/team aggregations)
CREATE INDEX IF NOT EXISTS idx_roster_class ON Roster(class_name);
CREATE INDEX IF NOT EXISTS idx_roster_grade ON Roster(grade_level);
CREATE INDEX IF NOT EXISTS idx_roster_team ON Roster(team_name);

-- =============================================================================
-- COMPOSITE INDEXES (for specific query patterns)
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_roster_grade_team ON Roster(grade_level, team_name);
CREATE INDEX IF NOT EXISTS idx_roster_class_team ON Roster(class_name, team_name);

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Check that indexes were created
SELECT name, tbl_name, sql 
FROM sqlite_master 
WHERE type='index' 
  AND name LIKE 'idx_%'
ORDER BY tbl_name, name;

-- =============================================================================
-- ANALYZE (Update SQLite statistics for query optimizer)
-- =============================================================================

ANALYZE;

-- =============================================================================
-- EXECUTION INSTRUCTIONS
-- =============================================================================

-- Execute on sample database:
--   sqlite3 db/readathon_sample.db < docs/PERFORMANCE_OPTIMIZATION_SCRIPT.sql

-- Execute on production database:
--   sqlite3 db/readathon_2025.db < docs/PERFORMANCE_OPTIMIZATION_SCRIPT.sql

-- Or using Python:
--   python3 -c "
--   import sqlite3
--   conn = sqlite3.connect('db/readathon_sample.db')
--   with open('docs/PERFORMANCE_OPTIMIZATION_SCRIPT.sql', 'r') as f:
--       conn.executescript(f.read())
--   conn.close()
--   "
