import { NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";
import type { DiagnosticResponse } from "@/lib/types";

type RequestBody = {
  productId?: string;
  sessionId?: string;
  issue?: string;
  answer?: string;
};

export async function POST(request: Request) {
  const body = (await request.json()) as RequestBody;
  const productId = body.productId || "hp-laserjet-pro-m404n";

  try {
    const response = await fetch(`${API_BASE_URL}/products/${productId}/diagnose`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        issue_description: body.issue,
        session_id: body.sessionId,
        answer: body.answer,
        top_k: 8,
      }),
    });

    if (!response.ok) {
      throw new Error(`Diagnostic API failed: ${response.status}`);
    }

    const payload = (await response.json()) as DiagnosticResponse;
    return NextResponse.json(payload);
  } catch {
    return NextResponse.json(fallbackDiagnostic(body), { status: 200 });
  }
}

function fallbackDiagnostic(body: RequestBody): DiagnosticResponse {
  return {
    session_id: body.sessionId ?? "dx-local-demo",
    probable_causes: ["Drum contamination", "Fuser temperature inconsistency", "Toner cartridge defect"],
    follow_up_question:
      "Does the fading appear in horizontal bands across the page, or as random light patches throughout the page?",
    next_step:
      "Intermittent fading without a toner warning suggests the toner is not fully depleted. Inspect the drum and fuser path first.",
    recommended_action: "Print a test page, then inspect the drum surface and fuser assembly for uneven marks.",
    documentation_references: [
      {
        source: "fallback",
        type: "manual",
        title: "Service Manual",
        snippet: "pp. 47-49 · Drum Unit",
      },
      {
        source: "fallback",
        type: "manual",
        title: "User Guide",
        snippet: "p. 112 · Fuser Assembly",
      },
    ],
  };
}
