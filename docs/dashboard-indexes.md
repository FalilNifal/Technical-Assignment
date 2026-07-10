# Dashboard Indexes

Run these in PostgreSQL or add them to an Alembic migration:

```sql
CREATE INDEX IF NOT EXISTS idx_reports_week_range
ON weekly_reports (week_start, week_end);

CREATE INDEX IF NOT EXISTS idx_reports_week_status
ON weekly_reports (week_start, week_end, status);

CREATE INDEX IF NOT EXISTS idx_reports_week_project
ON weekly_reports (week_start, week_end, project_id);

CREATE INDEX IF NOT EXISTS idx_reports_week_user
ON weekly_reports (week_start, week_end, user_id);

CREATE INDEX IF NOT EXISTS idx_reports_dashboard_filters
ON weekly_reports (week_start, week_end, project_id, user_id, status);

CREATE INDEX IF NOT EXISTS idx_reports_submitted_at
ON weekly_reports (submitted_at);

CREATE INDEX IF NOT EXISTS idx_reports_late
ON weekly_reports (is_late)
WHERE is_late = TRUE;

CREATE INDEX IF NOT EXISTS idx_reports_blockers_not_empty
ON weekly_reports (week_start, week_end)
WHERE blockers IS NOT NULL AND LENGTH(TRIM(blockers)) > 0;

CREATE INDEX IF NOT EXISTS idx_users_role_active
ON users (role_id, is_active);

CREATE INDEX IF NOT EXISTS idx_projects_active
ON projects (is_active);
```
