import { AppShell } from "@/components/AppShell";
import { MarketplaceView } from "@/components/MarketplaceView";
import { getProducts } from "@/lib/server-api";

export default async function MarketplacePage({
  searchParams,
}: {
  searchParams?: Promise<{ q?: string; category?: string }>;
}) {
  const params = await searchParams;
  const products = await getProducts({
    query: params?.q,
    category: params?.category,
  });

  return (
    <AppShell>
      <MarketplaceView products={products} query={params?.q} category={params?.category} />
    </AppShell>
  );
}
