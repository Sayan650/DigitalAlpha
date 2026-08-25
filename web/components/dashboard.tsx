"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "../lib/api";
import { defaults, Filters, fromQuery, monthDates, toQuery } from "../lib/filters";
import type { Reward, Transaction } from "../lib/types";
import { Badge, Button, Card, Modal } from "./ui";

const categories = ["Travel", "Shopping", "Utilities", "Food & Dining", "Health", "Education", "Entertainment", "Groceries", "Fuel", "Insurance", "Uncategorized"];
const palette = ["#24BF64", "#099774", "#137637", "#275462", "#82C357", "#178c66", "#448174", "#99CC74", "#0E5D44", "#306775", "#6B8E7D"];
const inr = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric", timeZone: "Asia/Kolkata" }).format(new Date(value));
}

function FilterControls({ filters, setFilters }: { filters: Filters; setFilters: React.Dispatch<React.SetStateAction<Filters>> }) {
  const [search, setSearch] = useState(filters.search);
  useEffect(() => {
    const timer = window.setTimeout(() => setFilters((current) => current.search === search ? current : { ...current, search, page: 1 }), 250);
    return () => window.clearTimeout(timer);
  }, [search, setFilters]);
  const update = (key: keyof Filters, value: string) => setFilters((current) => ({ ...current, [key]: value, page: 1 }));
  return <div className="filters" aria-label="Transaction filters">
    <label className="search"><span className="sr-only">Search merchant</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search merchants" /></label>
    <select aria-label="Category" value={filters.category} onChange={(event) => update("category", event.target.value)}><option value="">All categories</option>{categories.map((category) => <option key={category}>{category}</option>)}</select>
    <select aria-label="Payment status" value={filters.status} onChange={(event) => update("status", event.target.value)}><option value="">All statuses</option><option>SUCCESS</option><option>PENDING</option><option>FAILED</option></select>
    <label>Date from<input aria-label="Date from" type="date" value={filters.date_from} onChange={(event) => update("date_from", event.target.value)} /></label>
    <label>Date to<input aria-label="Date to" type="date" value={filters.date_to} onChange={(event) => update("date_to", event.target.value)} /></label>
    <label>Min ₹<input aria-label="Minimum amount" inputMode="decimal" value={filters.min_amount} onChange={(event) => update("min_amount", event.target.value)} /></label>
    <label>Max ₹<input aria-label="Maximum amount" inputMode="decimal" value={filters.max_amount} onChange={(event) => update("max_amount", event.target.value)} /></label>
    <Button className="quiet" onClick={() => { setSearch(""); setFilters(defaults); }}>Reset</Button>
  </div>;
}

function TransactionsTable({ data, filters, setFilters, onDetail, loading }: { data?: { items: Transaction[]; total: number; total_pages: number }; filters: Filters; setFilters: React.Dispatch<React.SetStateAction<Filters>>; onDetail: (transaction: Transaction) => void; loading: boolean }) {
  const toggleSort = (sortBy: "date" | "amount") => setFilters((current) => ({ ...current, page: 1, sort_by: sortBy, sort_order: current.sort_by === sortBy && current.sort_order === "desc" ? "asc" : "desc" }));
  const sortIcon = (field: "date" | "amount") => filters.sort_by === field ? filters.sort_order === "desc" ? " ↓" : " ↑" : "";
  return <Card className="table-card"><div className="table-heading"><div><p className="eyebrow">Transactions</p><h2>Every payment, in context</h2></div><span>{data?.total.toLocaleString() ?? "—"} records</span></div>
    <div className="table-scroll"><table><thead><tr><th>Merchant</th><th>Category</th><th><button onClick={() => toggleSort("date")}>Date{sortIcon("date")}</button></th><th>Method</th><th>Status</th><th className="amount"><button onClick={() => toggleSort("amount")}>Amount{sortIcon("amount")}</button></th></tr></thead>
      <tbody>{loading ? <tr><td colSpan={6} className="state">Loading transactions…</td></tr> : !data?.items.length ? <tr><td colSpan={6} className="state">No transactions match these filters.</td></tr> : data.items.map((transaction) => <tr key={transaction.id} tabIndex={0} onClick={() => onDetail(transaction)} onKeyDown={(event) => event.key === "Enter" && onDetail(transaction)}><td><strong>{transaction.merchant}</strong><small>{transaction.source_transaction_id}</small></td><td>{transaction.category}</td><td>{formatDate(transaction.occurred_at)}</td><td>{transaction.payment_method}</td><td><Badge tone={transaction.status}>{transaction.status}</Badge></td><td className={`amount ${Number(transaction.amount) < 0 ? "refund" : ""}`}>{inr.format(Number(transaction.amount))}</td></tr>)}</tbody>
    </table></div>
    <div className="pagination"><span>Page {filters.page} of {data?.total_pages || 1}</span><div><Button className="quiet" disabled={filters.page <= 1} onClick={() => setFilters((current) => ({ ...current, page: current.page - 1 }))}>Previous</Button><Button className="quiet" disabled={!data || filters.page >= data.total_pages} onClick={() => setFilters((current) => ({ ...current, page: current.page + 1 }))}>Next</Button></div></div>
  </Card>;
}

function AnalyticsCards({ analytics, onCategory, onMonth }: { analytics?: Awaited<ReturnType<typeof api.analytics>>; onCategory: (category: string) => void; onMonth: (month: string) => void }) {
  const categoryData = analytics?.by_category.map((item) => ({ ...item, amount: Number(item.amount) })) || [];
  const monthlyData = analytics?.by_month.map((item) => ({ ...item, amount: Number(item.amount), label: item.month.slice(5) })) || [];
  return <div className="analytics-grid"><Card className="chart-card"><div><p className="eyebrow">Spend by category</p><h2>Where your money went</h2></div><div className="chart"><ResponsiveContainer width="100%" height={220}><PieChart><Pie data={categoryData} dataKey="amount" nameKey="category" innerRadius={54} outerRadius={84} paddingAngle={2} onClick={(slice) => onCategory(String((slice as { category?: string }).category || ""))}>{categoryData.map((_, index) => <Cell key={index} fill={palette[index % palette.length]} />)}</Pie><Tooltip formatter={(value) => inr.format(Number(value))} /></PieChart></ResponsiveContainer></div><div className="legend">{categoryData.slice(0, 6).map((item, index) => <button key={item.category} onClick={() => onCategory(item.category)}><i style={{ background: palette[index] }} />{item.category}<span>{inr.format(item.amount)}</span></button>)}</div></Card>
    <Card className="chart-card"><div><p className="eyebrow">Monthly trend</p><h2>Net settled spend</h2></div><div className="chart"><ResponsiveContainer width="100%" height={220}><LineChart data={monthlyData} margin={{ left: 4, right: 4 }}><XAxis dataKey="label" tickLine={false} axisLine={false} /><YAxis hide /><Tooltip formatter={(value) => inr.format(Number(value))} labelFormatter={(_, data) => data[0]?.payload.month || ""} /><Line type="monotone" dataKey="amount" stroke="#24BF64" strokeWidth={3} dot={{ r: 3, strokeWidth: 0 }} activeDot={{ r: 6 }} /></LineChart></ResponsiveContainer></div><div className="month-buttons">{monthlyData.map((item) => <button key={item.month} onClick={() => onMonth(item.month)} aria-label={`Filter table to ${item.month}`}>{item.month}</button>)}</div></Card></div>;
}

function Rewards({ rewards, balance }: { rewards?: Reward[]; balance?: number }) {
  const client = useQueryClient();
  const [selected, setSelected] = useState<Reward | null>(null);
  const [notice, setNotice] = useState("");
  const mutation = useMutation({
    mutationFn: (reward: Reward) => api.redeem(reward.id, crypto.randomUUID()),
    onMutate: async (reward) => { setNotice(""); await client.cancelQueries({ queryKey: ["balance"] }); const previous = client.getQueryData<{ balance: number }>(["balance"]); if (previous) client.setQueryData(["balance"], { balance: previous.balance - reward.coin_cost }); return { previous }; },
    onError: (error: Error, _reward, context) => { if (context?.previous) client.setQueryData(["balance"], context.previous); setNotice(error.message); },
    onSuccess: (result) => { client.setQueryData(["balance"], { balance: result.balance }); setNotice("Reward redeemed - it is now in your rewards history."); },
    onSettled: () => { client.invalidateQueries({ queryKey: ["balance"] }); setSelected(null); },
  });
  return <Card className="rewards-card"><div className="section-head"><div><p className="eyebrow">Coin rewards</p><h2>Make your spend go further</h2></div><span className="coin-inline">✦ {balance?.toLocaleString() ?? "—"} coins</span></div>{notice && <p className="notice" role="status">{notice}</p>}<div className="rewards-grid">{rewards?.map((reward) => <article key={reward.id} className={`reward ${reward.accent}`}><span className="reward-mark">✦</span><h3>{reward.title}</h3><p>{reward.description}</p><div><strong>{reward.coin_cost.toLocaleString()} coins</strong><Button disabled={(balance ?? 0) < reward.coin_cost} onClick={() => setSelected(reward)}>Redeem</Button></div></article>)}</div>{selected && <Modal title={`Redeem ${selected.title}`} onClose={() => setSelected(null)}><p>This will use <strong>{selected.coin_cost.toLocaleString()} coins</strong> from your balance. This reward is an in-app claim.</p><div className="modal-actions"><Button className="quiet" onClick={() => setSelected(null)}>Cancel</Button><Button disabled={mutation.isPending} onClick={() => mutation.mutate(selected)}>{mutation.isPending ? "Redeeming…" : "Confirm redemption"}</Button></div></Modal>}</Card>;
}

export function Dashboard() {
  const params = useSearchParams();
  const [filters, setFilters] = useState<Filters>(() => fromQuery(new URLSearchParams(params.toString())));
  const [detail, setDetail] = useState<Transaction | null>(null);
  const tableQuery = useMemo(() => toQuery(filters), [filters]);
  const analyticsQuery = useMemo(() => toQuery(filters, false), [filters]);
  const transactions = useQuery({ queryKey: ["transactions", tableQuery.toString()], queryFn: () => api.transactions(tableQuery), placeholderData: keepPreviousData });
  const analytics = useQuery({ queryKey: ["analytics", analyticsQuery.toString()], queryFn: () => api.analytics(analyticsQuery) });
  const balance = useQuery({ queryKey: ["balance"], queryFn: api.balance });
  const rewards = useQuery({ queryKey: ["rewards"], queryFn: api.rewards });
  useEffect(() => { const query = toQuery(filters, false).toString(); window.history.replaceState(null, "", query ? `/?${query}` : "/"); }, [filters]);
  const setCategory = (category: string) => category && setFilters((current) => ({ ...current, category, page: 1 }));
  const setMonth = (month: string) => setFilters((current) => ({ ...current, ...monthDates(month), page: 1 }));

  return <main className="shell"><header className="topbar"><a className="brand" href="#top" aria-label="Coinwise dashboard"><span>✦</span>Coinwise</a><div className="balance"><small>Available balance</small><strong>✦ {balance.data?.balance.toLocaleString() ?? "—"}</strong><span>coins</span></div></header>
    <section className="hero" id="top"><p className="eyebrow">FINANCIAL WELLNESS, SIMPLIFIED</p><h1>Every transaction tells<br /><em>a smarter story.</em></h1><p>See your spending clearly, spot the patterns, and turn every settled payment into something rewarding.</p></section>
    <AnalyticsCards analytics={analytics.data} onCategory={setCategory} onMonth={setMonth} />
    <section className="transactions-section"><FilterControls filters={filters} setFilters={setFilters} />{transactions.isError ? <Card><p className="state">{(transactions.error as Error).message}</p></Card> : <TransactionsTable data={transactions.data} filters={filters} setFilters={setFilters} onDetail={setDetail} loading={transactions.isLoading} />}</section>
    <Rewards rewards={rewards.data} balance={balance.data?.balance} />
    {detail && <Modal title="Transaction details" onClose={() => setDetail(null)}><dl className="details"><div><dt>Merchant</dt><dd>{detail.merchant}</dd></div><div><dt>Amount</dt><dd>{inr.format(Number(detail.amount))}</dd></div><div><dt>Status</dt><dd><Badge tone={detail.status}>{detail.status}</Badge></dd></div><div><dt>Category</dt><dd>{detail.category}</dd></div><div><dt>Payment method</dt><dd>{detail.payment_method}</dd></div><div><dt>Source ID</dt><dd>{detail.source_transaction_id}</dd></div><div><dt>Original timestamp</dt><dd>{detail.raw_timestamp}</dd></div></dl></Modal>}
  </main>;
}

