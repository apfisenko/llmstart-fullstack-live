import type { LeaderboardCheckpointItem } from "@/lib/leaderboard-types";
import type { ProgressStatus } from "@/lib/teacher-dashboard-types";

export type { ProgressStatus };

export type StudentProgressCheckpointItem = LeaderboardCheckpointItem;

export type StudentProgressRecordItem = {
  checkpoint_id: string;
  status: ProgressStatus;
  updated_at: string | null;
  comment: string | null;
  submission_links: string[] | null;
};

export type StudentProgressOverviewResponse = {
  cohort_id: string;
  membership_id: string;
  display_name?: string | null;
  checkpoints: StudentProgressCheckpointItem[];
  records: StudentProgressRecordItem[];
};

export type PutProgressRecordRequest = {
  status: ProgressStatus;
  comment?: string | null;
  submission_links?: string[] | null;
};

export type ProgressRecordResponse = {
  id: string;
  cohort_id: string;
  membership_id: string;
  checkpoint_id: string;
  status: ProgressStatus;
  comment?: string | null;
  submission_links?: string[] | null;
  updated_at: string;
};
