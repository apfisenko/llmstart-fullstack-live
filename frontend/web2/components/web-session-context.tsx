"use client";

import { createContext, useContext } from "react";

import type { WebSession } from "@/lib/session";

export type WebSessionContextValue = {
  session: WebSession;
  setSession: (s: WebSession) => void;
};

const WebSessionContext = createContext<WebSessionContextValue | null>(null);

export function WebSessionProvider({
  value,
  children,
}: {
  value: WebSessionContextValue;
  children: React.ReactNode;
}) {
  return <WebSessionContext.Provider value={value}>{children}</WebSessionContext.Provider>;
}

export function useWebSession(): WebSessionContextValue {
  const ctx = useContext(WebSessionContext);
  if (!ctx) {
    throw new Error("useWebSession must be used within WebSessionProvider");
  }
  return ctx;
}
