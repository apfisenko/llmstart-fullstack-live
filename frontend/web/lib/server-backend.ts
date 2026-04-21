import { NextResponse } from "next/server";

export type BackendEnv =
  | { origin: string; token: string }
  | { error: NextResponse };

export function readBackendEnv(): BackendEnv {
  const origin = process.env.BACKEND_ORIGIN?.trim().replace(/\/$/, "") ?? "";
  const token = process.env.BACKEND_API_CLIENT_TOKEN?.trim() ?? "";
  if (!origin) {
    return {
      error: NextResponse.json(
        {
          error: {
            code: "WEB_CONFIG",
            message:
              "Задайте BACKEND_ORIGIN в frontend/web/.env.local (например http://127.0.0.1:8000)",
            details: null,
          },
        },
        { status: 500 },
      ),
    };
  }
  return { origin, token };
}

export function backendAuthHeaders(token: string): Record<string, string> {
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export function upstreamUnreachableResponse(): NextResponse {
  return NextResponse.json(
    {
      error: {
        code: "UPSTREAM_UNREACHABLE",
        message: "Не удалось связаться с backend",
        details: null,
      },
    },
    { status: 502 },
  );
}
