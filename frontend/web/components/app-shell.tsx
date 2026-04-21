"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ChatWidgetShell } from "@/components/chat-widget-shell";
import { WebDialogueChatProvider } from "@/components/web-dialogue-chat-context";
import { WebSessionProvider } from "@/components/web-session-context";
import { Button } from "@/components/ui/button";
import { clearWebSession, readWebSession, type WebSession } from "@/lib/session";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/teacher", label: "Панель преподавателя" },
  { href: "/leaderboard", label: "Лидерборд" },
  { href: "/student", label: "Кабинет студента" },
  { href: "/chat", label: "Чат" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [session, setSession] = useState<WebSession | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const s = readWebSession();
    if (!s) {
      router.replace("/login");
      return;
    }
    const t = window.setTimeout(() => {
      setSession(s);
      setReady(true);
    }, 0);
    return () => window.clearTimeout(t);
  }, [router]);

  function logout() {
    clearWebSession();
    router.replace("/login");
  }

  if (!ready || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        Загрузка…
      </div>
    );
  }

  const isChatRoute = pathname === "/chat";

  return (
    <WebSessionProvider value={{ session, setSession }}>
      <WebDialogueChatProvider>
        <div className="flex min-h-screen bg-background">
          <aside className="flex w-56 shrink-0 flex-col border-r border-border bg-card/40">
            <div className="border-b border-border px-4 py-3 font-mono text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              LLMStart
            </div>
            <nav className="flex flex-1 flex-col gap-0.5 p-2">
              {nav.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "rounded-md px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
                    pathname === item.href && "bg-accent text-accent-foreground",
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </aside>
          <div className="relative flex min-h-0 min-w-0 flex-1 flex-col">
            <header className="flex h-12 shrink-0 items-center justify-between border-b border-border px-4">
              <span className="truncate text-sm text-muted-foreground">
                {session.display_name ?? "Пользователь"} ·{" "}
                <span className="font-mono text-xs">
                  {session.role === "teacher" ? "преподаватель" : "студент"}
                </span>
              </span>
              <Button type="button" variant="outline" size="sm" onClick={logout}>
                Выход
              </Button>
            </header>
            <main
              className={cn(
                "flex-1",
                isChatRoute
                  ? "flex min-h-0 flex-col overflow-hidden p-0"
                  : "overflow-auto p-6",
              )}
            >
              {children}
            </main>
            <ChatWidgetShell />
          </div>
        </div>
      </WebDialogueChatProvider>
    </WebSessionProvider>
  );
}
