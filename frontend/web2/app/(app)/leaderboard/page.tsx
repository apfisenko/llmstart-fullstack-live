"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { LeaderboardScatter } from "@/components/leaderboard-scatter";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { Button, buttonVariants } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { LeaderboardResponse } from "@/lib/leaderboard-types";
import { readWebSession, type WebSession } from "@/lib/session";
import type { ApiErrorBody } from "@/lib/teacher-dashboard-types";
import { cn } from "@/lib/utils";

type ViewMode = "table" | "scatter";

export default function LeaderboardPage() {
  const [session, setSession] = useState<WebSession | null | undefined>(undefined);
  const [view, setView] = useState<ViewMode>("table");
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSession(readWebSession());
  }, []);

  const fetchLeaderboard = useCallback(async (s: WebSession) => {
    const params = new URLSearchParams({
      viewer_membership_id: s.membership_id,
    });
    const url = `/api/v1/cohorts/${encodeURIComponent(s.cohort_id)}/leaderboard?${params.toString()}`;
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
    return parsed as LeaderboardResponse;
  }, []);

  useEffect(() => {
    if (session === undefined || session === null) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const lb = await fetchLeaderboard(session);
        if (!cancelled) setData(lb);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Ошибка загрузки");
          setData(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [session, fetchLeaderboard]);

  if (session === undefined) {
    return (
      <div className="text-sm text-muted-foreground">Загрузка сессии…</div>
    );
  }

  if (session === null) {
    return (
      <Card className="max-w-lg border-border/80">
        <CardHeader>
          <CardTitle className="font-mono text-lg">Лидерборд</CardTitle>
          <CardDescription>
            Войдите по Telegram username, чтобы открыть данные потока.
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

  const title = session.cohort_title?.trim() || "Поток";

  return (
    <div className="flex min-w-0 flex-col gap-6 pb-10">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="font-mono text-xl font-semibold tracking-tight">
            Лидерборд
          </h1>
          <p className="mt-1 font-mono text-sm text-muted-foreground">{title}</p>
        </div>
        <div
          className="flex shrink-0 gap-1 rounded-lg border border-border bg-card/40 p-1"
          role="group"
          aria-label="Вид отображения"
        >
          <Button
            type="button"
            size="sm"
            variant={view === "table" ? "secondary" : "ghost"}
            className="font-mono text-xs"
            aria-pressed={view === "table"}
            onClick={() => setView("table")}
          >
            Таблица
          </Button>
          <Button
            type="button"
            size="sm"
            variant={view === "scatter" ? "secondary" : "ghost"}
            className="font-mono text-xs"
            aria-pressed={view === "scatter"}
            onClick={() => setView("scatter")}
          >
            Карта
          </Button>
        </div>
      </div>

      {error ? (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}

      {loading && !data ? (
        <p className="text-sm text-muted-foreground">Загрузка данных…</p>
      ) : null}

      {data && !loading && data.entries.length === 0 ? (
        <p className="text-sm text-muted-foreground">В потоке пока нет студентов в рейтинге.</p>
      ) : null}

      {data && data.entries.length > 0 ? (
        <Card className="border-border/80">
          <CardContent className="pt-6">
            {view === "table" ? (
              <LeaderboardTable data={data} />
            ) : (
              <LeaderboardScatter entries={data.entries} />
            )}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
