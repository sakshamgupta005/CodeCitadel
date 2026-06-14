import Link from "next/link";
import type { ProductView } from "@/lib/types";

export function ProductCard({ product }: { product: ProductView }) {
  return (
    <Link
      className={`mock-product-card ${product.featured ? "selected" : ""}`}
      href={`/products/${product.id}`}
    >
      <div className="mock-product-img">{product.emoji}</div>
      <div className="mock-product-body">
        <div className="mock-product-cat">{product.category}</div>
        <div className="mock-product-name">{product.name}</div>
        <div className="mock-product-company">
          {product.company}
          {product.model ? ` · ${product.model}` : ""}
        </div>
      </div>
      <div className="mock-product-footer">
        <div className="mock-product-docs">📄 {product.docs} docs</div>
        <div className="mock-fix-btn">Diagnose →</div>
      </div>
    </Link>
  );
}
