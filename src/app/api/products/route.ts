import { NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";
import { createStoredProduct, readStoredProducts } from "@/lib/server-product-store";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const suffix = searchParams.size ? `?${searchParams.toString()}` : "";

  try {
    const response = await fetch(`${API_BASE_URL}/products${suffix}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Backend failed: ${response.status}`);
    return NextResponse.json(await response.json());
  } catch {
    const products = await readStoredProducts({
      query: searchParams.get("query") ?? undefined,
      category: searchParams.get("category") ?? undefined,
    });
    return NextResponse.json(products);
  }
}

export async function POST(request: Request) {
  const body = await request.json();

  try {
    const response = await fetch(`${API_BASE_URL}/products`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorMsg = await response.text();
      return NextResponse.json({ detail: errorMsg || "Failed to create product" }, { status: response.status });
    }

    const payload = await response.json();
    return NextResponse.json(payload);
  } catch (error) {
    try {
      const product = await createStoredProduct(body);
      return NextResponse.json(product, { status: 201 });
    } catch (fallbackError) {
      const message = fallbackError instanceof Error ? fallbackError.message : error instanceof Error ? error.message : "Internal Server Error";
      return NextResponse.json({ detail: message }, { status: 500 });
    }
  }
}
