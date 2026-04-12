\set ON_ERROR_STOP on
SELECT version_num FROM alembic_version;
SELECT title FROM cohorts WHERE title = 'M05 LLM Start Fullstack';
SELECT COUNT(*) AS students FROM cohort_memberships m
  JOIN cohorts c ON c.id = m.cohort_id
  WHERE c.title = 'M05 LLM Start Fullstack' AND m.role = 'student';
SELECT COUNT(*) AS checkpoints FROM progress_checkpoints ck
  JOIN cohorts c ON c.id = ck.cohort_id
  WHERE c.title = 'M05 LLM Start Fullstack';
SELECT COUNT(*) AS progress_completed FROM progress_records pr
  JOIN cohort_memberships m ON m.id = pr.membership_id
  JOIN cohorts c ON c.id = m.cohort_id
  WHERE c.title = 'M05 LLM Start Fullstack' AND pr.status = 'completed';
