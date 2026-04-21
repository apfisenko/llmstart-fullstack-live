import { NextRequest, NextResponse } from "next/server";

import {
  backendAuthHeaders,
  readBackendEnv,
  upstreamUnreachableResponse,
} from "@/lib/server-backend";

export async function POST(req: NextRequest) {
  const env = readBackendEnv();
  if ("error" in env) {
    return env.error;
  }

  const body = await req.text();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...backendAuthHeaders(env.token),
  };

  let upstream: Response;
  try {
    upstream = await fetch(`${env.origin}/api/v1/auth/dev-session`, {
      method: "POST",
      headers,
      body,
    });
  } catch {
    return upstreamUnreachableResponse();
  }

  const text = await upstream.text();
  const contentType =
    upstream.headers.get("content-type") ?? "application/json";
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": contentType },
  });
}
