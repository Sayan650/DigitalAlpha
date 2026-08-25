import type { Analytics, Reward, TransactionPage } from "./types";

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(init?.headers || {}) } });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Something went wrong. Please try again.");
  }
  return response.json();
}

export const api = {
  transactions: (query: URLSearchParams) => request<TransactionPage>(`/transactions?${query}`),
  analytics: (query: URLSearchParams) => request<Analytics>(`/analytics?${query}`),
  balance: () => request<{ balance: number }>("/balance"),
  rewards: () => request<Reward[]>("/rewards"),
  redeem: (reward_id: string, idempotency_key: string) => request<{ balance: number; reward_id: string }>("/redeem", { method: "POST", body: JSON.stringify({ reward_id, idempotency_key }) }),
};

