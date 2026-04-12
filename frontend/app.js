const taskSelect = document.getElementById("taskSelect");
const actionSelect = document.getElementById("actionSelect");
const resetBtn = document.getElementById("resetBtn");
const policyStepBtn = document.getElementById("policyStepBtn");
const manualStepBtn = document.getElementById("manualStepBtn");
const refreshExplainBtn = document.getElementById("refreshExplainBtn");

const plainExplain = document.getElementById("plainExplain");
const statusBadge = document.getElementById("statusBadge");
const logOutput = document.getElementById("logOutput");

const errorRateVal = document.getElementById("errorRateVal");
const latencyVal = document.getElementById("latencyVal");
const riskVal = document.getElementById("riskVal");
const runbookVal = document.getElementById("runbookVal");
const budgetVal = document.getElementById("budgetVal");
const stepsVal = document.getElementById("stepsVal");

const errorRateBar = document.getElementById("errorRateBar");
const latencyBar = document.getElementById("latencyBar");
const riskBar = document.getElementById("riskBar");

const scoreVal = document.getElementById("scoreVal");
const successVal = document.getElementById("successVal");

let doneState = false;

function addLog(line) {
  const timestamp = new Date().toLocaleTimeString();
  logOutput.textContent = `[${timestamp}] ${line}\n${logOutput.textContent}`;
}

function clampPercent(v) {
  return Math.max(0, Math.min(100, v));
}

function updateBars(state) {
  errorRateBar.style.width = `${clampPercent((state.error_rate || 0) * 100)}%`;
  const latencyPercent = clampPercent(((state.latency_p95_ms || 0) / 900) * 100);
  latencyBar.style.width = `${latencyPercent}%`;
  riskBar.style.width = `${clampPercent((state.sla_breach_risk || 0) * 100)}%`;
}

function updateStateUi(state) {
  if (!state) {
    return;
  }

  errorRateVal.textContent = `${((state.error_rate || 0) * 100).toFixed(1)}%`;
  latencyVal.textContent = `${(state.latency_p95_ms || 0).toFixed(1)} ms`;
  riskVal.textContent = `${((state.sla_breach_risk || 0) * 100).toFixed(1)}%`;
  runbookVal.textContent = String(state.runbook_phase ?? "-");
  budgetVal.textContent = String(state.escalation_budget ?? "-");
  stepsVal.textContent = String(state.elapsed_steps ?? "-");
  updateBars(state);
}

function updateResultUi(score, success) {
  scoreVal.textContent = typeof score === "number" ? score.toFixed(3) : "-";
  if (success === true) {
    successVal.textContent = "Yes";
    statusBadge.textContent = "Episode Success";
    statusBadge.className = "badge good";
  } else if (success === false) {
    successVal.textContent = "No";
    statusBadge.textContent = doneState ? "Episode Finished" : "Simulation Active";
    statusBadge.className = doneState ? "badge bad" : "badge neutral";
  } else {
    successVal.textContent = "-";
  }
}

async function fetchJson(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Request failed (${res.status}): ${txt}`);
  }
  return res.json();
}

async function loadTasks() {
  const payload = await fetchJson("/tasks");
  const actions = [
    "prioritize_incident",
    "query_diagnostics",
    "apply_runbook_step",
    "rollback_release",
    "escalate_oncall",
    "mark_resolved",
  ];

  actionSelect.innerHTML = "";
  actions.forEach((action) => {
    const option = document.createElement("option");
    option.value = action;
    option.textContent = action;
    actionSelect.appendChild(option);
  });

  if (payload.tasks && payload.tasks[taskSelect.value]?.title) {
    addLog(`Loaded tasks. Current scenario: ${payload.tasks[taskSelect.value].title}`);
  }
}

async function loadExplain() {
  try {
    const payload = await fetchJson("/explain");
    const plain = payload.project_plain;
    plainExplain.textContent = `${plain.what_it_does} Why this matters: ${plain.why_it_matters}`;
  } catch (err) {
    plainExplain.textContent = "Could not load explanation right now.";
    addLog(`Explain error: ${err.message}`);
  }
}

async function resetScenario() {
  const taskId = taskSelect.value;
  const payload = await fetchJson("/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id: taskId }),
  });

  doneState = false;
  statusBadge.textContent = "Simulation Active";
  statusBadge.className = "badge neutral";

  updateStateUi(payload.state);
  updateResultUi(null, null);
  addLog(`Scenario reset: ${taskId}`);
}

async function runStepWithPolicy() {
  if (doneState) {
    addLog("Episode already finished. Reset scenario for a fresh run.");
    return;
  }

  const payload = await fetchJson("/step", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ use_policy: true, deterministic: true }),
  });

  doneState = Boolean(payload.done);
  updateStateUi(payload.state);

  const score = payload.info ? payload.info.score : null;
  const success = payload.info ? payload.info.success : null;
  updateResultUi(score, success);

  addLog(`AI action=${payload.action} reward=${Number(payload.reward || 0).toFixed(3)} done=${payload.done}`);
}

async function runManualStep() {
  if (doneState) {
    addLog("Episode already finished. Reset scenario for a fresh run.");
    return;
  }

  const action = actionSelect.value;
  const payload = await fetchJson("/step", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, use_policy: false, deterministic: true }),
  });

  doneState = Boolean(payload.done);
  updateStateUi(payload.state);

  const score = payload.info ? payload.info.score : null;
  const success = payload.info ? payload.info.success : null;
  updateResultUi(score, success);

  addLog(`Manual action=${action} reward=${Number(payload.reward || 0).toFixed(3)} done=${payload.done}`);
}

async function boot() {
  try {
    await loadTasks();
    await loadExplain();
    await resetScenario();
  } catch (err) {
    addLog(`Boot error: ${err.message}`);
  }
}

resetBtn.addEventListener("click", () => {
  resetScenario().catch((err) => addLog(`Reset error: ${err.message}`));
});

policyStepBtn.addEventListener("click", () => {
  runStepWithPolicy().catch((err) => addLog(`Policy step error: ${err.message}`));
});

manualStepBtn.addEventListener("click", () => {
  runManualStep().catch((err) => addLog(`Manual step error: ${err.message}`));
});

refreshExplainBtn.addEventListener("click", () => {
  loadExplain().then(() => addLog("Plain-language explanation refreshed.")).catch((err) => addLog(`Explain refresh error: ${err.message}`));
});

taskSelect.addEventListener("change", () => {
  resetScenario().catch((err) => addLog(`Task switch error: ${err.message}`));
});

boot();
