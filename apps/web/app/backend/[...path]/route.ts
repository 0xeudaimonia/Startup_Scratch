import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const API_INTERNAL_URL = process.env.API_INTERNAL_URL || "http://localhost:8000";

async function proxy(request: NextRequest, path: string[]) {
  const search = request.nextUrl.search;
  const url = `${API_INTERNAL_URL}/${path.join("/")}${search}`;
  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);
  const body = ["GET", "HEAD"].includes(request.method) ? undefined : await request.text();
  const response = await fetch(url, { method: request.method, headers, body, cache: "no-store" });
  const payload = await response.arrayBuffer();
  return new Response(payload, {
    status: response.status,
    headers: {
      "content-type": response.headers.get("content-type") || "application/json",
    },
  });
}

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return proxy(request, path);
}

export async function POST(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  return proxy(request, path);
}
