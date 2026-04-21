"use client";

import { Check, Circle, Minus } from "lucide-react";

import type {
  LeaderboardEntry,
  LeaderboardResponse,
  ProgressStatus,
} from "@/lib/leaderboard-types";
import { cn } from "@/lib/utils";

type Props = {
  data: LeaderboardResponse;
  className?: string;
};

function statusIcon(status: ProgressStatus) {
  if (status === "completed") {
    return (
      <Check className="size-4 text-emerald-400" strokeWidth={2.5} aria-label="Сдано" />
    );
  }
  if (status === "in_progress") {
    return (
      <Circle className="size-3.5 text-amber-400" strokeWidth={2} aria-label="В работе" />
    );
  }
  if (status === "skipped") {
    return (
      <Minus className="size-4 text-muted-foreground" strokeWidth={2} aria-label="Пропущено" />
    );
  }
  return <span className="inline-block size-3 rounded-sm bg-muted/50" aria-hidden />;
}

function rankCell(rank: number) {
  if (rank === 1) {
    return (
      <span className="inline-flex items-center justify-center font-mono tabular-nums">
        <span className="text-lg leading-none" aria-hidden>
          🥇
        </span>
        <span className="sr-only">1 место</span>
      </span>
    );
  }
  if (rank === 2) {
    return (
      <span className="inline-flex items-center justify-center font-mono tabular-nums">
        <span className="text-lg leading-none" aria-hidden>
          🥈
        </span>
        <span className="sr-only">2 место</span>
      </span>
    );
  }
  if (rank === 3) {
    return (
      <span className="inline-flex items-center justify-center font-mono tabular-nums">
        <span className="text-lg leading-none" aria-hidden>
          🥉
        </span>
        <span className="sr-only">3 место</span>
      </span>
    );
  }
  return <span className="font-mono tabular-nums text-muted-foreground">{rank}</span>;
}

function rowTone(rank: number): string {
  if (rank === 1) return "bg-amber-500/10 ring-1 ring-amber-500/25";
  if (rank === 2) return "bg-slate-400/10 ring-1 ring-slate-400/20";
  if (rank === 3) return "bg-amber-700/15 ring-1 ring-amber-700/30";
  return "";
}

function stickyNameBg(rank: number): string {
  if (rank === 1) return "bg-amber-500/10";
  if (rank === 2) return "bg-slate-400/10";
  if (rank === 3) return "bg-amber-700/15";
  return "bg-card";
}

function entryName(e: LeaderboardEntry): string {
  const n = e.display_name?.trim();
  if (n) return n;
  return `Участник ${e.membership_id.slice(0, 8)}…`;
}

export function LeaderboardTable({ data, className }: Props) {
  const cols = [...data.checkpoints].sort(
    (a, b) => a.sort_order - b.sort_order || a.id.localeCompare(b.id),
  );

  return (
    <div className={cn("overflow-x-auto rounded-lg border border-border", className)}>
      <table className="w-full min-w-max border-collapse text-left text-sm">
        <thead>
          <tr className="border-b border-border bg-card/40 font-mono text-xs uppercase tracking-wide text-muted-foreground">
            <th className="sticky left-0 z-10 min-w-[12rem] bg-card px-3 py-2.5 shadow-[1px_0_0_hsl(var(--border))]">
              <span className="mr-3 inline-block w-8 text-center">#</span>
              Участник
            </th>
            <th className="px-3 py-2.5">Прогресс</th>
            <th className="whitespace-nowrap px-3 py-2.5">Счёт</th>
            {cols.map((c) => (
              <th
                key={c.id}
                className="max-w-[4.5rem] px-1.5 py-2.5 text-center font-mono text-[10px] leading-tight normal-case"
                title={c.title}
              >
                <span className="line-clamp-2">{c.title}</span>
                {c.is_homework ? (
                  <span className="mt-0.5 block text-[9px] text-primary/80">ДЗ</span>
                ) : null}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.entries.map((e) => {
            const byCp = new Map(
              e.per_checkpoint.map((p) => [p.checkpoint_id, p.status]),
            );
            return (
              <tr
                key={e.membership_id}
                className={cn(
                  "border-b border-border/60 last:border-0",
                  rowTone(e.rank),
                )}
              >
                <td
                  className={cn(
                    "sticky left-0 z-10 max-w-[16rem] px-3 py-2 align-middle shadow-[1px_0_0_hsl(var(--border))]",
                    stickyNameBg(e.rank),
                  )}
                >
                  <div className="flex min-w-0 items-center gap-2">
                    <span className="shrink-0 font-mono">{rankCell(e.rank)}</span>
                    <span className="truncate font-medium">{entryName(e)}</span>
                  </div>
                </td>
                <td className="min-w-[8rem] px-3 py-2 align-middle">
                  <div className="flex items-center gap-2">
                    <div className="h-2 min-w-[5rem] flex-1 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary/80"
                        style={{ width: `${Math.min(100, Math.max(0, e.progress_percent))}%` }}
                      />
                    </div>
                    <span className="shrink-0 font-mono text-xs text-muted-foreground">
                      {e.progress_percent.toFixed(0)}%
                    </span>
                  </div>
                </td>
                <td className="whitespace-nowrap px-3 py-2 align-middle font-mono text-xs">
                  {e.completed_checkpoints} / {e.total_checkpoints}
                </td>
                {cols.map((c) => {
                  const st = byCp.get(c.id) ?? "not_started";
                  return (
                    <td key={c.id} className="px-1 py-2 text-center align-middle">
                      <div className="flex justify-center">{statusIcon(st)}</div>
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
