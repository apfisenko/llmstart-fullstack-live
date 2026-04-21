/** Типы ответов API диалога (snake_case как в backend / OpenAPI). */

export type PostDialogueMessageRequest = {
  membership_id: string;
  channel: "web";
  content: string;
  dialogue_id?: string | null;
};

export type PostDialogueMessageResponse = {
  dialogue_id: string;
  user_message_id: string;
  assistant_message: {
    id: string;
    content: string;
    created_at: string;
  };
};

export type DialogueTurnListItem = {
  user_message_id: string;
  assistant_message_id: string;
  question_text: string;
  answer_text: string;
  asked_at: string;
  answered_at: string;
};

export type DialogueTurnsListResponse = {
  items: DialogueTurnListItem[];
  next_before_asked_at: string | null;
};

export type ApiErrorBody = {
  error?: { code?: string; message?: string; details?: unknown };
};

export function parseApiErrorMessage(raw: string): string {
  try {
    const j = JSON.parse(raw) as ApiErrorBody;
    const m = j.error?.message;
    if (typeof m === "string" && m.trim()) {
      return m.trim();
    }
  } catch {
    /* ignore */
  }
  return "Произошла ошибка";
}
