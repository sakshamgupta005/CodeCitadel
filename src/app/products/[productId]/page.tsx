import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { ProductDetailView } from "@/components/ProductDetailView";
import { getProduct } from "@/lib/api";

export default async function ProductDetailsPage({
  params,
}: {
  params: Promise<{ productId: string }>;
}) {
  const { productId } = await params;
  const product = await getProduct(productId);

  if (!product) {
    notFound();
  }

  return (
    <AppShell>
      <ProductDetailView product={product} />
    </AppShell>
  );
}
