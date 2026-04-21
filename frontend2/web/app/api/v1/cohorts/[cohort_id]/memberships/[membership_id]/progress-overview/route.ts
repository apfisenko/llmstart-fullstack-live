import { NextRequest, NextResponse } from "next/server";

import {
  backendAuthHeaders,
  readBackendEnv,
  upstreamUnreachableResponse,
} from "@/lib/server-backend";

export async function GET(
  _req: NextRequest,
  ctx: { params: Promise<{ cohort_id: string; membership_id: string }> },
) {
  const env = readBackendEnv();
  if ("error" in env) {
    return env.error;
  }

  const { cohort_id, membership_id } = await ctx.params;
  const url = `${env.origin}/api/v1/cohorts/${encodeURIComponent(cohort_id)}/memberships/${encodeURIComponent(membership_id)}/progress-overview`;

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
