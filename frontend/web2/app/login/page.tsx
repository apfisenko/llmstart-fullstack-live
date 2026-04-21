"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  buildWebSession,
  readWebSession,
  writeWebSession,
  type DevSessionResponse,
} from "@/lib/session";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (readWebSession()) {
      router.replace("/teacher");
    }
  }, [router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const trimmed = username.trim().replace(/^@+/, "");
    if (!trimmed) {
      setError("Введите Telegram username");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/v1/auth/dev-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_username: trimmed }),
      });
      const raw = await res.text();
      let data: unknown;
      try {
        data = JSON.parse(raw) as unknown;
      } catch {
        setError("Некорректный ответ сервера");
        return;
      }
      if (!res.ok) {
        const err = data as { error?: { message?: string } };
        setError(err.error?.message ?? `Ошибка ${res.status}`);
        return;
      }
      const session = buildWebSession(data as DevSessionResponse);
      if (!session) {
        setError("У пользователя нет участий в потоках");
        return;
      }
      writeWebSession(session);
      router.replace("/teacher");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md border-border/80 shadow-xl">
        <CardHeader>
          <CardTitle className="font-mono text-lg">Вход</CardTitle>
          <CardDescription>
            Идентификация только по Telegram username: значение уходит на backend в{" "}
            <span className="font-mono text-xs">POST /api/v1/auth/dev-session</span>, где
            проверяется по базе. Пароль и OAuth не используются.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Telegram username</Label>
              <Input
                id="username"
                name="username"
                autoComplete="off"
                placeholder="username или @username"
                value={username}
                onChange={(ev) => setUsername(ev.target.value)}
                disabled={loading}
              />
            </div>
            {error ? (
              <p className="text-sm text-destructive" role="alert">
                {error}
              </p>
            ) : null}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Вход…" : "Войти"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
