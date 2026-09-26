import { useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Code2,
  FileCode2,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Wrench,
  Terminal,
  Zap,
} from "lucide-react";
import heroVisual from "./assets/hero.png";

import "./App.css";

type Severity = "low" | "medium" | "high" | "critical";

interface Finding {
  id: string;
  category: string;
  severity: Severity;
  title: string;
  description: string;
  line: number | null;
  recommendation: string;
}

interface Scores {
  security: number;
  maintainability: number;
  modernization: number;
  overall: number;
}

interface Analysis {
  language: string;
  lines_of_code: number;
  findings: Finding[];
  scores: Scores;
  modernization_plan: string[];
  summary: string;
}

interface Modernization {
  language: string;
  original_code: string;
  modernized_code: string;
  changes: string[];
  unified_diff: string;
  before_scores: Scores;
  after_scores: Scores;
  before_findings: number;
  after_findings: number;
  score_improvement: number;
  findings_resolved: number;
}

const API = "http://127.0.0.1:8000";

const samples: Record<string, string> = {
  python: `import os
import pickle

password = "admin123"
api_key = "demo-secret-key"

def process():
    expression = input("Expression: ")
    result = eval(expression)

    os.system(input("Command: "))

    data = pickle.loads(input("Data: "))

    try:
        print(result)
    except:
        print("failed")

# TODO: remove legacy implementation
`,

  javascript: `function legacyLogin(user) {
  var username = user;

  if (username == "admin") {
    var message = "Welcome";
    return message;
  }

  return "Denied";
}`,

  java: `import java.util.Vector;
import java.util.Hashtable;

public class LegacyApplication {

    public static void main(String[] args) {
        Vector<String> users = new Vector<>();
        Hashtable<String, String> config = new Hashtable<>();

        users.add("admin");

        System.out.println(users);
        System.out.println(config);
    }
}`,
};

function scoreLabel(score: number) {
  if (score >= 90) return "Excellent";
  if (score >= 75) return "Healthy";
  if (score >= 55) return "Needs attention";
  return "High risk";
}

function App() {
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(samples.python);

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [modernization, setModernization] =
    useState<Modernization | null>(null);

  const [loading, setLoading] = useState(false);
  const [modernizing, setModernizing] = useState(false);
  const [error, setError] = useState("");

  const severityCounts = useMemo(() => {
    const counts = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
    };

    if (!analysis) {
      return counts;
    }

    for (const finding of analysis.findings) {
      counts[finding.severity] += 1;
    }

    return counts;
  }, [analysis]);

  function changeLanguage(nextLanguage: string) {
    setLanguage(nextLanguage);
    setCode(samples[nextLanguage]);
    setAnalysis(null);
    setModernization(null);
    setError("");
  }

  async function analyzeCode() {
    if (!code.trim()) {
      setError("Add some source code before running analysis.");
      return;
    }

    setLoading(true);
    setError("");
    setModernization(null);

    try {
      const response = await fetch(`${API}/api/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code,
          language,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);

        throw new Error(
          data?.detail || `Analysis failed with status ${response.status}.`,
        );
      }

      const data: Analysis = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to the RecodeAI backend.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function modernizeCode() {
    if (!code.trim()) {
      return;
    }

    setModernizing(true);
    setError("");

    try {
      const response = await fetch(`${API}/api/modernize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code,
          language,
          apply_safe_fixes: true,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);

        throw new Error(
          data?.detail ||
            `Modernization failed with status ${response.status}.`,
        );
      }

      const data: Modernization = await response.json();
      setModernization(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to generate modernization suggestions.",
      );
    } finally {
      setModernizing(false);
    }
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to code analysis</a>
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <div className="brand-mark">
              <Code2 size={19} />
            </div>

            <div>
              <strong>RecodeAI</strong>
              <span>Explainable modernization</span>
            </div>
          </div>

          <div className="topbar-actions">
            <span className="engine-pill"><Terminal size={12} /> API :8000</span>
            <div className="topbar-status">
            <span className="status-dot" />
            Deterministic analysis engine
            </div>
          </div>
        </div>
      </header>

      <main className="container" id="main-content">
        <section className="hero">
          <div className="eyebrow">
            <Sparkles size={13} />
            RECODEAI // LEGACY CODE INTELLIGENCE
          </div>

          <h1>
            Understand legacy code
            <br />
            <span>before you rewrite it.</span>
          </h1>

          <p>
            RecodeAI detects modernization risks, explains why they matter,
            creates a prioritized remediation plan and measures whether
            conservative transformations actually improve the code.
          </p>
          <div className="hero-pills">
            <span><ShieldCheck size={13} /> Explainable findings</span>
            <span><Zap size={13} /> Measurable impact</span>
            <span><Code2 size={13} /> Python · JS · Java</span>
          </div>
          <div className="hero-visual" aria-hidden="true">
            <span className="hero-visual-label">TRACE / REVIEW / REPAIR</span>
            <img src={heroVisual} alt="" />
            <span className="hero-visual-note">A safer path through legacy systems.</span>
          </div>
        </section>

        <section className="workspace-grid">
          <div className={`panel editor-panel ${loading ? "is-scanning" : ""}`}>
            <div className="panel-header">
              <div>
                <div className="panel-title">
                  <FileCode2 size={16} />
                  Source code
                </div>

                <p>
                  Paste legacy source code or start with one of the demo
                  samples.
                </p>
              </div>

              <select
                className="language-select"
                value={language}
                onChange={(event) => changeLanguage(event.target.value)}
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
              </select>
            </div>

            <textarea
              className="code-editor"
              aria-label="Source code to analyze"
              value={code}
              spellCheck={false}
              onChange={(event) => {
                setCode(event.target.value);
                setAnalysis(null);
                setModernization(null);
              }}
            />

            <div className="editor-footer">
              <span>
                {code.split("\n").length} lines · {code.length} characters
              </span>

              <button
                className="primary-button"
                onClick={analyzeCode}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <RefreshCw className="spin" size={15} />
                    Analyzing
                  </>
                ) : (
                  <>
                    <Activity size={15} />
                    Analyze code
                  </>
                )}
              </button>
            </div>
          </div>

          <aside className="panel overview-panel">
            <div className="panel-header compact">
              <div>
                <div className="panel-title">
                  <ShieldCheck size={16} />
                  Modernization health
                </div>

                <p>Explainable engineering signals</p>
              </div>
            </div>

            {!analysis ? (
              <div className="empty-overview">
                <div className="empty-icon">
                  <Activity size={24} />
                </div>

                <strong>Waiting for analysis</strong>

                <p>
                  Run the analyzer to calculate security, maintainability and
                  modernization health.
                </p>
              </div>
            ) : (
              <>
                <div className="overall-score">
                  <div className="score-ring" style={{ "--score": `${analysis.scores.overall * 3.6}deg` } as React.CSSProperties}>
                    <strong>{analysis.scores.overall}</strong>
                    <span>/100</span>
                  </div>

                  <div>
                    <span className="score-caption">OVERALL HEALTH</span>
                    <strong className="score-label">
                      {scoreLabel(analysis.scores.overall)}
                    </strong>
                  </div>
                </div>

                <div className="score-stack">
                  <ScoreCard
                    label="Security"
                    value={analysis.scores.security}
                  />

                  <ScoreCard
                    label="Maintainability"
                    value={analysis.scores.maintainability}
                  />

                  <ScoreCard
                    label="Modernization"
                    value={analysis.scores.modernization}
                  />
                </div>
              </>
            )}
          </aside>
        </section>

        {error && (
          <div className="error-banner">
            <AlertTriangle size={17} />
            <div>
              <strong>RecodeAI could not complete the request.</strong>
              <span>{error}</span>
            </div>
          </div>
        )}

        {analysis && (
          <>
            <section className="metrics-grid">
              <Metric
                label="TOTAL FINDINGS"
                value={analysis.findings.length}
                detail="detected issues"
              />

              <Metric
                label="CRITICAL"
                value={severityCounts.critical}
                detail="immediate attention"
              />

              <Metric
                label="HIGH"
                value={severityCounts.high}
                detail="priority findings"
              />

              <Metric
                label="LINES ANALYZED"
                value={analysis.lines_of_code}
                detail={analysis.language}
              />
            </section>

            <section className="panel results-panel">
              <div className="section-heading">
                <div>
                  <span className="section-kicker">ANALYSIS RESULTS</span>
                  <h2>Explainable findings</h2>
                </div>

                <span className="finding-count">
                  {analysis.findings.length} findings
                </span>
              </div>

              <p className="analysis-summary">{analysis.summary}</p>

              {analysis.findings.length === 0 ? (
                <div className="clean-state">
                  <CheckCircle2 size={22} />
                  <div>
                    <strong>No high-confidence findings detected</strong>
                    <p>
                      The current deterministic rule set did not identify a
                      known modernization issue in this sample.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="findings-list">
                  {analysis.findings.map((finding) => (
                    <article
                      className="finding-card"
                      key={`${finding.id}-${finding.line}`}
                    >
                      <div className="finding-topline">
                        <div className="finding-identity">
                          <span
                            className={`severity severity-${finding.severity}`}
                          >
                            {finding.severity}
                          </span>

                          <span className="category">
                            {finding.category}
                          </span>

                          {finding.line !== null && (
                            <span className="line-number">
                              line {finding.line}
                            </span>
                          )}
                        </div>

                        <span className="finding-id">{finding.id}</span>
                      </div>

                      <h3>{finding.title}</h3>

                      <p>{finding.description}</p>

                      <div className="recommendation">
                        <Wrench size={14} />

                        <div>
                          <span>RECOMMENDATION</span>
                          <p>{finding.recommendation}</p>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>

            <section className="two-column-section">
              <div className="panel plan-panel">
                <div className="section-heading">
                  <div>
                    <span className="section-kicker">PRIORITIZED ROADMAP</span>
                    <h2>Modernization plan</h2>
                  </div>
                </div>

                <div className="plan-list">
                  {analysis.modernization_plan.map((step, index) => (
                    <div className="plan-item" key={`${step}-${index}`}>
                      <span>{String(index + 1).padStart(2, "0")}</span>

                      <p>{step}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="panel action-panel">
                <span className="section-kicker">CONSERVATIVE TRANSFORMATION</span>

                <h2>Generate a modernization candidate</h2>

                <p>
                  RecodeAI applies only deterministic transformations supported
                  by the current MVP and then re-analyzes the output using the
                  same scoring engine.
                </p>

                <div className="safety-note">
                  <ShieldCheck size={17} />

                  <span>
                    Potentially behavior-changing issues remain recommendations
                    for developer review.
                  </span>
                </div>

                <button
                  className="primary-button full-width"
                  onClick={modernizeCode}
                  disabled={modernizing}
                >
                  {modernizing ? (
                    <>
                      <RefreshCw className="spin" size={15} />
                      Generating candidate
                    </>
                  ) : (
                    <>
                      <Sparkles size={15} />
                      Generate modernization
                    </>
                  )}
                </button>
              </div>
            </section>
          </>
        )}

        {modernization && (
          <section className="panel modernization-panel">
            <div className="section-heading">
              <div>
                <span className="section-kicker">MEASURABLE IMPACT</span>
                <h2>Modernization result</h2>
              </div>

              <span className="candidate-badge">
                Re-analyzed automatically
              </span>
            </div>

            <div className="impact-grid">
              <div className="impact-score">
                <span>BEFORE</span>
                <strong>{modernization.before_scores.overall}</strong>
                <small>/100</small>
              </div>

              <ArrowRight size={22} />

              <div className="impact-score">
                <span>AFTER</span>
                <strong>{modernization.after_scores.overall}</strong>
                <small>/100</small>
              </div>

              <div className="impact-result">
                <span>HEALTH IMPROVEMENT</span>
                <strong>
                  {modernization.score_improvement >= 0 ? "+" : ""}
                  {modernization.score_improvement}
                </strong>
                <small>points</small>
              </div>

              <div className="impact-result">
                <span>FINDINGS RESOLVED</span>
                <strong>{modernization.findings_resolved}</strong>
                <small>
                  of {modernization.before_findings}
                </small>
              </div>
            </div>

            <div className="change-list">
              <span className="change-heading">TRANSFORMATIONS</span>

              {modernization.changes.map((change, index) => (
                <div className="change-item" key={`${change}-${index}`}>
                  <CheckCircle2 size={15} />
                  <span>{change}</span>
                </div>
              ))}
            </div>

            <div className="code-comparison">
              <CodePanel
                title="BEFORE"
                code={modernization.original_code}
              />

              <CodePanel
                title="AFTER"
                code={modernization.modernized_code}
              />
            </div>

            <div className="diff-section">
              <div className="diff-header">
                <Code2 size={15} />
                Unified diff
              </div>

              <pre className="diff-view">
                {modernization.unified_diff ||
                  "No deterministic source-code transformation was applied."}
              </pre>
            </div>
          </section>
        )}

        <footer>
          <div className="footer-brand">
            <Code2 size={15} />
            RecodeAI
          </div>

          <span>
            Explainable legacy-code modernization · MVP
          </span>
        </footer>
      </main>
    </div>
  );
}

function ScoreCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="score-card">
      <div className="score-card-header">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>

      <div className="score-bar">
        <div
          className="score-bar-fill"
          style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
        />
      </div>
    </div>
  );
}

function Metric({
  label,
  value,
  detail,
}: {
  label: string;
  value: number | string;
  detail: string;
}) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function CodePanel({
  title,
  code,
}: {
  title: string;
  code: string;
}) {
  return (
    <div className="code-panel">
      <div className="code-panel-header">
        <span>{title}</span>
        <small>{code.split("\n").length} lines</small>
      </div>

      <pre>{code}</pre>
    </div>
  );
}

export default App;
