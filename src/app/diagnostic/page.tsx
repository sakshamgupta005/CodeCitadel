import { AppShell } from "@/components/AppShell";
import { DiagnosticAssistant } from "@/components/DiagnosticAssistant";
import { getProduct, getProducts } from "@/lib/server-api";

export default async function DiagnosticPage({
  searchParams,
}: {
  searchParams?: Promise<{ productId?: string; issue?: string }>;
}) {
  const params = await searchParams;
  const productId = params?.productId;
  const product = productId ? await getProduct(productId) : null;
  const products = await getProducts();

  return (
    <AppShell>
      <DiagnosticAssistant product={product} initialIssue={params?.issue} allProducts={products} />
    </AppShell>
  );
}
