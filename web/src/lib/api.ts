const mutationMethods = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

export class APIError extends Error {
  status: number;
  code: string;
  details: unknown;
  constructor(status: number, code: string, message: string, details: unknown) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method || 'GET').toUpperCase();
  const headers = new Headers(init.headers);
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (mutationMethods.has(method) && !headers.has('Idempotency-Key')) headers.set('Idempotency-Key', crypto.randomUUID());
  const response = await fetch(`/v1${path}`, { ...init, headers });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ error: { code: 'http_error', message: response.statusText } }));
    throw new APIError(response.status, payload.error?.code ?? 'http_error', payload.error?.message ?? response.statusText, payload.error?.details);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function json(method: string, value: unknown): RequestInit {
  return { method, body: JSON.stringify(value) };
}
