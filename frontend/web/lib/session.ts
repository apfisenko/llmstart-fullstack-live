export const WEB_SESSION_KEY = "llmstart_web_session_v1";

export type WebSession = {
  user_id: string;
  display_name: string | null;
  membership_id: string;
  cohort_id: string;
  role: "student" | "teacher";
  cohort_title: string | null;
  web_dialogue_id: string | null;
};

export type DevSessionMembership = {
  membership_id: string;
  cohort_id: string;
  cohort_title: string | null;
  role: "student" | "teacher";
};

export type DevSessionResponse = {
  user_id: string;
  display_name?: string | null;
  memberships: DevSessionMembership[];
  web_dialogue_id?: string | null;
};

/** Нормализация роли из API (в т.ч. legacy `str(Enum)` → `MembershipRole.teacher`). */
export function normalizeMembershipRole(
  raw: string,
): "student" | "teacher" {
  const r = raw.trim().toLowerCase();
  if (r === "teacher" || r.endsWith(".teacher")) {
    return "teacher";
  }
  return "student";
}

export function pickMembership(
  memberships: DevSessionMembership[],
): DevSessionMembership | null {
  if (memberships.length === 0) {
    return null;
  }
  const teacher = memberships.find(
    (m) => normalizeMembershipRole(m.role) === "teacher",
  );
  const picked = teacher ?? memberships[0] ?? null;
  if (!picked) {
    return null;
  }
  return { ...picked, role: normalizeMembershipRole(picked.role) };
}

export function buildWebSession(data: DevSessionResponse): WebSession | null {
  const m = pickMembership(data.memberships);
  if (!m) {
    return null;
  }
  return {
    user_id: data.user_id,
    display_name: data.display_name ?? null,
    membership_id: m.membership_id,
    cohort_id: m.cohort_id,
    role: m.role,
    cohort_title: m.cohort_title ?? null,
    web_dialogue_id: data.web_dialogue_id ?? null,
  };
}

export function readWebSession(): WebSession | null {
  if (typeof window === "undefined") {
    return null;
  }
  const raw = window.localStorage.getItem(WEB_SESSION_KEY);
  if (!raw) {
    return null;
  }
  try {
    const s = JSON.parse(raw) as WebSession & { role?: string };
    if (typeof s.role !== "string") {
      return null;
    }
    return {
      ...s,
      role: normalizeMembershipRole(s.role),
    };
  } catch {
    return null;
  }
}

export function writeWebSession(session: WebSession): void {
  window.localStorage.setItem(WEB_SESSION_KEY, JSON.stringify(session));
}

/** Частичное обновление сохранённой сессии (например `web_dialogue_id` после первого сообщения). */
export function patchWebSession(
  partial: Partial<Pick<WebSession, "web_dialogue_id">>,
): WebSession | null {
  const current = readWebSession();
  if (!current) {
    return null;
  }
  const next: WebSession = { ...current, ...partial };
  writeWebSession(next);
  return next;
}

export function clearWebSession(): void {
  window.localStorage.removeItem(WEB_SESSION_KEY);
}
