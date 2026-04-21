"use client";

import { RotateCcw } from "lucide-react";

import { ChatConversationPanel } from "@/components/chat-conversation-panel";
import { useWebDialogueChatContext } from "@/components/web-dialogue-chat-context";
import { useWebSession } from "@/components/web-session-context";
import { Button } from "@/components/ui/button";

export default function ChatMainPage() {
  const { session } = useWebSession();
  const chat = useWebDialogueChatContext();

  return (
    <div className="flex min-h-0 flex-1 flex-col bg-zinc-950/40">
      <div className="flex shrink-0 flex-col gap-1 border-b border-border/60 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-2">
        <div className="min-w-0">
          <h1 className="font-mono text-sm font-semibold tracking-tight text-zinc-100">Чат</h1>
          <p className="font-mono text-xs text-zinc-500">
            Канал web · поток {session.cohort_title ?? `${session.cohort_id.slice(0, 8)}…`}
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="shrink-0 self-start font-mono text-xs sm:self-auto"
          disabled={!session.web_dialogue_id || chat.resetting || chat.sending}
          onClick={() => void chat.onReset()}
        >
          <RotateCcw className="mr-1 h-3.5 w-3.5" />
          {chat.resetting ? "…" : "Сброс контекста"}
        </Button>
      </div>

      <ChatConversationPanel session={session} chat={chat} textareaRows={5} />
    </div>
  );
}
