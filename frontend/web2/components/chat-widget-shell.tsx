"use client";

import { MessageSquare, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";

import { ChatConversationPanel } from "@/components/chat-conversation-panel";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useWebDialogueChatContext } from "@/components/web-dialogue-chat-context";
import { useWebSession } from "@/components/web-session-context";

export function ChatWidgetShell() {
  const { session } = useWebSession();
  const chat = useWebDialogueChatContext();
  const { fetchHistory } = chat;
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) {
      return;
    }
    return fetchHistory();
  }, [open, fetchHistory]);

  return (
    <>
      <Button
        type="button"
        size="icon"
        className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full shadow-lg"
        onClick={() => setOpen(true)}
        aria-label="Открыть чат с ассистентом"
      >
        <MessageSquare className="h-6 w-6" />
      </Button>
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent
          side="right"
          showCloseButton
          className="flex w-full flex-col gap-0 border-l bg-zinc-950 p-0 sm:max-w-md"
        >
          <SheetHeader className="shrink-0 flex-row items-center justify-between gap-2 border-b border-border/60 bg-zinc-950 pr-14">
            <div className="min-w-0 flex-1">
              <SheetTitle className="font-mono text-sm tracking-tight text-zinc-100">
                assistant
              </SheetTitle>
              <SheetDescription className="font-mono text-xs text-zinc-500">
                Канал web · поток {session.cohort_title ?? session.cohort_id.slice(0, 8)}…
              </SheetDescription>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="shrink-0 font-mono text-xs"
              disabled={!session.web_dialogue_id || chat.resetting || chat.sending}
              onClick={() => void chat.onReset()}
            >
              <RotateCcw className="mr-1 h-3.5 w-3.5" />
              {chat.resetting ? "…" : "Сброс"}
            </Button>
          </SheetHeader>

          <ChatConversationPanel session={session} chat={chat} />
        </SheetContent>
      </Sheet>
    </>
  );
}
