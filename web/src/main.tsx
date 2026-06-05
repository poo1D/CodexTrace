import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, CheckCircle2, Code2, FileText, Search, Terminal, Timer, Wrench } from "lucide-react";
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

const demoReport: Report = {
  trace: {
    thread_id: "demo-thread-001",
    usage: { input_tokens: 28600, cached_input_tokens: 12000, output_tokens: 900, reasoning_output_tokens: 220 },
    events: [
      { id: "e0000", kind: "thread", status: "in_progress", title: "thread.started", detail: "", files: [] },
      { id: "e0001", kind: "turn", status: "in_progress", title: "turn.started", detail: "", files: [] },
      { id: "e0002", kind: "agent_message", status: "completed", title: "I will inspect the repository and find the failing tests.", detail: "I will inspect the repository and find the failing tests.", files: [] },
      { id: "e0003", kind: "command", status: "completed", title: "rg \"calculate_total\"", detail: "src/cart.py:def calculate_total(items):", command: "rg \"calculate_total\"", exit_code: 0, files: [] },
      { id: "e0004", kind: "command", status: "completed", title: "rg \"calculate_total\"", detail: "src/cart.py:def calculate_total(items):", command: "rg \"calculate_total\"", exit_code: 0, files: [] },
      { id: "e0005", kind: "command", status: "failed", title: "pytest -q", detail: "FAILED tests/test_cart.py::test_discount", command: "pytest -q", exit_code: 1, files: [] },
      { id: "e0006", kind: "file_change", status: "completed", title: "file change", detail: "src/cart.py", files: ["src/cart.py"] },
      { id: "e0007", kind: "command", status: "failed", title: "npm install", detail: "permission denied by sandbox: network access requires approval", command: "npm install", exit_code: 1, files: [] },
      { id: "e0008", kind: "agent_message", status: "completed", title: "I updated the implementation. The task is complete.", detail: "I updated the implementation. The task is complete.", files: [] },
      { id: "e0009", kind: "turn", status: "completed", title: "turn.completed", detail: "input_tokens=28600, cached_input_tokens=12000, output_tokens=900, reasoning_output_tokens=220", files: [] }
    ]
  },
  diagnosis: {
    outcome: "failed",
    failure_score: 100,
    summary: "Failed trace: Command failures were not clearly handled. 10 events, 4 commands, 2 failed commands.",
    metrics: { events: 10, command_events: 4, failed_commands: 2, file_change_events: 1, verification_commands: 1, post_edit_verification_commands: 0, search_commands: 2, input_tokens: 28600, output_tokens: 900, reasoning_output_tokens: 220 },
    findings: [
      { code: "command_failure_unhandled", title: "Command failures were not clearly handled", severity: "high", evidence: ["e0007 command: npm install exit_code=1"], recommendation: "After a failed command, add an explicit repair step and rerun the relevant verification command before ending the turn.", event_ids: ["e0007"] },
      { code: "verification_gap", title: "Files changed without a verification command", severity: "high", evidence: ["1 file-change event(s), 0 post-edit verification command(s)."], recommendation: "Add a post-edit validation step such as tests, type checks, or a focused smoke command.", event_ids: ["e0006"] },
      { code: "repeated_search_or_read", title: "Repeated search/read commands suggest inefficient exploration", severity: "medium", evidence: ["`rg \"calculate_total\"` repeated 2 times"], recommendation: "Summarize discovered facts after each exploration pass and switch from broad search to targeted file reads.", event_ids: [] },
      { code: "sandbox_or_permission_block", title: "Sandbox or permission friction blocked progress", severity: "medium", evidence: ["e0007 command: npm install exit_code=1"], recommendation: "Declare the needed permission up front, reduce the command scope, or redesign the workflow to keep privileged steps outside the agent loop.", event_ids: ["e0007"] }
    ]
  }
};

function App() {
  const [report, setReport] = useState<Report>(demoReport);

  useEffect(() => {
    fetch("/report.json")
      .then((response) => (response.ok ? response.json() : demoReport))
      .then((data: Report) => setReport(data))
      .catch(() => setReport(demoReport));
  }, []);

  const highlighted = new Set(report.diagnosis.findings.flatMap((finding) => finding.event_ids));

  return (
    <main>
      <header className="topbar">
        <div>
          <p className="eyebrow">Codex Agent Harness Debugger</p>
          <h1>CodexTrace</h1>
        </div>
        <div className={`status ${report.diagnosis.outcome}`}>
          {report.diagnosis.outcome === "healthy" ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
          {report.diagnosis.outcome}
        </div>
      </header>

      <section className="summary">
        <div>
          <span>Failure score</span>
          <strong>{report.diagnosis.failure_score}/100</strong>
        </div>
        <div>
          <span>Commands</span>
          <strong>{report.diagnosis.metrics.command_events}</strong>
        </div>
        <div>
          <span>Failed commands</span>
          <strong>{report.diagnosis.metrics.failed_commands}</strong>
        </div>
        <div>
          <span>Input tokens</span>
          <strong>{report.diagnosis.metrics.input_tokens.toLocaleString()}</strong>
        </div>
      </section>

      <section className="layout">
        <aside className="findings">
          <h2>Findings</h2>
          {report.diagnosis.findings.map((finding) => (
            <article className={`finding ${finding.severity}`} key={finding.code}>
              <div className="finding-title">
                <AlertTriangle size={16} />
                <h3>{finding.title}</h3>
              </div>
              <p>{finding.recommendation}</p>
              <code>{finding.code}</code>
            </article>
          ))}
        </aside>

        <section className="timeline">
          <div className="section-heading">
            <h2>Trace Timeline</h2>
            <p>{report.diagnosis.summary}</p>
          </div>
          {report.trace.events.map((event) => (
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
    </main>
  );
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
