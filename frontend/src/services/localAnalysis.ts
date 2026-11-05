import type {
  Analysis,
  Metric,
  Recommendation,
  TimeSeriesPoint,
} from "../types/analysis";

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;
const MAX_RECORDS = 5_000;
const MAX_COLUMNS = 50;

type CellValue = string | number | null;
type RecordRow = Record<string, CellValue>;

function parseCsvText(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];

    if (inQuotes) {
      if (char === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"' && field.length === 0) {
      inQuotes = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n" || char === "\r") {
      row.push(field);

      if (!(row.length === 1 && row[0] === "")) {
        rows.push(row);
      }

      row = [];
      field = "";

      if (char === "\r" && text[i + 1] === "\n") {
        i++;
      }
    } else if (char === '"') {
      throw new Error("The CSV file has an invalid structure.");
    } else {
      field += char;
    }
  }

  if (inQuotes) {
    throw new Error("The CSV file has an invalid structure.");
  }

  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }

  return rows;
}

function convertValue(value: string): CellValue {
  const normalized = value.trim();

  if (!normalized) {
    return null;
  }

  if (/^[+-]?\d+$/.test(normalized)) {
    const digits = normalized.replace(/^[+-]/, "");

    if (digits.length > 1 && digits.startsWith("0")) {
      return normalized;
    }

    const integer = Number(normalized);

    if (!Number.isSafeInteger(integer)) {
      return normalized;
    }

    return integer;
  }

  const isNumeric =
    /^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/.test(normalized);

  if (!isNumeric) {
    if (/^[+-]?(?:Infinity|NaN)$/i.test(normalized)) {
      throw new Error(`Non-finite numeric value found: ${normalized}`);
    }

    return normalized;
  }

  const number = Number(normalized);

  if (!Number.isFinite(number)) {
    throw new Error(`Non-finite numeric value found: ${normalized}`);
  }

  return number;
}


async function parseCsv(file: File): Promise<RecordRow[]> {
  const fileName = file.name.toLowerCase();

  // 1. File extension check
  if (!fileName.endsWith(".csv")) {
    throw new Error("Only CSV files are allowed.");
  }

  // MIME type is not a reliable security check.
  // Browsers and operating systems may report different MIME types.

  // 2. File size validation
  if (file.size === 0) {
    throw new Error("The uploaded CSV file is empty.");
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    throw new Error("The CSV file exceeds the 5 MB size limit.");
  }

  let text: string;

  // 3. Read and decode file safely
  try {
    const buffer = await file.arrayBuffer();

    text = new TextDecoder("utf-8", {
      fatal: true
    }).decode(buffer);

  } catch {
    throw new Error("The CSV file must use valid UTF-8 encoding.");
  }

  // 4. Remove optional UTF-8 BOM
  text = text.replace(/^\uFEFF/, "");

  // 5. Reject binary data and unexpected control characters
  if (/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/.test(text)) {
    throw new Error("The CSV file contains invalid control characters.");
  }

  // 6. Parse CSV
  const rows = parseCsvText(text);

  if (!Array.isArray(rows) || rows.length === 0) {
    throw new Error("The CSV file must contain a header row.");
  }

  // 7. Limit records before further processing
  if (rows.length - 1 > MAX_RECORDS) {
    throw new Error(`The CSV file must not exceed ${MAX_RECORDS} records.`);
  }

  // 8. Validate headers
  const headers = rows[0].map((header) => header.trim());

  if (headers.length === 0 || headers.length > MAX_COLUMNS) {
    throw new Error(`The CSV file must not exceed ${MAX_COLUMNS} columns.`);
  }

  if (headers.some((header) => !header)) {
    throw new Error("CSV column names must not be empty.");
  }

  const normalizedHeaders = headers.map((header) =>
    header.toLowerCase()
  );

  if (new Set(normalizedHeaders).size !== headers.length) {
    throw new Error("Duplicate CSV column names are not allowed.");
  }

  // 9. Reject potentially dangerous object property names
  const forbiddenHeaders = new Set([
    "__proto__",
    "prototype",
    "constructor"
  ]);

  if (normalizedHeaders.some((header) => forbiddenHeaders.has(header))) {
    throw new Error("The CSV contains a reserved column name.");
  }

  // 10. Validate data rows
  const dataRows = rows.slice(1);

  if (dataRows.length === 0) {
    throw new Error("The CSV file must contain at least one data row.");
  }

  const MAX_CELL_LENGTH = 100_000;

  return dataRows.map((values) => {
    if (!Array.isArray(values)) {
      throw new Error("Invalid CSV row.");
    }

    if (values.length > headers.length) {
      throw new Error("A CSV row contains more values than the header.");
    }

    if (values.some((value) => value.length > MAX_CELL_LENGTH)) {
      throw new Error("A CSV cell exceeds the maximum allowed length.");
    }

    // Null prototype prevents special object property behavior
    const record = Object.create(null) as RecordRow;

    headers.forEach((header, index) => {
      record[header] =
        index < values.length
          ? convertValue(values[index])
          : null;
    });

    return record;
  });
}


function calculateMetrics(records: RecordRow[]): Metric[] {
  const fields = [
    ...new Set(
      records.flatMap((row) =>
        Object.entries(row)
          .filter(([, value]) => typeof value === "number")
          .map(([key]) => key),
      ),
    ),
  ].sort();

  return fields.map((field) => {
    const values = records
      .map((row) => row[field])
      .filter((value): value is number => typeof value === "number");

    const total = values.reduce((sum, value) => sum + value, 0);

    return {
      field,
      count: values.length,
      total: round(total),
      average: round(total / values.length),
      minimum: round(Math.min(...values)),
      maximum: round(Math.max(...values)),
    };
  });
}

function round(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

function quantile(sorted: number[], probability: number): number {
  const position = (sorted.length - 1) * probability;
  const lower = Math.floor(position);
  const upper = Math.ceil(position);

  if (lower === upper) {
    return sorted[lower];
  }

  return (
    sorted[lower] +
    (sorted[upper] - sorted[lower]) * (position - lower)
  );
}

function generateRecommendations(
  metrics: Metric[],
  records: RecordRow[],
): Recommendation[] {
  const recommendations: Recommendation[] = [];

  for (const metric of metrics) {
    const values = records
      .map((row) => row[metric.field])
      .filter((value): value is number => typeof value === "number")
      .sort((a, b) => a - b);

    if (values.length >= 4) {
      const q1 = quantile(values, 0.25);
      const q3 = quantile(values, 0.75);
      const iqr = q3 - q1;

      const lowerBound = q1 - 1.5 * iqr;
      const upperBound = q3 + 1.5 * iqr;

      const outliers = values.filter(
        (value) => value < lowerBound || value > upperBound,
      );

      if (outliers.length > 0) {
        recommendations.push({
          title: `Investigate statistical outliers in ${metric.field}`,
          description:
            `Detected ${outliers.length} statistical outlier(s) ` +
            `outside the IQR bounds (${lowerBound.toFixed(2)} to ${upperBound.toFixed(2)}).`,
          priority: "medium",
          rationale:
            "Values outside the 1.5 × IQR boundaries may indicate unusual business activity and should be investigated.",
          confidence: 0.85,
        });
      }
    }

    if (metric.minimum < 0) {
      recommendations.push({
        title: `Review negative values in ${metric.field}`,
        description:
          `At least one negative value was found (minimum: ${metric.minimum}).`,
        priority: "high",
        rationale:
          "Negative values may be valid, but should be checked against the business meaning of this field.",
        confidence: 0.8,
      });
    }
  }

  if (recommendations.length === 0) {
    recommendations.push({
      title: "Define business-specific performance thresholds",
      description:
        "No obvious numeric anomaly was detected by the baseline rules.",
      priority: "low",
      rationale:
        "Domain-specific thresholds make future recommendations more relevant and measurable.",
      confidence: 0.65,
    });
  }

  return recommendations;
}


function generateTimeSeries(
  records: RecordRow[],
  metrics: Metric[],
): TimeSeriesPoint[] {
  if (records.length === 0) {
    return [];
  }

  const dateColumn = Object.keys(records[0]).find((column) =>
    /^(date|datum|timestamp|time|created_at|order_date)$/i.test(column.trim()),
  );

  if (!dateColumn) {
    return [];
  }

  return records
    .map((row) => {
      const rawDate = row[dateColumn];

      if (typeof rawDate !== "string") {
        return null;
      }

      const timestamp = Date.parse(rawDate);

      if (!Number.isFinite(timestamp)) {
        return null;
      }

      const point: TimeSeriesPoint = {
        date: new Date(timestamp).toISOString(),
      };

      for (const metric of metrics) {
        const value = row[metric.field];

        if (typeof value === "number") {
          point[metric.field] = value;
        }
      }

      return { timestamp, point };
    })
    .filter(
      (entry): entry is { timestamp: number; point: TimeSeriesPoint } =>
        entry !== null,
    )
    .sort((a, b) => a.timestamp - b.timestamp)
    .map((entry) => entry.point);
}
export async function analyzeLocally(file: File): Promise<Analysis> {
  const records = await parseCsv(file);
  const metrics = calculateMetrics(records);
  const recommendations = generateRecommendations(metrics, records);
  const timeSeries = generateTimeSeries(records, metrics);

  return {
    id: 0,
    dataset_name: file.name,
    record_count: records.length,
    created_at: new Date().toISOString(),
    result: {
      summary:
        `Analyzed ${records.length} records in '${file.name}'. ` +
        `Found ${metrics.length} numeric fields.`,
      record_count: records.length,
      numeric_metrics: metrics,
      time_series: timeSeries,
      recommendations,
      llm_enhanced: false,
    },
  };
}
