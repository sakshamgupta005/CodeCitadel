"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createProduct } from "@/lib/api";

type UploadType = "pdf" | "text" | "url";

export function ProductUploader() {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [name, setName] = useState("");
  const [category, setCategory] = useState("Electronics");
  const [description, setDescription] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [uploadType, setUploadType] = useState<UploadType>("pdf");
  const [docFile, setDocFile] = useState<File | null>(null);
  const [docTitle, setDocTitle] = useState("");
  const [docText, setDocText] = useState("");
  const [docUrl, setDocUrl] = useState("");

  function reset() {
    setName("");
    setCategory("Electronics");
    setDescription("");
    setImageUrl("");
    setUploadType("pdf");
    setDocFile(null);
    setDocTitle("");
    setDocText("");
    setDocUrl("");
    setError("");
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    if (!name.trim() || !description.trim()) {
      setError("Product name and description are required.");
      return;
    }

    if (uploadType === "pdf" && !docFile) {
      setError("Choose a PDF or switch the document type.");
      return;
    }
    if (uploadType === "text" && !docText.trim()) {
      setError("Paste document text or switch the document type.");
      return;
    }
    if (uploadType === "url" && !docUrl.trim()) {
      setError("Enter a document URL or switch the document type.");
      return;
    }

    setIsSubmitting(true);
    try {
      const product = await createProduct({
        name: name.trim(),
        category,
        description: description.trim(),
        image_url: imageUrl.trim() || "https://images.unsplash.com/photo-1558618666-fcd25c85cd64",
      });

      await uploadKnowledge(product.id);
      reset();
      setIsOpen(false);
      router.refresh();
      router.push(`/products/${product.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add product.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function uploadKnowledge(productId: string) {
    let response: Response;

    if (uploadType === "pdf" && docFile) {
      const formData = new FormData();
      formData.append("file", docFile);
      response = await fetch(`/api/products/${productId}/knowledge/pdf`, {
        method: "POST",
        body: formData,
      });
    } else if (uploadType === "text") {
      const formData = new FormData();
      formData.append("text", docText);
      formData.append("title", docTitle.trim() || "Uploaded document");
      response = await fetch(`/api/products/${productId}/knowledge/text`, {
        method: "POST",
        body: formData,
      });
    } else {
      response = await fetch(`/api/products/${productId}/knowledge/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: docUrl.trim(), title: docTitle.trim() || docUrl.trim() }),
      });
    }

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data?.detail || "Product was created, but document upload failed.");
    }
  }

  return (
    <>
      <button className="mock-dash-add-btn" onClick={() => setIsOpen(true)} type="button">
        + Add product
      </button>

      {isOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">Add product and document</h2>
              <button
                className="modal-close"
                onClick={() => {
                  reset();
                  setIsOpen(false);
                }}
                type="button"
              >
                x
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              {error && <div className="form-error">{error}</div>}

              <div className="form-group">
                <label className="form-label">Product name</label>
                <input className="form-input" onChange={(event) => setName(event.target.value)} value={name} />
              </div>

              <div className="form-group">
                <label className="form-label">Category</label>
                <select className="form-select" onChange={(event) => setCategory(event.target.value)} value={category}>
                  <option value="Appliances">Appliances</option>
                  <option value="Electronics">Electronics</option>
                  <option value="HVAC">HVAC</option>
                  <option value="Networking">Networking</option>
                  <option value="Industrial">Industrial</option>
                  <option value="Automotive">Automotive</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-textarea" onChange={(event) => setDescription(event.target.value)} value={description} />
              </div>

              <div className="form-group">
                <label className="form-label">Image URL optional</label>
                <input className="form-input" onChange={(event) => setImageUrl(event.target.value)} value={imageUrl} />
              </div>

              <div className="form-group">
                <label className="form-label">Document type</label>
                <select
                  className="form-select"
                  onChange={(event) => setUploadType(event.target.value as UploadType)}
                  value={uploadType}
                >
                  <option value="pdf">PDF file</option>
                  <option value="text">Text document</option>
                  <option value="url">Document URL</option>
                </select>
              </div>

              {uploadType === "pdf" && (
                <div className="form-group">
                  <label className="form-label">PDF or document</label>
                  <input
                    accept=".pdf,.txt,.md,.doc,.docx"
                    className="form-input"
                    onChange={(event) => setDocFile(event.target.files?.[0] ?? null)}
                    type="file"
                  />
                </div>
              )}

              {uploadType !== "pdf" && (
                <div className="form-group">
                  <label className="form-label">Document title</label>
                  <input className="form-input" onChange={(event) => setDocTitle(event.target.value)} value={docTitle} />
                </div>
              )}

              {uploadType === "text" && (
                <div className="form-group">
                  <label className="form-label">Document text</label>
                  <textarea className="form-textarea" onChange={(event) => setDocText(event.target.value)} value={docText} />
                </div>
              )}

              {uploadType === "url" && (
                <div className="form-group">
                  <label className="form-label">Document URL</label>
                  <input className="form-input" onChange={(event) => setDocUrl(event.target.value)} type="url" value={docUrl} />
                </div>
              )}

              <div className="modal-actions">
                <button className="btn-secondary" onClick={() => setIsOpen(false)} type="button">
                  Cancel
                </button>
                <button className="btn-primary" disabled={isSubmitting} type="submit">
                  {isSubmitting ? "Adding..." : "Add product"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
