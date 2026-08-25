export type Filters = {
  page: number; search: string; category: string; status: string; date_from: string; date_to: string;
  min_amount: string; max_amount: string; sort_by: "date" | "amount"; sort_order: "asc" | "desc";
};

export const defaults: Filters = { page: 1, search: "", category: "", status: "", date_from: "", date_to: "", min_amount: "", max_amount: "", sort_by: "date", sort_order: "desc" };

export function toQuery(filters: Filters, includePagination = true) {
  const params = new URLSearchParams();
  (Object.entries(filters) as [keyof Filters, string | number][]).forEach(([key, value]) => {
    if (value !== "" && !(key === "page" && value === 1)) params.set(key, String(value));
  });
  if (includePagination) params.set("page_size", "50"); else params.delete("page");
  return params;
}

export function fromQuery(params: URLSearchParams): Filters {
  return {
    ...defaults,
    ...Object.fromEntries([...params.entries()].filter(([key]) => key in defaults)),
    page: Math.max(1, Number(params.get("page") || 1)),
    sort_by: params.get("sort_by") === "amount" ? "amount" : "date",
    sort_order: params.get("sort_order") === "asc" ? "asc" : "desc",
  };
}

export function monthDates(month: string) {
  const start = `${month}-01`;
  const end = new Date(`${start}T00:00:00Z`);
  end.setUTCMonth(end.getUTCMonth() + 1, 0);
  return { date_from: start, date_to: end.toISOString().slice(0, 10) };
}

