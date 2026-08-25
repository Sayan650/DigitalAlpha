import { describe, expect, it } from "vitest";
import { defaults, fromQuery, monthDates, toQuery } from "./filters";

describe("dashboard URL filter state", () => {
  it("serializes active filters and a server page size", () => {
    const query = toQuery({ ...defaults, page: 3, category: "Travel", min_amount: "1000" });
    expect(query.toString()).toContain("page=3");
    expect(query.get("category")).toBe("Travel");
    expect(query.get("page_size")).toBe("50");
  });

  it("restores a safe filter state from a URL", () => {
    const filters = fromQuery(new URLSearchParams("page=2&status=SUCCESS&sort_by=amount&sort_order=asc"));
    expect(filters).toMatchObject({ page: 2, status: "SUCCESS", sort_by: "amount", sort_order: "asc" });
  });

  it("turns a chart month into an inclusive date range", () => {
    expect(monthDates("2026-02")).toEqual({ date_from: "2026-02-01", date_to: "2026-02-28" });
  });
});

