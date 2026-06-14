import { AppShell } from "@/components/AppShell";
import { DashboardView } from "@/components/DashboardView";
import { getImportStatus, getProducts } from "@/lib/server-api";

export default async function DashboardPage() {
  const [products, importStatus] = await Promise.all([getProducts(), getImportStatus()]);

  return (
    <AppShell>
      <DashboardView products={products} importStatus={importStatus} />
    </AppShell>
  );
}
