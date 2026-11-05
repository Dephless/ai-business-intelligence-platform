
const CSV_TEMPLATE = [
  "order_id,date,region,product,category,units_sold,unit_price,revenue,marketing_cost,customers",
  "1001,2026-01-01,North,Product A,Electronics,12,49.99,599.88,120.00,10",
  "1002,2026-01-02,South,Product B,Home,8,79.50,636.00,95.00,7",
  "1003,2026-01-03,West,Product C,Electronics,15,29.99,449.85,80.00,13",
  "1004,2026-01-04,East,Product A,Electronics,10,49.99,499.90,110.00,9",
].join("\r\n");

export function downloadCsvTemplate(): void {
  const blob = new Blob(
    ["\uFEFF", CSV_TEMPLATE],
    { type: "text/csv;charset=utf-8" },
  );

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  try {
    link.href = url;
    link.download = "business-intelligence-template.csv";
    link.style.display = "none";

    document.body.appendChild(link);
    link.click();
  } finally {
    link.remove();
    URL.revokeObjectURL(url);
  }
}
