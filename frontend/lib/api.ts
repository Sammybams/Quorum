const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(await readError(res));
  }
  return res.json() as Promise<T>;
}

export async function apiPost<TResponse, TPayload>(path: string, payload: TPayload): Promise<TResponse> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(await readError(res));
  }

  return res.json() as Promise<TResponse>;
}

async function readError(res: Response) {
  const fallback = `Request failed: ${res.status} ${res.statusText}`;

  try {
    const data = await res.clone().json();
    if (typeof data?.detail === "string") {
      return data.detail;
    }
    if (Array.isArray(data?.detail)) {
      return data.detail.map((item: { msg?: string }) => item.msg || "Invalid field").join(", ");
    }
  } catch {
    const text = await res.text();
    return text || fallback;
  }

  return fallback;
}

export { API_BASE_URL };
