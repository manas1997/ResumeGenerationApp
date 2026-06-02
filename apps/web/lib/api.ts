import type { TailoringRequest, TailoringResponse } from "@/types/tailoring";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function createTailoringRun(payload: TailoringRequest): Promise<TailoringResponse> {
  const response = await fetch(`${API_URL}/api/v1/tailoring-runs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail ?? "Request failed");
  }

  return response.json();
}

