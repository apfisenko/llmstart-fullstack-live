import { NextRequest, NextResponse } from "next/server";

import {
  backendAuthHeaders,
  readBackendEnv,
  upstreamUnreachableResponse,
} from "@/lib/server-backend";

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ cohort_id: string }> },
) {
  const env = readBackendEnv();
  if ("error" in env) {
    return env.error;
  }

  const { cohort_id } = await ctx.params;
  const search = req.nextUrl.search;
  const url = `${env.origin}/api/v1/cohorts/${encodeURIComponent(cohort_id)}/teacher-dashboard${search}`;

  let upstream: Response;
  try {
    upstream = await fetch(url, {
      method: "GET",
      headers: {
        ...backendAuthHeaders(env.token),
      },
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
