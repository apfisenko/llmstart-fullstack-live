import { NextRequest, NextResponse } from "next/server";

import {
  backendAuthHeaders,
  readBackendEnv,
  upstreamUnreachableResponse,
} from "@/lib/server-backend";

export async function PUT(
  req: NextRequest,
  ctx: {
    params: Promise<{
      cohort_id: string;
      membership_id: string;
      checkpoint_id: string;
    }>;
  },
) {
  const env = readBackendEnv();
  if ("error" in env) {
    return env.error;
  }

  const { cohort_id, membership_id, checkpoint_id } = await ctx.params;
  const body = await req.text();
  const url = `${env.origin}/api/v1/cohorts/${encodeURIComponent(cohort_id)}/memberships/${encodeURIComponent(membership_id)}/progress-records/${encodeURIComponent(checkpoint_id)}`;

  let upstream: Response;
  try {
    upstream = await fetch(url, {
      method: "PUT",
      headers: {
        ...backendAuthHeaders(env.token),
        "Content-Type":
          req.headers.get("content-type") ?? "application/json",
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
