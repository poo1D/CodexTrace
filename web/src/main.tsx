import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  CheckCircle2,
  Code2,
  FileText,
  GitCompare,
  ListFilter,
  Search,
  Terminal,
  Timer,
  Wrench,
} from "lucide-react";
import "./styles.css";

type TraceEvent = {
  id: string;
  kind: string;
  status: string;
  title: string;
  detail: string;
  phase?: string;
  command?: string | null;
  exit_code?: number | null;
  files: string[];
};

type Finding = {
  code: string;
  title: string;
  severity: "low" | "medium" | "high";
  evidence: string[];
  recommendation: string;
  event_ids: string[];
};

type Report = {
  trace: {
    thread_id: string;
    usage: Record<string, number>;
    events: TraceEvent[];
  };
  diagnosis: {
    outcome: "healthy" | "warning" | "failed";
    failure_score: number;
    summary: string;
    metrics: Record<string, number>;
    findings: Finding[];
  };
};

type Run = {
  id: string;
  task_id: string;
  prompt_type: "baseline" | "intervention" | string;
  outcome: "success" | "failure" | "unknown" | string;
  report: Report;
  diff?: string;
  test_log?: string;
  report_path?: string;
};

type DashboardData = {
  runs: Run[];
};

const demoRuns: Run[] = [
  {
    id: "SM-001-baseline",
    task_id: "SM-001",
    prompt_type: "baseline",
    outcome: "failure",
    diff: "diff --git a/src/calc.py b/src/calc.py\n-    return sum(values[: n + 1])\n+    return sum(values[:n])",
    test_log: "FAILED tests/test_calc.py::test_sum_prefix - assert 10 == 6",
    report: makeReport("demo-thread-baseline", "failed", 100, "src/calc.py", "pytest -q", 1),
  },
  {
    id: "SM-001-intervention",
    task_id: "SM-001",
    prompt_type: "intervention",
    outcome: "success",
    diff: "diff --git a/src/calc.py b/src/calc.py\n-    return sum(values[: n + 1])\n+    return sum(values[:n])",
    test_log: "3 passed in 0.02s",
    report: makeReport("demo-thread-intervention", "healthy", 0, "src/calc.py", "python3 -m unittest discover -s tests", 0),
  },
];

function makeReport(thread: string, outcome: Report["diagnosis"]["outcome"], score: number, file: string, command: string, exitCode: number): Report {
  const failed = exitCode !== 0;
  return {
    trace: {
      thread_id: thread,
      usage: { input_tokens: failed ? 28600 : 21400, output_tokens: failed ? 900 : 620 },
      events: [
        { id: "e0000", kind: "thread", status: "in_progress", title: "thread.started", detail: "", files: [] },
        { id: "e0001", kind: "command", status: "completed", title: "rg target", detail: file, command: "rg target", exit_code: 0, files: [] },
        { id: "e0002", kind: "file_change", status: "completed", title: "file change", detail: file, files: [file] },
        { id: "e0003", kind: "command", status: failed ? "failed" : "completed", title: command, detail: failed ? "FAILED tests/test_calc.py" : "3 passed", command, exit_code: exitCode, files: [] },
        { id: "e0004", kind: "turn", status: "completed", title: "turn.completed", detail: "", files: [] },
      ],
    },
    diagnosis: {
      outcome,
      failure_score: score,
      summary: failed ? "Failed trace: verification ended red after an edit." : "No obvious failure pattern was detected in this trace.",
      metrics: {
        events: 5,
        command_events: 2,
        failed_commands: failed ? 1 : 0,
        file_change_events: 1,
        verification_commands: 1,
        input_tokens: failed ? 28600 : 21400,
      },
      findings: failed
        ? [
            {
              code: "command_failure_unhandled",
              title: "Command failures were not clearly handled",
              severity: "high",
              evidence: ["e0003 command failed"],
              recommendation: "Repair the failure and rerun the focused verification command.",
              event_ids: ["e0003"],
            },
          ]
        : [],
    },
  };
}

function App() {
  const [runs, setRuns] = useState<Run[]>(demoRuns);
  const [selectedRunId, setSelectedRunId] = useState(demoRuns[0].id);
  const [phaseFilter, setPhaseFilter] = useState("all");
  const [kindFilter, setKindFilter] = useState("all");

  useEffect(() => {
    loadRuns().then((loaded) => {
      setRuns(loaded);
      setSelectedRunId(loaded[0]?.id ?? demoRuns[0].id);
    });
  }, []);

  const selected = runs.find((run) => run.id === selectedRunId) ?? runs[0];
  const paired = runs.find((run) => run.task_id === selected.task_id && run.prompt_type !== selected.prompt_type);
  const highlighted = new Set(selected.report.diagnosis.findings.flatMap((finding) => finding.event_ids));
  const phases = uniqueValues(selected.report.trace.events.map((event) => event.phase ?? "other"));
  const kinds = uniqueValues(selected.report.trace.events.map((event) => event.kind));
  const visibleEvents = selected.report.trace.events.filter((event) => {
    const phaseMatches = phaseFilter === "all" || (event.phase ?? "other") === phaseFilter;
    const kindMatches = kindFilter === "all" || event.kind === kindFilter;
    return phaseMatches && kindMatches;
  });
  const taskIds = uniqueValues(runs.map((run) => run.task_id));
  const summary = useMemo(() => summarizeRuns(runs), [runs]);

  return (
    <main>
      <header className="topbar">
        <div>
          <p className="eyebrow">Agent Harness</p>
          <h1>CodexTrace</h1>
        </div>
        <div className="top-actions">
          <div className={`status ${selected.report.diagnosis.outcome}`}>
            {selected.report.diagnosis.outcome === "healthy" ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
            {selected.report.diagnosis.outcome}
          </div>
        </div>
      </header>

      <section className="summary">
        <Metric label="Runs" value={runs.length} />
        <Metric label="Tasks" value={taskIds.length} />
        <Metric label="Failures" value={summary.failures} />
        <Metric label="Mean score" value={summary.meanScore} />
      </section>

      <section className="dashboard">
        <aside className="run-list">
          <div className="panel-heading">
            <ListFilter size={17} />
            <h2>Runs</h2>
          </div>
          {runs.map((run) => (
            <button
              className={`run-row ${run.id === selected.id ? "active" : ""}`}
              key={run.id}
              onClick={() => setSelectedRunId(run.id)}
            >
              <span>{run.task_id}</span>
              <code>{run.prompt_type}</code>
              <strong className={run.outcome}>{run.outcome}</strong>
            </button>
          ))}
        </aside>

        <section className="workspace">
          <section className="compare-band">
            <div>
              <div className="panel-heading">
                <GitCompare size={17} />
                <h2>Comparison</h2>
              </div>
              <div className="compare-grid">
                <CompareCell label={selected.prompt_type} run={selected} />
                <CompareCell label={paired?.prompt_type ?? "paired"} run={paired} />
              </div>
            </div>
            <div className="tag-strip">
              {selected.report.diagnosis.findings.length === 0 ? (
                <span className="tag healthy">healthy</span>
              ) : (
                selected.report.diagnosis.findings.map((finding) => (
                  <span className={`tag ${finding.severity}`} key={finding.code}>
                    {finding.code}
                  </span>
                ))
              )}
            </div>
          </section>

          <section className="artifact-grid">
            <Panel title="Diff">
              <pre>{selected.diff || "No diff captured."}</pre>
            </Panel>
            <Panel title="Test Log">
              <pre>{selected.test_log || selected.report.diagnosis.summary}</pre>
            </Panel>
          </section>

          <section className="timeline">
            <div className="timeline-toolbar">
              <div className="panel-heading">
                <Timer size={17} />
                <h2>Timeline</h2>
              </div>
              <div className="filters">
                <select value={phaseFilter} onChange={(event) => setPhaseFilter(event.target.value)} aria-label="Phase filter">
                  <option value="all">all phases</option>
                  {phases.map((phase) => (
                    <option value={phase} key={phase}>
                      {phase}
                    </option>
                  ))}
                </select>
                <select value={kindFilter} onChange={(event) => setKindFilter(event.target.value)} aria-label="Kind filter">
                  <option value="all">all kinds</option>
                  {kinds.map((kind) => (
                    <option value={kind} key={kind}>
                      {kind}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            {visibleEvents.map((event) => (
              <article className={`event ${event.status} ${highlighted.has(event.id) ? "highlighted" : ""}`} key={event.id}>
                <div className="event-icon">{iconFor(event.kind)}</div>
                <div className="event-body">
                  <div className="event-meta">
                    <code>{event.id}</code>
                    <span>{event.kind}</span>
                    <span>{event.phase ?? "other"}</span>
                    <span>{event.status}</span>
                  </div>
                  <h3>{event.title}</h3>
                  {event.detail && <p>{event.detail}</p>}
                </div>
              </article>
            ))}
          </section>
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function CompareCell({ label, run }: { label: string; run?: Run }) {
  return (
    <div className="compare-cell">
      <span>{label}</span>
      <strong>{run ? `${run.report.diagnosis.failure_score}/100` : "-"}</strong>
      <code>{run?.outcome ?? "missing"}</code>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="artifact-panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

async function loadRuns(): Promise<Run[]> {
  const multi = await fetchJson<DashboardData>("/reports.json");
  if (multi?.runs?.length) return multi.runs;
  const single = await fetchJson<Report>("/report.json");
  if (single?.trace && single?.diagnosis) {
    return [
      {
        id: single.trace.thread_id || "report",
        task_id: "demo",
        prompt_type: "baseline",
        outcome: single.diagnosis.outcome === "healthy" ? "success" : "failure",
        report: single,
      },
    ];
  }
  return demoRuns;
}

async function fetchJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(path);
    return response.ok ? ((await response.json()) as T) : null;
  } catch {
    return null;
  }
}

function summarizeRuns(items: Run[]) {
  const failures = items.filter((run) => run.outcome === "failure" || run.report.diagnosis.outcome === "failed").length;
  const meanScore = items.length
    ? Math.round(items.reduce((total, run) => total + run.report.diagnosis.failure_score, 0) / items.length)
    : 0;
  return { failures, meanScore };
}

function uniqueValues(values: string[]) {
  return Array.from(new Set(values)).sort();
}

function iconFor(kind: string) {
  if (kind === "command") return <Terminal size={18} />;
  if (kind === "file_change") return <FileText size={18} />;
  if (kind === "web_search") return <Search size={18} />;
  if (kind === "mcp_tool") return <Wrench size={18} />;
  if (kind === "agent_message") return <Code2 size={18} />;
  return <Timer size={18} />;
}

createRoot(document.getElementById("root")!).render(<App />);
