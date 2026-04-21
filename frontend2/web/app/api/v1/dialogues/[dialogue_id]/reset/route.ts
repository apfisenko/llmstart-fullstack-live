import { NextRequest, NextResponse } from "next/server";

import {
  backendAuthHeaders,
  readBackendEnv,
  upstreamUnreachableResponse,
} from "@/lib/server-backend";

export async function POST(
  _req: NextRequest,
  ctx: { params: Promise<{ dialogue_id: string }> },
) {
  const env = readBackendEnv();
  if ("error" in env) {
    return env.error;
  }

  const { dialogue_id } = await ctx.params;
  const url = `${env.origin}/api/v1/dialogues/${encodeURIComponent(dialogue_id)}/reset`;

  let upstream: Response;
  try {
    upstream = await fetch(url, {
      method: "POST",
      headers: {
        ...backendAuthHeaders(env.token),
      },
      cache: "no-store",
    });
  } catch {
    return upstreamUnreachableResponse();
  }

  if (upstream.status === 204) {
    return new NextResponse(null, { status: 204 });
  }

  const text = await upstream.text();
  const contentType =
    upstream.headers.get("content-type") ?? "application/json";
  return new NextResponse(text, {
    status: upstream.status,
    headers: { "Content-Type": contentType },
  });
}
