import { AppShell } from "@/components/AppShell";
import { DiagnosticAssistant } from "@/components/DiagnosticAssistant";
import { getProduct } from "@/lib/api";

export default async function DiagnosticPage({
  searchParams,
}: {
  searchParams?: Promise<{ productId?: string; issue?: string }>;
}) {
  const params = await searchParams;
  const product = await getProduct(params?.productId ?? "hp-laserjet-pro-m404n");

  return (
    <AppShell>
      <DiagnosticAssistant product={product!} initialIssue={params?.issue} />
    </AppShell>
  );
}
