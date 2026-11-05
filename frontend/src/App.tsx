
import {
  useRef,
  useState,
  type ChangeEvent,
} from "react";
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  Database,
  Download,
  FileUp,
  LayoutDashboard,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { analyzeLocally } from "./services/localAnalysis";
import { downloadCsvTemplate } from "./utils/csvTemplate";
import type { Analysis } from "./types/analysis";

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
  }).format(value);
}

interface DashboardProps {
  analysis: Analysis | null;
  onUpload: (file: File) => Promise<void>;
  uploading: boolean;
  uploadError: string;
  onClear: () => void;
}

function Dashboard({
  analysis,
  onUpload,
  uploading,
  uploadError,
  onClear,
}: DashboardProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedMetric, setSelectedMetric] = useState("revenue");

  const metrics = analysis?.result.numeric_metrics ?? [];
const timeSeries = analysis?.result.time_series ?? [];
const recommendations = analysis?.result.recommendations ?? [];

const selectedMetricField = metrics.some(
  (metric) => metric.field === selectedMetric,
)
  ? selectedMetric
  : metrics.find((metric) => metric.field.toLowerCase() === "revenue")
      ?.field ?? metrics[0]?.field ?? "";

  const kpis = [
    {
      title: "Analyzed Records",
      value: analysis ? formatNumber(analysis.record_count) : "—",
      icon: Database,
    },
    {
      title: "Numeric Fields",
      value: analysis ? formatNumber(metrics.length) : "—",
      icon: Activity,
    },
    {
      title: "Recommendations",
      value: analysis ? formatNumber(recommendations.length) : "—",
      icon: Sparkles,
    },
    {
      title: "External AI",
      value: "Disabled",
      icon: TrendingUp,
    },
  ];

  async function handleFileChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (file) {
      await onUpload(file);
      event.target.value = "";
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <BarChart3 size={22} />
          </div>
          <div>
            <strong>InsightAI</strong>
            <span>BUSINESS INTELLIGENCE</span>
          </div>
        </div>

        <div className="nav-section">
          <span className="nav-label">WORKSPACE</span>

          <a className="nav-link active" href="#dashboard">
            <LayoutDashboard size={18} />
            Dashboard
          </a>

          <a className="nav-link" href="#datasets">
            <Database size={18} />
            Analysis
          </a>

          <a className="nav-link" href="#insights">
            <Sparkles size={18} />
            Statistical Insights
          </a>
        </div>

        <div className="sidebar-bottom">
          <div className="profile">
            <div className="avatar">DE</div>
            <div className="profile-info">
              <strong>Public Demo</strong>
              <span>No account required</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace / Overview</span>
            <h1>Dashboard</h1>
          </div>

          <span className="connection-status">
            <span className="connection-dot" />
            Local processing
          </span>
        </header>

        <section className="welcome">
          <div>
            <h2>Welcome to InsightAI</h2>
            <p>
              {analysis
                ? `Latest analysis: ${analysis.dataset_name}`
                : "Upload a CSV file to discover business insights."}
            </p>
          </div>

          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,text/csv"
              hidden
              onChange={handleFileChange}
            />

            <button
              className="primary-button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              <FileUp size={17} />
              {uploading ? "Analyzing..." : "Select CSV file"}
            </button>

            <button
              type="button"
              onClick={downloadCsvTemplate}
              className="template-download-button"
            >
              <Download size={16} />
              Download CSV template
            </button>
          </div>
        </section>

        <section className="privacy-notice">
          <ShieldCheck size={20} />
          <div>
            <strong>Privacy-first processing</strong>
            <p>
              CSV files are processed locally in your browser.
              The application does not upload CSV contents to an
              application server or persist analysis results.
              Use synthetic data for this public demo.
            </p>
          </div>
        </section>

        {uploadError && (
          <p className="error-message upload-error">{uploadError}</p>
        )}

        <section className="metrics-grid">
          {kpis.map((metric) => {
            const Icon = metric.icon;

            return (
              <article className="metric-card" key={metric.title}>
                <div className="metric-top">
                  <span>{metric.title}</span>
                  <div className="metric-icon">
                    <Icon size={19} />
                  </div>
                </div>

                <strong className="metric-value">
                  {metric.value}
                </strong>

                <div className="metric-change">
                  <small>
                    {analysis ? "From current analysis" : "Waiting for data"}
                  </small>
                </div>
              </article>
            );
          })}
        </section>

        <section className="content-grid">
         <article className="panel revenue-panel">
  <div className="panel-header">
    <div>
      <h3>Time Series Analysis</h3>
      <p>Chronological development of your selected metric</p>
    </div>

    {timeSeries.length > 0 && (
      <select
        value={selectedMetricField}
        onChange={(event) => setSelectedMetric(event.target.value)}
        aria-label="Select metric"
      >
        {metrics.map((metric) => (
          <option key={metric.field} value={metric.field}>
            {metric.field}
          </option>
        ))}
      </select>
    )}
  </div>

  {timeSeries.length > 0 && selectedMetricField ? (
    <>
      <div className="chart-summary">
        <strong>{timeSeries.length}</strong>
        <span>time points analyzed</span>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={timeSeries}>
            <defs>
              <linearGradient
                id="metricsGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop offset="0%" stopColor="#818cf8" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid
              stroke="#273449"
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#8995a9", fontSize: 11 }}
              tickFormatter={(value: string) =>
                new Intl.DateTimeFormat("de-DE", {
                  day: "2-digit",
                  month: "short",
                }).format(new Date(value))
              }
            />

            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#8995a9", fontSize: 11 }}
            />

            <Tooltip
              labelFormatter={(value) =>
                new Intl.DateTimeFormat("de-DE", {
                  dateStyle: "medium",
                }).format(new Date(String(value)))
              }
              contentStyle={{
                backgroundColor: "#111827",
                border: "1px solid #273449",
                borderRadius: "10px",
                color: "#fff",
              }}
            />

            <Area
              type="monotone"
              dataKey={selectedMetricField}
              name={selectedMetricField}
              stroke="#818cf8"
              strokeWidth={3}
              fill="url(#metricsGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </>
  ) : (
    <div className="empty-state">
      <Database size={30} />
      <strong>No time-series data</strong>
      <p>
        Upload a CSV containing a date column and numeric values to display
        the timeline.
      </p>
    </div>
  )}
</article>

          <article className="panel insights-panel" id="insights">
            <div className="panel-header">
              <div>
                <h3>Statistical Insights</h3>
                <p>Recommendations from local analysis rules</p>
              </div>

              <Sparkles size={20} color="#a78bfa" />
            </div>

            {recommendations.length > 0 ? (
              <div className="insights-list">
                {recommendations.map((item, index) => (
                  <div
                    className="insight-item"
                    key={`${item.title}-${index}`}
                  >
                    <div
                      className={`insight-indicator ${
                        item.priority === "high"
                          ? "suggestion"
                          : "positive"
                      }`}
                    />

                    <div>
                      <strong>{item.title}</strong>
                      <p>{item.description}</p>
                      <small>
                        Priority: {item.priority} · Confidence:{" "}
                        {Math.round(item.confidence * 100)}%
                      </small>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state compact">
                <Sparkles size={26} />
                <p>
                  Recommendations will appear here after your first analysis.
                </p>
              </div>
            )}
          </article>
        </section>

        <section className="panel datasets-panel" id="datasets">
          <div className="panel-header">
            <div>
              <h3>Current Analysis</h3>
              <p>Temporary results held in browser memory</p>
            </div>

            {analysis && (
              <button
                type="button"
                className="template-download-button"
                onClick={onClear}
              >
                Clear results
              </button>
            )}
          </div>

          {analysis ? (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>DATASET NAME</th>
                    <th>RECORDS</th>
                    <th>ANALYZED AT</th>
                    <th>STATUS</th>
                  </tr>
                </thead>

                <tbody>
                  <tr>
                    <td>
                      <strong>{analysis.dataset_name}</strong>
                    </td>
                    <td>{formatNumber(analysis.record_count)}</td>
                    <td>
                      {new Date(analysis.created_at).toLocaleString()}
                    </td>
                    <td>
                      <span className="status">
                        <CheckCircle2 size={14} />
                        Completed
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <FileUp size={28} />
              <p>No analysis currently loaded.</p>
            </div>
          )}
        </section>

        {analysis && (
          <section className="panel summary-panel">
            <div className="panel-header">
              <div>
                <h3>Analysis Summary</h3>
                <p>Generated locally in your browser</p>
              </div>

              <ArrowUpRight size={18} color="#a5b4fc" />
            </div>

            <p>{analysis.result.summary}</p>
          </section>
        )}

        <footer className="footer">
          <span>InsightAI · Privacy-first demo</span>

          <span>
            <span className="connection-dot" />
            Local processing · No application database
          </span>
        </footer>
      </main>
    </div>
  );
}

function App() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  async function handleUpload(file: File) {
    setUploading(true);
    setUploadError("");
    setAnalysis(null);

    try {
      const result = await analyzeLocally(file);
      setAnalysis(result);
    } catch (error) {
      setUploadError(
        error instanceof Error
          ? error.message
          : "CSV analysis failed.",
      );
    } finally {
      setUploading(false);
    }
  }

  function handleClear() {
    setAnalysis(null);
    setUploadError("");
  }

  return (
    <Dashboard
      analysis={analysis}
      onUpload={handleUpload}
      uploading={uploading}
      uploadError={uploadError}
      onClear={handleClear}
    />
  );
}

export default App;
