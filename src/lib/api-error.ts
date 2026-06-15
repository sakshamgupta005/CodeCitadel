export async function backendErrorDetail(response: Response, fallback: string): Promise<string> {
  const text = await response.text();
  if (!text) return fallback;

  try {
    const parsed = JSON.parse(text) as { detail?: unknown; error_type?: unknown };
    if (typeof parsed.detail === "string" && parsed.detail.trim()) {
      return parsed.detail;
    }
  } catch {
    // Plain-text backend responses are still useful to show.
  }

  return text;
}
