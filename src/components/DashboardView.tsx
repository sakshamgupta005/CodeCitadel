import { formatNumber } from "@/lib/design-data";
import type { ImportStatusResponse, ProductView } from "@/lib/types";

export function DashboardView({
  products,
  importStatus,
}: {
  products: ProductView[];
  importStatus: ImportStatusResponse | null;
}) {
  const docsIndexed = products.reduce((total, product) => total + product.docs, 0);
  const sessions = products.reduce((total, product) => total + product.sessions, 0);
  const rows = products.slice(0, 3);

  return (
    <>
      <div className="page-kicker">Company Dashboard</div>
      <div className="mock-dashboard">
        <aside className="mock-dash-sidebar">
          <div className="mock-dash-brand">
            <div className="mock-logo-mark" style={{ fontSize: 10, height: 20, width: 20 }}>
              ⚡
            </div>
            FixPilot
          </div>
          {["📊 Overview", "📦 Products", "📄 Documents", "📈 Analytics", "⚙️ Settings"].map(
            (item, index) => (
              <div className={`mock-dash-nav-item ${index === 0 ? "active" : ""}`} key={item}>
                <span className="mock-dash-icon">{item.slice(0, 2)}</span>
                {item.slice(3)}
              </div>
            ),
          )}
          <div className="dashboard-account">
            <div className="mock-dash-nav-item">
              <span className="mock-dash-icon">🆘</span>
              Support
            </div>
            <div className="account-card">
              <div>Bosch Home</div>
              <div>Pro Plan</div>
            </div>
          </div>
        </aside>

        <section className="mock-dash-main">
          <div className="mock-dash-topbar">
            <div>
              <div className="mock-dash-heading">Overview</div>
              <div style={{ color: "var(--text-muted)", fontSize: 12 }}>
                Bosch Home Appliances · bosch-home
              </div>
            </div>
            <button className="mock-dash-add-btn">+ Add Product</button>
          </div>

          <div className="mock-stat-row">
            <Stat label="Products Listed" value={products.length.toString()} tone="indigo" />
            <Stat label="Docs Indexed" value={formatNumber(docsIndexed)} tone="teal" />
            <Stat label="Diagnostic Sessions" value={formatNumber(sessions)} tone="amber" />
            <Stat label="Resolution Rate" value="91%" tone="green" />
          </div>

          <div style={{ alignItems: "center", display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
            <div style={{ color: "var(--text-primary)", fontSize: 13, fontWeight: 600 }}>Your Products</div>
            <div style={{ color: "var(--text-muted)", fontSize: 12 }}>
              Showing {rows.length} of {products.length}
            </div>
          </div>

          <div className="mock-product-table">
            <div className="mock-table-header">
              <div>Product</div>
              <div>Docs</div>
              <div>Sessions</div>
              <div>Status</div>
              <div />
            </div>
            {rows.map((product, index) => (
              <div className="mock-table-row" key={product.id}>
                <div className="mock-table-name">
                  <span style={{ fontSize: 16 }}>{product.emoji}</span>
                  {product.name}
                </div>
                <div className="mock-table-cell">{product.docs}</div>
                <div className="mock-table-cell">{formatNumber(product.sessions)}</div>
                <div className="mock-table-cell">
                  <span className={`mock-status-badge ${index === rows.length - 1 ? "indexing" : "live"}`}>
                    {index === rows.length - 1 ? "Indexing" : "Live"}
                  </span>
                </div>
                <div className="mock-table-actions">
                  <button className="mock-action-btn">Edit</button>
                  <button className="mock-action-btn">+Doc</button>
                </div>
              </div>
            ))}
          </div>

          {importStatus?.last_import && (
            <div className="empty-state" style={{ marginTop: 16 }}>
              Last import: {importStatus.last_import.message}
            </div>
          )}
        </section>
      </div>
    </>
  );
}

function Stat({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "indigo" | "teal" | "amber" | "green";
}) {
  const className = tone === "green" ? "mock-stat-value" : `mock-stat-value ${tone}`;
  return (
    <div className="mock-stat">
      <div className={className} style={tone === "green" ? { color: "var(--green)" } : undefined}>
        {value}
      </div>
      <div className="mock-stat-label">{label}</div>
    </div>
  );
}
