import type { ProgressStatus } from "@/lib/teacher-dashboard-types";

export type { ProgressStatus };

export type LeaderboardCheckpointItem = {
  id: string;
  code: string;
  title: string;
  sort_order: number;
  required: boolean;
  is_homework: boolean;
};

export type LeaderboardCheckpointStatus = {
  checkpoint_id: string;
  status: ProgressStatus;
};

export type LeaderboardEntry = {
  rank: number;
  membership_id: string;
  user_id: string;
  display_name: string | null;
  progress_percent: number;
  completed_checkpoints: number;
  total_checkpoints: number;
  homework_completed: number;
  lesson_completed: number;
  scatter_x: number | null;
  scatter_y: number | null;
  per_checkpoint: LeaderboardCheckpointStatus[];
};

export type LeaderboardResponse = {
  cohort_id: string;
  checkpoints: LeaderboardCheckpointItem[];
  entries: LeaderboardEntry[];
};
