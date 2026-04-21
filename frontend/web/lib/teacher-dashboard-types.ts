export type ProgressStatus =
  | "not_started"
  | "in_progress"
  | "completed"
  | "skipped";

export type KpiWeekPair = {
  current_week: number;
  previous_week: number;
};

export type AvgProgressWeekPair = {
  current_week: number;
  previous_week: number;
};

export type TeacherDashboardKpis = {
  active_students: KpiWeekPair;
  homework_completed_events: KpiWeekPair;
  avg_progress_percent: AvgProgressWeekPair;
  dialogue_questions: KpiWeekPair;
};

export type ActivityByDayItem = {
  day: string;
  question_count: number;
};

export type DashboardDialogueTurnItem = {
  membership_id: string;
  user_message_id: string;
  assistant_message_id: string;
  student_display_name: string | null;
  question_text: string;
  answer_text: string;
  asked_at: string;
};

export type DashboardRecentSubmissionItem = {
  membership_id: string;
  student_display_name: string | null;
  checkpoint_id: string;
  checkpoint_title: string;
  status: ProgressStatus;
  comment: string | null;
  submission_links: string[] | null;
  updated_at: string;
};

export type DashboardMatrixCell = {
  checkpoint_id: string;
  status: ProgressStatus;
  updated_at: string | null;
};

export type DashboardMatrixRow = {
  membership_id: string;
  display_name: string | null;
  score_completed: number;
  score_total: number;
  cells: DashboardMatrixCell[];
};

export type TeacherDashboardRecentTurns = {
  items: DashboardDialogueTurnItem[];
  next_cursor: string | null;
};

export type TeacherDashboardResponse = {
  cohort_id: string;
  cohort_title?: string | null;
  kpis: TeacherDashboardKpis;
  activity_by_day: ActivityByDayItem[];
  recent_turns: TeacherDashboardRecentTurns;
  recent_submissions: DashboardRecentSubmissionItem[];
  matrix: DashboardMatrixRow[];
};

export type ApiErrorBody = {
  error?: { code?: string; message?: string; details?: unknown };
};
