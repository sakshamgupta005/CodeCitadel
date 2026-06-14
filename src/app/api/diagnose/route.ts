import { NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";
import type { DiagnosticResponse } from "@/lib/types";
import { readStoredProduct } from "@/lib/server-product-store";

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
  } catch (error) {
    const product = await readStoredProduct(productId);
    const symptom = body.answer || body.issue || "the reported symptom";
    const sessionId = body.sessionId || `local-${Date.now().toString(36)}`;
    const payload: DiagnosticResponse = {
      session_id: sessionId,
      probable_causes: [
        `Configuration or setup issue affecting ${product?.name ?? "this product"}`,
        "Loose connection, blocked component, or worn consumable",
        "Recent usage pattern or environment change",
      ],
      follow_up_question: "When did this start, and did anything change right before it happened?",
      next_step: `Check the visible status indicators and reproduce this symptom once: ${symptom}.`,
      recommended_action: "Record any error light, code, noise, or timing pattern, then inspect the product documentation added for this item.",
      documentation_references: [
        {
          source: "local",
          type: "fallback",
          title: product ? `${product.name} uploaded knowledge` : "Uploaded product knowledge",
          snippet: "Local fallback response while the diagnostic backend is unavailable.",
          score: 1,
        },
      ],
    };

    return NextResponse.json(payload);
  }
}
