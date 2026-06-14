import { NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";
import { deleteStoredProduct, readStoredProduct, updateStoredProduct } from "@/lib/server-product-store";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ productId: string }> }
) {
  const { productId } = await params;

  try {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`Backend failed: ${response.status}`);
    return NextResponse.json(await response.json());
  } catch {
    const product = await readStoredProduct(productId);
    if (!product) return NextResponse.json({ detail: "Product not found" }, { status: 404 });
    return NextResponse.json(product);
  }
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ productId: string }> }
) {
  const { productId } = await params;
  const body = await request.json();

  try {
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
    try {
      return NextResponse.json(await updateStoredProduct(productId, body));
    } catch (fallbackError) {
      const message = fallbackError instanceof Error ? fallbackError.message : error instanceof Error ? error.message : "Internal Server Error";
      return NextResponse.json({ detail: message }, { status: 500 });
    }
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ productId: string }> }
) {
  const { productId } = await params;

  try {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      const errorMsg = await response.text();
      return NextResponse.json({ detail: errorMsg || "Failed to delete product" }, { status: response.status });
    }

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    try {
      await deleteStoredProduct(productId);
      return new NextResponse(null, { status: 204 });
    } catch (fallbackError) {
      const message = fallbackError instanceof Error ? fallbackError.message : error instanceof Error ? error.message : "Internal Server Error";
      return NextResponse.json({ detail: message }, { status: 500 });
    }
  }
}
