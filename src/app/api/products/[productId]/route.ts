import { NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";

export async function PUT(
  request: Request,
  { params }: { params: { productId: string } }
) {
  try {
    const { productId } = params;
    const body = await request.json();
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorMsg = await response.text();
      return NextResponse.json({ detail: errorMsg || "Failed to update product" }, { status: response.status });
    }

    const payload = await response.json();
    return NextResponse.json(payload);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Internal Server Error";
    return NextResponse.json({ detail: message }, { status: 500 });
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { productId: string } }
) {
  try {
    const { productId } = params;
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      const errorMsg = await response.text();
      return NextResponse.json({ detail: errorMsg || "Failed to delete product" }, { status: response.status });
    }

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Internal Server Error";
    return NextResponse.json({ detail: message }, { status: 500 });
  }
}
