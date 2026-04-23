"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

import {
  type DialogueTurnListItem,
  type DialogueTurnsListResponse,
  type PostDialogueMessageResponse,
  parseApiErrorMessage,
} from "@/lib/dialogue-api";
import { patchWebSession, type WebSession } from "@/lib/session";

export type WebDialogueChatLine = {
  key: string;
  role: "user" | "assistant";
  text: string;
};

function turnsToLines(items: DialogueTurnListItem[]): WebDialogueChatLine[] {
  const out: WebDialogueChatLine[] = [];
  for (const t of items) {
    out.push({
      key: `${t.user_message_id}-u`,
      role: "user",
      text: t.question_text,
    });
    out.push({
      key: `${t.user_message_id}-a`,
      role: "assistant",
      text: t.answer_text,
    });
  }
  return out;
}

export function useWebDialogueChat(
  session: WebSession,
  onSessionChange: (s: WebSession) => void,
) {
  const [lines, setLines] = useState<WebDialogueChatLine[]>([]);
  const [draft, setDraft] = useState("");
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [resetting, setResetting] = useState(false);

  const loadTurns = useCallback(
    (signal: AbortSignal) => {
      const dialogueId = session.web_dialogue_id;
      if (!dialogueId) {
        setLines([]);
        setHistoryError(null);
        setHistoryLoading(false);
        return Promise.resolve();
      }

      setHistoryLoading(true);
      setHistoryError(null);

      const url = `/api/v1/dialogues/${encodeURIComponent(dialogueId)}/turns?limit=50`;
      return fetch(url, { method: "GET", cache: "no-store", signal })
        .then(async (res) => {
          const raw = await res.text();
          if (signal.aborted) {
            return;
          }
          if (!res.ok) {
            setHistoryError(parseApiErrorMessage(raw));
            setLines([]);
            return;
          }
          let data: DialogueTurnsListResponse;
          try {
            data = JSON.parse(raw) as DialogueTurnsListResponse;
          } catch {
            setHistoryError("Некорректный ответ сервера");
            setLines([]);
            return;
          }
          setLines(turnsToLines(data.items ?? []));
        })
        .catch((err: unknown) => {
          if (signal.aborted || (err instanceof DOMException && err.name === "AbortError")) {
            return;
          }
          setHistoryError("Не удалось загрузить историю");
          setLines([]);
        })
        .finally(() => {
          if (!signal.aborted) {
            setHistoryLoading(false);
          }
        });
    },
    [session.web_dialogue_id],
  );

  useEffect(() => {
    const ac = new AbortController();
    void loadTurns(ac.signal);
    return () => ac.abort();
  }, [loadTurns]);

  const fetchHistory = useCallback(() => {
    const ac = new AbortController();
    void loadTurns(ac.signal);
    return () => ac.abort();
  }, [loadTurns]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const text = draft.trim();
    if (!text || sending) {
      return;
    }
    setSending(true);
    setSendError(null);
    try {
      const res = await fetch(
        `/api/v1/cohorts/${encodeURIComponent(session.cohort_id)}/dialogues/messages`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            membership_id: session.membership_id,
            channel: "web",
            content: text,
            dialogue_id: session.web_dialogue_id ?? null,
          }),
        },
      );
      const raw = await res.text();
      if (!res.ok) {
        const detail = parseApiErrorMessage(raw);
        if (res.status === 502 || res.status === 503) {
          setSendError(
            detail && detail !== "Произошла ошибка"
              ? `Ассистент временно недоступен (${detail})`
              : "Ассистент временно недоступен. Попробуйте позже.",
          );
        } else {
          setSendError(detail);
        }
        return;
      }
      let data: PostDialogueMessageResponse;
      try {
        data = JSON.parse(raw) as PostDialogueMessageResponse;
      } catch {
        setSendError("Некорректный ответ сервера");
        return;
      }
      const next = patchWebSession({ web_dialogue_id: data.dialogue_id });
      if (next) {
        onSessionChange(next);
      }
      setDraft("");
      setLines((prev) => [
        ...prev,
        {
          key: `${data.user_message_id}-u`,
          role: "user",
          text,
        },
        {
          key: `${data.user_message_id}-a`,
          role: "assistant",
          text: data.assistant_message.content,
        },
      ]);
    } finally {
      setSending(false);
    }
  }

  async function onReset() {
    const id = session.web_dialogue_id;
    if (!id || resetting || sending) {
      return;
    }
    setResetting(true);
    setSendError(null);
    try {
      const res = await fetch(`/api/v1/dialogues/${encodeURIComponent(id)}/reset`, {
        method: "POST",
        cache: "no-store",
      });
      if (!res.ok && res.status !== 204) {
        const raw = await res.text();
        setSendError(parseApiErrorMessage(raw));
        return;
      }
      setLines([]);
    } finally {
      setResetting(false);
    }
  }

  return {
    lines,
    draft,
    setDraft,
    historyLoading,
    historyError,
    sending,
    sendError,
    resetting,
    fetchHistory,
    onSubmit,
    onReset,
  };
}

export type WebDialogueChatState = ReturnType<typeof useWebDialogueChat>;
