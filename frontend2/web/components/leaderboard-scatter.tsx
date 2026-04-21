"use client";

import { useMemo, useState } from "react";

import type { LeaderboardEntry } from "@/lib/leaderboard-types";
import { cn } from "@/lib/utils";

type Props = {
  entries: LeaderboardEntry[];
  className?: string;
};

function entryName(e: LeaderboardEntry): string {
  const n = e.display_name?.trim();
  if (n) return n;
  return `Участник ${e.membership_id.slice(0, 8)}…`;
}

export function LeaderboardScatter({ entries, className }: Props) {
  const [hoverId, setHoverId] = useState<string | null>(null);

  const plot = useMemo(() => {
    const w = 560;
    const h = 360;
    const padL = 48;
    const padR = 24;
    const padT = 24;
    const padB = 48;
    const innerW = w - padL - padR;
    const innerH = h - padT - padB;
    return { w, h, padL, padR, padT, padB, innerW, innerH };
  }, []);

  const { w, h, padL, padT, padB, innerW, innerH } = plot;

  const points = entries
    .map((e) => {
      const sx = e.scatter_x;
      const sy = e.scatter_y;
      if (sx == null || sy == null) return null;
      const x = padL + Math.min(1, Math.max(0, sx)) * innerW;
      const y = padT + innerH - Math.min(1, Math.max(0, sy)) * innerH;
      return { entry: e, x, y, sx, sy };
    })
    .filter((p): p is NonNullable<typeof p> => p !== null);

  const hovered = hoverId
    ? points.find((p) => p.entry.membership_id === hoverId)
    : null;

  const tipW = 168;
  const tipH = 88;
  let tipX = hovered ? hovered.x + 12 : 0;
  let tipY = hovered ? hovered.y - tipH - 8 : 0;
  if (hovered) {
    if (tipX + tipW > w - 8) tipX = hovered.x - tipW - 12;
    if (tipX < 8) tipX = 8;
    if (tipY < padT + 4) tipY = hovered.y + 14;
    if (tipY + tipH > h - padB) tipY = h - padB - tipH - 4;
  }

  if (points.length === 0) {
    return (
      <div
        className={cn(
          "flex min-h-[280px] items-center justify-center rounded-lg border border-border bg-card/30 text-sm text-muted-foreground",
          className,
        )}
      >
        Нет координат для карты (нет завершённых этапов по типам урок/ДЗ)
      </div>
    );
  }

  return (
    <div className={cn(className)}>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        className="h-auto w-full max-w-full text-muted-foreground"
        role="img"
        aria-label="Карта прогресса: уроки и домашки"
      >
        <rect
          x={padL}
          y={padT}
          width={innerW}
          height={innerH}
          className="fill-card/40 stroke-border"
          strokeWidth={1}
          rx={4}
        />
        <line
          x1={padL}
          y1={padT + innerH}
          x2={padL + innerW}
          y2={padT + innerH}
          className="stroke-border"
          strokeWidth={1}
        />
        <line
          x1={padL}
          y1={padT}
          x2={padL}
          y2={padT + innerH}
          className="stroke-border"
          strokeWidth={1}
        />
        <text
          x={padL + innerW / 2}
          y={h - 12}
          textAnchor="middle"
          className="fill-muted-foreground font-mono text-[11px]"
        >
          Уроки (доля завершённых)
        </text>
        <text
          x={14}
          y={padT + innerH / 2}
          className="fill-muted-foreground font-mono text-[11px]"
          transform={`rotate(-90 14 ${padT + innerH / 2})`}
          textAnchor="middle"
        >
          Домашки (доля завершённых)
        </text>
        {points.map((p) => (
          <g key={p.entry.membership_id}>
            <circle
              cx={p.x}
              cy={p.y}
              r={16}
              className="cursor-pointer fill-transparent"
              onMouseEnter={() => setHoverId(p.entry.membership_id)}
              onMouseLeave={() => setHoverId(null)}
            />
            <circle
              cx={p.x}
              cy={p.y}
              r={p.entry.rank <= 3 ? 6 : 4.5}
              className={cn(
                "stroke-background stroke-[1.5]",
                p.entry.rank === 1 && "fill-amber-400",
                p.entry.rank === 2 && "fill-slate-300",
                p.entry.rank === 3 && "fill-amber-700",
                p.entry.rank > 3 && "fill-primary",
              )}
              onMouseEnter={() => setHoverId(p.entry.membership_id)}
              onMouseLeave={() => setHoverId(null)}
            />
            <title>
              {`${entryName(p.entry)} — уроки: ${p.entry.lesson_completed}, ДЗ: ${p.entry.homework_completed}, ${p.entry.progress_percent.toFixed(0)}%, место ${p.entry.rank}`}
            </title>
          </g>
        ))}

        {hovered ? (
          <g pointerEvents="none">
            <rect
              x={tipX}
              y={tipY}
              width={tipW}
              height={tipH}
              rx={6}
              className="fill-popover stroke-border"
              strokeWidth={1}
            />
            <text
              x={tipX + 10}
              y={tipY + 18}
              className="fill-foreground font-mono text-[11px] font-medium"
            >
              {entryName(hovered.entry).length > 22
                ? `${entryName(hovered.entry).slice(0, 21)}…`
                : entryName(hovered.entry)}
            </text>
            <text
              x={tipX + 10}
              y={tipY + 38}
              className="fill-muted-foreground font-mono text-[10px]"
            >
              {`Уроки: ${hovered.entry.lesson_completed}  ДЗ: ${hovered.entry.homework_completed}`}
            </text>
            <text
              x={tipX + 10}
              y={tipY + 54}
              className="fill-muted-foreground font-mono text-[10px]"
            >
              {`Прогресс: ${hovered.entry.progress_percent.toFixed(0)}%  Место: ${hovered.entry.rank}`}
            </text>
          </g>
        ) : null}
      </svg>
    </div>
  );
}
