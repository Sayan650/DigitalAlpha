export type Transaction = {
  id: string; source_transaction_id: string; occurred_at: string; merchant: string; category: string;
  amount: string; currency: string; status: string; payment_method: string; raw_timestamp: string;
};
export type TransactionPage = { items: Transaction[]; total: number; page: number; page_size: number; total_pages: number };
export type Analytics = { by_category: { category: string; amount: string }[]; by_month: { month: string; amount: string }[] };
export type Reward = { id: string; title: string; description: string; coin_cost: number; accent: string };

