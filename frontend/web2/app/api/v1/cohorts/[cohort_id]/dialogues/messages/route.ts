import { NextRequest, NextResponse } from "next/server";

import {
  backendAuthHeaders,
  readBackendEnv,
  upstreamUnreachableResponse,
} from "@/lib/server-backend";

export async function POST(
  req: NextRequest,
  ctx: { params: Promise<{ cohort_id: string }> },
) {
  const env = readBackendEnv();
  if ("error" in env) {
    return env.error;
  }

  const { cohort_id } = await ctx.params;
  const url = `${env.origin}/api/v1/cohorts/${encodeURIComponent(cohort_id)}/dialogues/messages`;

  let body: string;
  try {
    body = await req.text();
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "BAD_REQUEST",
          message: "Некорректное тело запроса",
          details: null,
        },
      },
      { status: 400 },
    );
  }

  let upstream: Response;
  try {
    upstream = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...backendAuthHeaders(env.token),
      },
      body,
      cache: "no-store",
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
