"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { TeacherActivityChart } from "@/components/teacher-activity-chart";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { readWebSession, type WebSession } from "@/lib/session";
import type {
  ApiErrorBody,
  DashboardMatrixRow,
  DashboardRecentSubmissionItem,
  ProgressStatus,
  TeacherDashboardResponse,
} from "@/lib/teacher-dashboard-types";
import { cn } from "@/lib/utils";

function formatAskedAt(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

function formatUpdatedTooltip(iso: string | null): string {
  if (!iso) return "Нет даты сдачи";
  try {
    return new Date(iso).toLocaleString("ru-RU");
  } catch {
    return iso;
  }
}

function deltaIntLabel(current: number, previous: number): string {
  const d = current - previous;
  if (d === 0) return "как на прошлой неделе";
  const sign = d > 0 ? "+" : "−";
  return `${sign}${Math.abs(d)} к прошлой неделе`;
}

function deltaFloatLabel(current: number, previous: number): string {
  const d = current - previous;
  if (Math.abs(d) < 0.01) return "как на прошлой неделе";
  const sign = d > 0 ? "+" : "−";
  return `${sign}${Math.abs(d).toFixed(1)} п.п. к прошлой неделе`;
}

function cellTone(status: ProgressStatus): string {
  if (status === "completed") {
    return "bg-emerald-500/25 ring-1 ring-emerald-500/40";
  }
  if (status === "in_progress") {
    return "bg-amber-500/15 ring-1 ring-amber-500/30";
  }
  if (status === "skipped") {
    return "bg-muted/60 ring-1 ring-border";
  }
  return "bg-muted/30 ring-1 ring-border/60";
}

export default function TeacherDashboardPage() {
  const [session, setSession] = useState<WebSession | null>(null);
  const [qInput, setQInput] = useState("");
  const [q, setQ] = useState("");
  const [activityDays, setActivityDays] = useState(14);

  const [dashboard, setDashboard] = useState<TeacherDashboardResponse | null>(
    null,
  );
  const [turnItems, setTurnItems] = useState<
    TeacherDashboardResponse["recent_turns"]["items"]
  >([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sheetOpen, setSheetOpen] = useState(false);
  const [selectedSubmission, setSelectedSubmission] =
    useState<DashboardRecentSubmissionItem | null>(null);

  useEffect(() => {
    setSession(readWebSession());
  }, []);

  useEffect(() => {
    const t = window.setTimeout(() => setQ(qInput), 400);
    return () => window.clearTimeout(t);
  }, [qInput]);

  const fetchPage = useCallback(
    async (turnsCursor: string | null) => {
      if (!session || session.role !== "teacher") {
        return null;
      }
      const params = new URLSearchParams({
        viewer_membership_id: session.membership_id,
        activity_days: String(activityDays),
        limit: "20",
      });
      const trimmedQ = q.trim();
      if (trimmedQ) {
        params.set("q", trimmedQ);
      }
      if (turnsCursor) {
        params.set("turns_cursor", turnsCursor);
      }
      const url = `/api/v1/cohorts/${encodeURIComponent(session.cohort_id)}/teacher-dashboard?${params.toString()}`;
      const res = await fetch(url, { cache: "no-store" });
      const raw = await res.text();
      let data: unknown;
      try {
        data = JSON.parse(raw) as unknown;
      } catch {
        throw new Error("Некорректный ответ сервера");
      }
      if (!res.ok) {
        const err = data as ApiErrorBody;
        const msg = err.error?.message ?? `Ошибка ${res.status}`;
        throw new Error(msg);
      }
      return data as TeacherDashboardResponse;
    },
    [session, activityDays, q],
  );

  useEffect(() => {
    if (!session || session.role !== "teacher") {
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchPage(null);
        if (cancelled || !data) return;
        setDashboard(data);
        setTurnItems(data.recent_turns.items);
        setNextCursor(data.recent_turns.next_cursor ?? null);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Ошибка загрузки");
          setDashboard(null);
          setTurnItems([]);
          setNextCursor(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [session, fetchPage]);

  async function loadMoreTurns() {
    if (!nextCursor || loadingMore) return;
    setLoadingMore(true);
    setError(null);
    try {
      const data = await fetchPage(nextCursor);
      if (!data) return;
      setTurnItems((prev) => [...prev, ...data.recent_turns.items]);
      setNextCursor(data.recent_turns.next_cursor ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка загрузки");
    } finally {
      setLoadingMore(false);
    }
  }

  const matrixColumns = useMemo(() => {
    const row = dashboard?.matrix[0];
    if (!row) return [];
    return row.cells.map((c, i) => ({ checkpoint_id: c.checkpoint_id, index: i + 1 }));
  }, [dashboard?.matrix]);

  if (session === null) {
    return (
      <div className="text-sm text-muted-foreground">Загрузка сессии…</div>
    );
  }

  if (session.role !== "teacher") {
    return (
      <Card className="max-w-lg border-border/80">
        <CardHeader>
          <CardTitle className="font-mono text-lg">Панель преподавателя</CardTitle>
          <CardDescription>
            Доступна только для роли преподавателя. Вы вошли как студент.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            href="/student"
            className={cn(buttonVariants({ variant: "outline", size: "sm" }), "inline-flex")}
          >
            Открыть кабинет студента
          </Link>
        </CardContent>
      </Card>
    );
  }

  const title =
    dashboard?.cohort_title?.trim() ||
    session.cohort_title?.trim() ||
    "Поток";

  return (
    <div className="flex min-w-0 flex-col gap-8 pb-10">
      <div>
        <h1 className="font-mono text-xl font-semibold tracking-tight">
          Панель преподавателя
        </h1>
        <p className="mt-1 font-mono text-sm text-muted-foreground">{title}</p>
      </div>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      {loading && !dashboard ? (
        <p className="text-sm text-muted-foreground">Загрузка данных…</p>
      ) : null}

      {dashboard ? (
        <>
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard
              title="Активные студенты"
              description="Уникальные авторы вопросов за календарную неделю"
              current={dashboard.kpis.active_students.current_week}
              previous={dashboard.kpis.active_students.previous_week}
              formatDelta={deltaIntLabel}
            />
            <KpiCard
              title="События «ДЗ сдано»"
              description="Завершённые домашние чекпоинты за неделю"
              current={dashboard.kpis.homework_completed_events.current_week}
              previous={dashboard.kpis.homework_completed_events.previous_week}
              formatDelta={deltaIntLabel}
            />
            <KpiCard
              title="Средний прогресс"
              description="Доля завершённых этапов по студентам"
              current={dashboard.kpis.avg_progress_percent.current_week}
              previous={dashboard.kpis.avg_progress_percent.previous_week}
              suffix="%"
              formatDelta={deltaFloatLabel}
            />
            <KpiCard
              title="Вопросы к ассистенту"
              description="Новые ходы диалога за неделю"
              current={dashboard.kpis.dialogue_questions.current_week}
              previous={dashboard.kpis.dialogue_questions.previous_week}
              formatDelta={deltaIntLabel}
            />
          </section>

          <Card className="border-border/80">
            <CardHeader className="pb-2">
              <CardTitle className="font-mono text-base">
                Активность: вопросы по дням
              </CardTitle>
              <CardDescription>
                Число вопросов к ассистенту за выбранный период
              </CardDescription>
              <div className="flex flex-wrap gap-2 pt-2">
                {([7, 14, 30] as const).map((d) => (
                  <Button
                    key={d}
                    type="button"
                    size="xs"
                    variant={activityDays === d ? "default" : "outline"}
                    onClick={() => setActivityDays(d)}
                  >
                    {d} дн.
                  </Button>
                ))}
              </div>
            </CardHeader>
            <CardContent>
              <TeacherActivityChart data={dashboard.activity_by_day} />
            </CardContent>
          </Card>

          <Card className="border-border/80">
            <CardHeader className="pb-2">
              <CardTitle className="font-mono text-base">
                Вопросы и ответы
              </CardTitle>
              <CardDescription>Поиск по тексту вопроса</CardDescription>
              <div className="max-w-md pt-2">
                <Input
                  value={qInput}
                  onChange={(e) => setQInput(e.target.value)}
                  placeholder="Поиск…"
                  className="font-mono text-sm"
                  aria-label="Поиск по вопросам"
                />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="overflow-x-auto rounded-md border border-border">
                <table className="w-full min-w-[640px] border-collapse text-left text-sm">
                  <thead className="border-b border-border bg-muted/40 font-mono text-xs uppercase tracking-wide text-muted-foreground">
                    <tr>
                      <th className="px-3 py-2">Когда</th>
                      <th className="px-3 py-2">Студент</th>
                      <th className="px-3 py-2">Вопрос</th>
                      <th className="px-3 py-2">Ответ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {turnItems.length === 0 ? (
                      <tr>
                        <td
                          colSpan={4}
                          className="px-3 py-8 text-center text-muted-foreground"
                        >
                          Нет записей
                        </td>
                      </tr>
                    ) : (
                      turnItems.map((row) => (
                        <tr
                          key={`${row.user_message_id}-${row.assistant_message_id}`}
                          className="border-b border-border/60 align-top last:border-0"
                        >
                          <td className="whitespace-nowrap px-3 py-2 font-mono text-xs text-muted-foreground">
                            {formatAskedAt(row.asked_at)}
                          </td>
                          <td className="px-3 py-2 text-xs">
                            {row.student_display_name ?? "—"}
                          </td>
                          <td className="max-w-[220px] px-3 py-2 text-xs leading-relaxed break-words">
                            {row.question_text}
                          </td>
                          <td className="max-w-[280px] px-3 py-2 text-xs leading-relaxed break-words text-muted-foreground">
                            {row.answer_text}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
              {nextCursor ? (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={loadingMore}
                  onClick={() => void loadMoreTurns()}
                >
                  {loadingMore ? "Загрузка…" : "Ещё"}
                </Button>
              ) : null}
            </CardContent>
          </Card>

          <Card className="border-border/80">
            <CardHeader className="pb-2">
              <CardTitle className="font-mono text-base">
                Последние сдачи
              </CardTitle>
              <CardDescription>Нажмите строку — отчёт и ссылки</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="divide-y divide-border rounded-md border border-border">
                {dashboard.recent_submissions.length === 0 ? (
                  <li className="px-3 py-6 text-center text-sm text-muted-foreground">
                    Нет сдач
                  </li>
                ) : (
                  dashboard.recent_submissions.map((s) => (
                    <li key={`${s.membership_id}-${s.checkpoint_id}-${s.updated_at}`}>
                      <button
                        type="button"
                        className="flex w-full flex-col gap-0.5 px-3 py-3 text-left text-sm transition-colors hover:bg-muted/50"
                        onClick={() => {
                          setSelectedSubmission(s);
                          setSheetOpen(true);
                        }}
                      >
                        <span className="font-medium">
                          {s.student_display_name ?? "Студент"} · {s.checkpoint_title}
                        </span>
                        <span className="font-mono text-xs text-muted-foreground">
                          {formatAskedAt(s.updated_at)}
                        </span>
                      </button>
                    </li>
                  ))
                )}
              </ul>
            </CardContent>
          </Card>

          <Card className="border-border/80">
            <CardHeader className="pb-2">
              <CardTitle className="font-mono text-base">
                Матрица прогресса
              </CardTitle>
              <CardDescription>
                Студенты × этапы; при наведении на ячейку — дата обновления
              </CardDescription>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              <MatrixTable rows={dashboard.matrix} columns={matrixColumns} />
            </CardContent>
          </Card>
        </>
      ) : null}

      <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
        <SheetContent side="right" className="w-full sm:max-w-md">
          <SheetHeader>
            <SheetTitle className="font-mono text-sm">Сдача</SheetTitle>
            <SheetDescription>
              {selectedSubmission
                ? `${selectedSubmission.student_display_name ?? "Студент"} · ${selectedSubmission.checkpoint_title}`
                : ""}
            </SheetDescription>
          </SheetHeader>
          {selectedSubmission ? (
            <div className="flex flex-col gap-4 px-4 pb-6 text-sm">
              <div>
                <div className="font-mono text-xs text-muted-foreground">
                  Обновлено
                </div>
                <div>{formatAskedAt(selectedSubmission.updated_at)}</div>
              </div>
              <div>
                <div className="font-mono text-xs text-muted-foreground">
                  Отчёт
                </div>
                <pre className="mt-1 max-h-48 overflow-auto whitespace-pre-wrap rounded-md border border-border bg-muted/30 p-3 font-mono text-xs">
                  {selectedSubmission.comment?.trim() || "—"}
                </pre>
              </div>
              <div>
                <div className="font-mono text-xs text-muted-foreground">
                  Ссылки
                </div>
                {selectedSubmission.submission_links &&
                selectedSubmission.submission_links.length > 0 ? (
                  <ul className="mt-2 space-y-2">
                    {selectedSubmission.submission_links.map((link) => (
                      <li key={link}>
                        <a
                          href={link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="break-all text-primary underline-offset-4 hover:underline"
                        >
                          {link}
                        </a>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-1 text-muted-foreground">Нет ссылок</p>
                )}
              </div>
            </div>
          ) : null}
        </SheetContent>
      </Sheet>
    </div>
  );
}

function KpiCard({
  title,
  description,
  current,
  previous,
  suffix = "",
  formatDelta,
}: {
  title: string;
  description: string;
  current: number;
  previous: number;
  suffix?: string;
  formatDelta: (current: number, previous: number) => string;
}) {
  return (
    <Card className="border-border/80">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium leading-snug">{title}</CardTitle>
        <CardDescription className="text-xs">{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="font-mono text-3xl font-semibold tracking-tight">
          {suffix === "%" ? current.toFixed(1) : current}
          {suffix}
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Прошлая неделя:{" "}
          <span className="font-mono text-foreground">
            {suffix === "%" ? previous.toFixed(1) : previous}
            {suffix}
          </span>
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          {formatDelta(current, previous)}
        </p>
      </CardContent>
    </Card>
  );
}

function MatrixTable({
  rows,
  columns,
}: {
  rows: DashboardMatrixRow[];
  columns: { checkpoint_id: string; index: number }[];
}) {
  if (rows.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-muted-foreground">
        Нет студентов в потоке
      </p>
    );
  }

  return (
    <table className="w-full min-w-max border-collapse text-left text-xs">
      <thead>
        <tr className="border-b border-border bg-muted/40 font-mono uppercase tracking-wide text-muted-foreground">
          <th className="sticky left-0 z-10 bg-muted/95 px-2 py-2 backdrop-blur-sm">
            Студент
          </th>
          {columns.map((c) => (
            <th
              key={c.checkpoint_id}
              className="whitespace-nowrap px-1 py-2 text-center font-mono"
              title={c.checkpoint_id}
            >
              {c.index}
            </th>
          ))}
          <th className="whitespace-nowrap px-2 py-2 text-center">Счёт</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr
            key={row.membership_id}
            className="border-b border-border/60 last:border-0"
          >
            <td className="sticky left-0 z-10 bg-card/95 px-2 py-1.5 backdrop-blur-sm">
              <span className="font-medium">
                {row.display_name ?? "—"}
              </span>
            </td>
            {row.cells.map((cell) => (
              <td key={cell.checkpoint_id} className="p-0.5 text-center">
                <div
                  className={cn(
                    "mx-auto h-6 w-6 rounded-sm",
                    cellTone(cell.status),
                  )}
                  title={formatUpdatedTooltip(cell.updated_at)}
                />
              </td>
            ))}
            <td className="whitespace-nowrap px-2 py-1.5 text-center font-mono">
              {row.score_completed}/{row.score_total}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
