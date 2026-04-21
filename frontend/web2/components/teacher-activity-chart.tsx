"use client";

import type { ActivityByDayItem } from "@/lib/teacher-dashboard-types";

type Props = {
  data: ActivityByDayItem[];
  className?: string;
};

export function TeacherActivityChart({ data, className }: Props) {
  if (data.length === 0) {
    return (
      <div
        className={`flex h-48 items-center justify-center rounded-lg border border-border bg-card/30 text-sm text-muted-foreground ${className ?? ""}`}
      >
        Нет данных за период
      </div>
    );
  }

  const maxY = Math.max(1, ...data.map((d) => d.question_count));
  const w = 640;
  const h = 220;
  const padL = 36;
  const padR = 12;
  const padT = 16;
  const padB = 36;
  const innerW = w - padL - padR;
  const innerH = h - padT - padB;

  const points = data.map((d, i) => {
    const x = padL + (data.length === 1 ? innerW / 2 : (innerW * i) / (data.length - 1));
    const y = padT + innerH - (innerH * d.question_count) / maxY;
    return { x, y, day: d.day, count: d.question_count };
  });

  const pathD = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
    .join(" ");

  const labelEvery = Math.ceil(data.length / 6);

  return (
    <div className={className}>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        className="h-auto w-full max-w-full text-muted-foreground"
        role="img"
        aria-label="Вопросы к ассистенту по дням"
      >
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
        <path
          d={pathD}
          fill="none"
          className="stroke-primary"
          strokeWidth={2}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        {points.map((p) => (
          <circle
            key={p.day}
            cx={p.x}
            cy={p.y}
            r={3.5}
            className="fill-primary stroke-background"
            strokeWidth={1}
          >
            <title>{`${p.day}: ${p.count}`}</title>
          </circle>
        ))}
        {points.map((p, i) =>
          i % labelEvery === 0 || i === data.length - 1 ? (
            <text
              key={`lbl-${p.day}-${i}`}
              x={p.x}
              y={h - 10}
              textAnchor="middle"
              className="fill-muted-foreground font-mono text-[10px]"
            >
              {p.day.slice(5)}
            </text>
          ) : null,
        )}
        <text
          x={8}
          y={padT + innerH / 2}
          className="fill-muted-foreground font-mono text-[10px]"
          transform={`rotate(-90 8 ${padT + innerH / 2})`}
        >
          вопросы
        </text>
      </svg>
    </div>
  );
}
