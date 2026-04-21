"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { Button, buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import type { ApiErrorBody } from "@/lib/teacher-dashboard-types";
import type {
  ProgressStatus,
  StudentProgressCheckpointItem,
  StudentProgressOverviewResponse,
  StudentProgressRecordItem,
} from "@/lib/student-progress-types";
import { readWebSession, type WebSession } from "@/lib/session";
import { cn } from "@/lib/utils";

const MAX_SUBMISSION_LINKS = 32;

type MergedLessonRow = {
  checkpoint: StudentProgressCheckpointItem;
  record: StudentProgressRecordItem | undefined;
  status: ProgressStatus;
};

function formatUpdatedAt(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("ru-RU", {
      dateStyle: "short",
      timeStyle: "short",
    });
  } catch {
    return iso;
  }
}

function mergeOverview(data: StudentProgressOverviewResponse): MergedLessonRow[] {
  const byCp = new Map(data.records.map((r) => [r.checkpoint_id, r]));
  return [...data.checkpoints]
    .sort((a, b) => a.sort_order - b.sort_order)
    .map((checkpoint) => {
      const record = byCp.get(checkpoint.id);
      const status: ProgressStatus = record?.status ?? "not_started";
      return { checkpoint, record, status };
    });
}

function findSubmittableRowIndex(rows: MergedLessonRow[]): number | null {
  for (let i = 0; i < rows.length; i++) {
    const prevCleared = rows
      .slice(0, i)
      .every((r) => r.status === "completed" || r.status === "skipped");
    if (!prevCleared) continue;
    if (rows[i].status !== "completed" && rows[i].status !== "skipped") {
      return i;
    }
  }
  return null;
}

function parseSubmissionLinks(raw: string): string[] {
  const lines = raw
    .split(/\r?\n/)
    .map((s) => s.trim())
    .filter(Boolean);
  return lines.slice(0, MAX_SUBMISSION_LINKS);
}

export default function StudentCabinetPage() {
  const [session, setSession] = useState<WebSession | null | undefined>(undefined);
  const [overview, setOverview] = useState<StudentProgressOverviewResponse | null>(
    null,
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sheetOpen, setSheetOpen] = useState(false);
  const [submitCheckpointId, setSubmitCheckpointId] = useState<string | null>(null);
  const [submitTitle, setSubmitTitle] = useState("");
  const [comment, setComment] = useState("");
  const [linksRaw, setLinksRaw] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    setSession(readWebSession());
  }, []);

  const fetchOverview = useCallback(async (s: WebSession) => {
    const url = `/api/v1/cohorts/${encodeURIComponent(s.cohort_id)}/memberships/${encodeURIComponent(s.membership_id)}/progress-overview`;
    const res = await fetch(url, { cache: "no-store" });
    const raw = await res.text();
    let parsed: unknown;
    try {
      parsed = JSON.parse(raw) as unknown;
    } catch {
      throw new Error("Некорректный ответ сервера");
    }
    if (!res.ok) {
      const err = parsed as ApiErrorBody;
      throw new Error(err.error?.message ?? `Ошибка ${res.status}`);
    }
    return parsed as StudentProgressOverviewResponse;
  }, []);

  useEffect(() => {
    if (session === undefined || session === null || session.role !== "student") {
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchOverview(session);
        if (!cancelled) setOverview(data);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Ошибка загрузки");
          setOverview(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [session, fetchOverview]);

  const rows = useMemo(
    () => (overview ? mergeOverview(overview) : []),
    [overview],
  );
  const submittableIndex = useMemo(() => findSubmittableRowIndex(rows), [rows]);
  const completedCount = useMemo(
    () => rows.filter((r) => r.status === "completed").length,
    [rows],
  );

  function openSubmitSheet(checkpointId: string, title: string) {
    setSubmitCheckpointId(checkpointId);
    setSubmitTitle(title);
    setComment("");
    setLinksRaw("");
    setSubmitError(null);
    setSheetOpen(true);
  }

  async function onSubmitRecord() {
    if (!session || session.role !== "student" || !submitCheckpointId) return;
    setSubmitting(true);
    setSubmitError(null);
    const submission_links = parseSubmissionLinks(linksRaw);
    const body = {
      status: "completed" as const,
      comment: comment.trim() || null,
      submission_links: submission_links.length > 0 ? submission_links : null,
    };
    try {
      const url = `/api/v1/cohorts/${encodeURIComponent(session.cohort_id)}/memberships/${encodeURIComponent(session.membership_id)}/progress-records/${encodeURIComponent(submitCheckpointId)}`;
      const res = await fetch(url, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const raw = await res.text();
      let parsed: unknown;
      try {
        parsed = JSON.parse(raw) as unknown;
      } catch {
        throw new Error("Некорректный ответ сервера");
      }
      if (!res.ok) {
        const err = parsed as ApiErrorBody;
        throw new Error(err.error?.message ?? `Ошибка ${res.status}`);
      }
      setSheetOpen(false);
      setSubmitCheckpointId(null);
      const next = await fetchOverview(session);
      setOverview(next);
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Ошибка сохранения");
    } finally {
      setSubmitting(false);
    }
  }

  if (session === undefined) {
    return (
      <div className="text-sm text-muted-foreground">Загрузка сессии…</div>
    );
  }

  if (session === null) {
    return (
      <Card className="max-w-lg border-border/80">
        <CardHeader>
          <CardTitle className="font-mono text-lg">Кабинет студента</CardTitle>
          <CardDescription>
            Войдите по Telegram username, чтобы открыть прогресс по потоку.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            href="/login"
            className={cn(buttonVariants({ variant: "default", size: "sm" }), "inline-flex")}
          >
            Вход
          </Link>
        </CardContent>
      </Card>
    );
  }

  if (session.role === "teacher") {
    return (
      <Card className="max-w-lg border-border/80">
        <CardHeader>
          <CardTitle className="font-mono text-lg">Кабинет студента</CardTitle>
          <CardDescription>
            Экран прогресса доступен в сессии со ролью студента. В текущей сессии вы
            вошли как преподаватель.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            href="/teacher"
            className={cn(buttonVariants({ variant: "default", size: "sm" }), "inline-flex")}
          >
            Панель преподавателя
          </Link>
        </CardContent>
      </Card>
    );
  }

  const cohortTitle = session.cohort_title?.trim() || "Поток";
  const displayName =
    overview?.display_name?.trim() ||
    session.display_name?.trim() ||
    "Студент";
  const nextLessonTitle =
    submittableIndex !== null ? rows[submittableIndex]?.checkpoint.title : null;

  return (
    <div className="flex min-w-0 flex-col gap-6 pb-10">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="font-mono text-xl font-semibold tracking-tight">
            Кабинет студента
          </h1>
          <p className="mt-1 font-mono text-sm text-muted-foreground">{cohortTitle}</p>
          <p className="mt-3 text-sm text-foreground">
            Здравствуйте,{" "}
            <span className="font-medium text-primary">{displayName}</span>
          </p>
        </div>
        <Link
          href="/chat"
          className={cn(
            buttonVariants({ variant: "secondary", size: "sm" }),
            "shrink-0 font-mono text-xs",
          )}
        >
          Чат с ассистентом
        </Link>
      </div>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      {loading && !overview ? (
        <p className="text-sm text-muted-foreground">Загрузка данных…</p>
      ) : null}

      {overview && !loading ? (
        <Card className="border-border/80">
          <CardHeader className="pb-2">
            <CardTitle className="font-mono text-base">Прогресс</CardTitle>
            <CardDescription>
              Сдано уроков: {completedCount} из {rows.length}
              {nextLessonTitle ? (
                <>
                  . Следующий этап:{" "}
                  <span className="text-foreground">{nextLessonTitle}</span>
                </>
              ) : rows.length > 0 ? (
                <>. Все этапы закрыты по текущим данным.</>
              ) : null}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {rows.length === 0 ? (
              <p className="text-sm text-muted-foreground">В потоке нет этапов.</p>
            ) : (
              <ul className="divide-y divide-border rounded-md border border-border">
                {rows.map((row, index) => {
                  const { checkpoint, status, record } = row;
                  const isDone = status === "completed" || status === "skipped";
                  const isSubmittable =
                    submittableIndex !== null && index === submittableIndex;
                  const isLocked = !isDone && !isSubmittable;

                  return (
                    <li
                      key={checkpoint.id}
                      className={cn(
                        "flex flex-col gap-2 px-3 py-3 sm:flex-row sm:items-center sm:justify-between",
                        isDone && status === "completed" && "bg-emerald-950/20",
                        isLocked && "opacity-60",
                      )}
                    >
                      <div className="min-w-0 flex-1">
                        <div className="font-medium">{checkpoint.title}</div>
                        <div className="font-mono text-xs text-muted-foreground">
                          {checkpoint.code} · порядок {checkpoint.sort_order}
                          {status === "skipped" ? " · пропущено" : null}
                        </div>
                        {status === "completed" && record?.updated_at ? (
                          <div className="mt-1 font-mono text-xs text-emerald-600/90 dark:text-emerald-400/90">
                            Сдано: {formatUpdatedAt(record.updated_at)}
                          </div>
                        ) : null}
                      </div>
                      <div className="shrink-0">
                        {isSubmittable ? (
                          <Button
                            type="button"
                            size="sm"
                            className="font-mono text-xs"
                            onClick={() =>
                              openSubmitSheet(checkpoint.id, checkpoint.title)
                            }
                          >
                            Сдать задание
                          </Button>
                        ) : isLocked ? (
                          <span className="font-mono text-xs text-muted-foreground">
                            Заблокировано
                          </span>
                        ) : isDone ? (
                          <span className="font-mono text-xs text-muted-foreground">
                            {status === "skipped" ? "Пропуск" : "Сдано"}
                          </span>
                        ) : null}
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </CardContent>
        </Card>
      ) : null}

      <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
        <SheetContent side="right" className="w-full sm:max-w-md">
          <SheetHeader>
            <SheetTitle className="font-mono text-sm">Сдача задания</SheetTitle>
            <SheetDescription className="font-mono text-xs">
              {submitTitle}
            </SheetDescription>
          </SheetHeader>
          <div className="flex flex-col gap-4 px-4 pb-2">
            <div className="space-y-2">
              <Label htmlFor="student-comment" className="font-mono text-xs">
                Текстовый отчёт
              </Label>
              <textarea
                id="student-comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={6}
                maxLength={2000}
                placeholder="Что сделали, что поняли…"
                disabled={submitting}
                className={cn(
                  "w-full resize-y rounded-lg border border-input bg-transparent px-2.5 py-2 text-sm outline-none",
                  "placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
                  "disabled:cursor-not-allowed disabled:opacity-50 dark:bg-input/30",
                )}
              />
              <p className="font-mono text-[10px] text-muted-foreground">
                {comment.length} / 2000
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="student-links" className="font-mono text-xs">
                Ссылки на работы (по одной на строку, до {MAX_SUBMISSION_LINKS})
              </Label>
              <textarea
                id="student-links"
                value={linksRaw}
                onChange={(e) => setLinksRaw(e.target.value)}
                rows={4}
                placeholder="https://…"
                disabled={submitting}
                className={cn(
                  "w-full resize-y rounded-lg border border-input bg-transparent px-2.5 py-2 font-mono text-xs outline-none",
                  "placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
                  "disabled:cursor-not-allowed disabled:opacity-50 dark:bg-input/30",
                )}
              />
            </div>
            {submitError ? (
              <p className="text-sm text-destructive" role="alert">
                {submitError}
              </p>
            ) : null}
          </div>
          <SheetFooter className="border-t border-border/60 sm:flex-row">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={submitting}
              onClick={() => setSheetOpen(false)}
            >
              Отмена
            </Button>
            <Button
              type="button"
              size="sm"
              disabled={submitting}
              onClick={() => void onSubmitRecord()}
            >
              {submitting ? "Отправка…" : "Отправить"}
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>
    </div>
  );
}
