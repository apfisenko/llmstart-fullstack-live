"use client";

import { createContext, useContext } from "react";

import { useWebSession } from "@/components/web-session-context";
import {
  useWebDialogueChat,
  type WebDialogueChatState,
} from "@/hooks/use-web-dialogue-chat";

const WebDialogueChatContext = createContext<WebDialogueChatState | null>(null);

export function WebDialogueChatProvider({ children }: { children: React.ReactNode }) {
  const { session, setSession } = useWebSession();
  const chat = useWebDialogueChat(session, setSession);
  return (
    <WebDialogueChatContext.Provider value={chat}>{children}</WebDialogueChatContext.Provider>
  );
}

export function useWebDialogueChatContext(): WebDialogueChatState {
  const ctx = useContext(WebDialogueChatContext);
  if (!ctx) {
    throw new Error("useWebDialogueChatContext must be used within WebDialogueChatProvider");
  }
  return ctx;
}
