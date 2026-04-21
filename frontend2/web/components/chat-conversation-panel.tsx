"use client";

import { Bot } from "lucide-react";
import { useEffect, useRef } from "react";

import { Button } from "@/components/ui/button";
import type { WebDialogueChatState } from "@/hooks/use-web-dialogue-chat";
import type { WebSession } from "@/lib/session";
import { cn } from "@/lib/utils";

type ChatConversationPanelProps = {
  session: WebSession;
  chat: WebDialogueChatState;
  rootClassName?: string;
  scrollAreaClassName?: string;
  footerClassName?: string;
  textareaRows?: number;
};

export function ChatConversationPanel({
  session,
  chat,
  rootClassName,
  scrollAreaClassName,
  footerClassName,
  textareaRows = 3,
}: ChatConversationPanelProps) {
  const {
    lines,
    draft,
    setDraft,
    historyLoading,
    historyError,
    sending,
    sendError,
    onSubmit,
  } = chat;

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) {
      return;
    }
    el.scrollTop = el.scrollHeight;
  }, [lines, sending, historyLoading]);

  return (
    <div className={cn("flex min-h-0 flex-1 flex-col", rootClassName)}>
      <div
        ref={scrollRef}
        className={cn(
          "min-h-0 flex-1 overflow-y-auto px-3 py-3 font-mono text-sm",
          scrollAreaClassName,
        )}
      >
        {historyLoading ? (
          <p className="text-xs text-zinc-500">загрузка истории…</p>
        ) : null}
        {historyError ? (
          <p className="text-xs text-red-400" role="alert">
            {historyError}
          </p>
        ) : null}
        {!historyLoading && lines.length === 0 && !historyError ? (
          <p className="text-xs text-zinc-500">
            {session.web_dialogue_id
              ? "> Нет сообщений. Напишите ниже."
              : "> Новый диалог. Отправьте первое сообщение."}
          </p>
        ) : null}
        <div className="flex flex-col gap-3">
          {lines.map((line) =>
            line.role === "assistant" ? (
              <div
                key={line.key}
                className="flex max-w-[95%] items-start gap-2 self-start md:max-w-[80%]"
              >
                <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-zinc-800 text-zinc-300">
                  <Bot className="h-4 w-4" aria-hidden />
                </span>
                <div
                  className={cn(
                    "rounded-lg rounded-tl-none border border-zinc-700/80 bg-zinc-900/90 px-3 py-2",
                    "whitespace-pre-wrap text-zinc-100",
                  )}
                >
                  {line.text}
                </div>
              </div>
            ) : (
              <div key={line.key} className="flex max-w-[90%] flex-col self-end md:max-w-[70%]">
                <div
                  className={cn(
                    "rounded-lg rounded-tr-none border border-emerald-900/60 bg-emerald-950/50 px-3 py-2",
                    "whitespace-pre-wrap text-zinc-100",
                  )}
                >
                  {line.text}
                </div>
              </div>
            ),
          )}
        </div>
        {sending ? (
          <p className="mt-2 text-xs text-zinc-500">ожидание ответа…</p>
        ) : null}
      </div>

      <div className={cn("shrink-0 border-t border-border/60 bg-zinc-950", footerClassName)}>
        {sendError ? (
          <p className="px-3 pt-2 text-xs text-red-400" role="alert">
            {sendError}
          </p>
        ) : null}
        <form className="flex w-full flex-col gap-2 p-3" onSubmit={onSubmit}>
          <textarea
            name="message"
            rows={textareaRows}
            value={draft}
            onChange={(ev) => setDraft(ev.target.value)}
            disabled={sending}
            placeholder="> введите сообщение…"
            className={cn(
              "w-full resize-none rounded-md border border-zinc-700 bg-zinc-900/80 px-3 py-2 text-sm text-zinc-100",
              "placeholder:text-zinc-600 focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] outline-none",
            )}
            autoComplete="off"
          />
          <Button type="submit" className="w-full font-mono text-xs" disabled={sending}>
            {sending ? "Отправка…" : "Отправить"}
          </Button>
        </form>
      </div>
    </div>
  );
}
