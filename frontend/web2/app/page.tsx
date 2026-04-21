"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { readWebSession } from "@/lib/session";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    if (readWebSession()) {
      router.replace("/teacher");
    } else {
      router.replace("/login");
    }
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
      Загрузка…
    </div>
  );
}
