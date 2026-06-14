import { API_BASE_URL } from "@/lib/api";
import { fallbackProducts, toProductView } from "@/lib/design-data";
import { readStoredProduct, readStoredProducts } from "@/lib/server-product-store";
import type { ImportStatusResponse, Product, ProductView } from "@/lib/types";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export async function getProducts(options?: {
  query?: string;
  category?: string;
}): Promise<ProductView[]> {
  const params = new URLSearchParams();
  if (options?.query) params.set("query", options.query);
  if (options?.category && options.category !== "All") params.set("category", options.category);
  const suffix = params.size ? `?${params.toString()}` : "";

  try {
    const products = await fetchJson<Product[]>(`/products${suffix}`);
    return products.length ? products.map(toProductView) : fallbackProducts.map(toProductView);
  } catch {
    const products = await readStoredProducts({
      query: options?.query,
      category: options?.category === "All" ? undefined : options?.category,
    });
    return products.map(toProductView);
  }
}

export async function getProduct(productId: string): Promise<ProductView | null> {
  try {
    return toProductView(await fetchJson<Product>(`/products/${productId}`));
  } catch {
    const storedProduct = await readStoredProduct(productId);
    return storedProduct ? toProductView(storedProduct) : null;
  }
}

export async function getImportStatus(): Promise<ImportStatusResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/import/status`, { cache: "no-store" });
    if (!response.ok) return null;
    return await response.json() as Promise<ImportStatusResponse>;
  } catch {
    return null;
  }
}
