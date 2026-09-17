const SECRET_RE =
  /\b(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|postgresql:\/\/[^\s"']+|Bearer\s+[A-Za-z0-9._\-]+)/gi;

const SYSTEM_ORDER = ["github", "postgres", "deploy", "filesystem"];
const SYSTEM_LABELS = {
  github: "GitHub",
  postgres: "Postgres",
  deploy: "Deploy",
  filesystem: "Filesystem",
};

function siteBase() {
  const parts = location.pathname.split("/").filter(Boolean);
  if (parts[0] === "ops-mcp") return "/ops-mcp/";
  return "./";
}

const BASE = siteBase();

async function loadJson(name) {
  const res = await fetch(`${BASE}data/${name}`);
  if (!res.ok) throw new Error(`Failed to load ${name}: ${res.status}`);
  return res.json();
}

function redact(text) {
  return String(text).replace(SECRET_RE, "[REDACTED]");
}

function pretty(value) {
  return redact(JSON.stringify(value, null, 2));
}

function el(tag, props = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "className") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on") && typeof v === "function") {
      node.addEventListener(k.slice(2).toLowerCase(), v);
    } else if (v !== undefined && v !== null) {
      node.setAttribute(k, v);
    }
  }
  for (const child of children) {
    if (child == null) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
}

let tools = [];
let scenarios = [];
let activeScenario = null;
let safetyDemos = [];
let activeSafety = null;
let safetyRevealed = false;

function renderCatalog() {
  const host = document.getElementById("catalog-groups");
  host.replaceChildren(
    ...SYSTEM_ORDER.map((system) => {
      const groupTools = tools.filter((t) => t.system === system);
      if (!groupTools.length) return null;
      const grid = el(
        "div",
        { className: "tool-grid" },
        groupTools.map((tool) =>
          el("article", { className: "tool-card" }, [
            el("p", { className: "name", text: tool.name }),
            el("p", { className: "can", text: tool.can || tool.summary }),
            el("p", { className: "cannot", text: tool.cannot || "See safety notes in source." }),
          ])
        )
      );
      return el("div", { className: "catalog-group" }, [
        el("h3", { className: "group-title", text: SYSTEM_LABELS[system] || system }),
        grid,
      ]);
    }).filter(Boolean)
  );
}

function selectScenario(scenario) {
  activeScenario = scenario;
  document.querySelectorAll(".scenario-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.id === scenario.id);
  });
  document.getElementById("scenario-title").textContent = scenario.title;
  document.getElementById("scenario-blurb").textContent = scenario.blurb;
  document.getElementById("scenario-inputs").textContent = pretty(scenario.inputs);
  document.getElementById("run-scenario").disabled = false;
  document.getElementById("sim-banner").classList.add("hidden");
  document.getElementById("scenario-result").classList.add("hidden");
}

function renderScenarios() {
  const host = document.getElementById("scenario-list");
  host.replaceChildren(
    ...scenarios.map((s) =>
      el(
        "button",
        {
          type: "button",
          className: "scenario-btn",
          role: "option",
          "data-id": s.id,
          onClick: () => selectScenario(s),
        },
        [s.title, el("small", { text: s.tool })]
      )
    )
  );
  if (scenarios[0]) selectScenario(scenarios[0]);
}

function runScenario() {
  if (!activeScenario) return;
  const raw = pretty(activeScenario.inputs);
  if (raw.includes("[REDACTED]") || /ghp_|github_pat_|postgresql:\/\//i.test(raw)) {
    const banner = document.getElementById("sim-banner");
    banner.textContent =
      "Blocked: secret-shaped input must stay in local .env — not on this site.";
    banner.classList.remove("hidden");
    document.getElementById("scenario-result").classList.add("hidden");
    return;
  }
  const banner = document.getElementById("sim-banner");
  banner.textContent = "Simulated result — not a live MCP call";
  banner.classList.remove("hidden");
  const out = document.getElementById("scenario-result");
  out.textContent = pretty(activeScenario.result);
  out.classList.remove("hidden");
}

function paintSafety(demo, revealed) {
  document.getElementById("safety-title").textContent = demo.title;
  document.getElementById("safety-blurb").textContent = demo.blurb;
  document.getElementById("safety-gate").textContent = demo.gate;
  document.getElementById("safety-request").textContent = pretty(demo.request);
  document.getElementById("safety-note").textContent = demo.note || "";

  const tag = document.getElementById("safety-outcome-tag");
  const response = document.getElementById("safety-response");
  const panel = document.getElementById("safety-response-panel");
  panel.classList.remove("flash-block", "flash-dry");

  if (!revealed) {
    tag.className = "tag neutral";
    tag.textContent = "pending";
    response.textContent = "// Run gate demo to see the server response";
    return;
  }

  response.textContent = pretty(demo.response);
  if (demo.outcome === "blocked") {
    tag.className = "tag blocked";
    tag.textContent = "blocked";
    panel.classList.add("flash-block");
  } else if (demo.outcome === "dry_run") {
    tag.className = "tag dry_run";
    tag.textContent = "dry_run";
    panel.classList.add("flash-dry");
  } else {
    tag.className = "tag neutral";
    tag.textContent = demo.outcome;
  }
}

function selectSafety(demo) {
  activeSafety = demo;
  safetyRevealed = false;
  document.querySelectorAll(".safety-tab").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.id === demo.id);
  });
  document.getElementById("safety-run").disabled = false;
  paintSafety(demo, false);
}

function renderSafetyTabs() {
  const host = document.getElementById("safety-tabs");
  host.replaceChildren(
    ...safetyDemos.map((demo) =>
      el(
        "button",
        {
          type: "button",
          className: "safety-tab",
          role: "tab",
          "data-id": demo.id,
          onClick: () => selectSafety(demo),
        },
        [demo.tool]
      )
    )
  );
  if (safetyDemos[0]) selectSafety(safetyDemos[0]);
}

function runSafety() {
  if (!activeSafety) return;
  safetyRevealed = true;
  paintSafety(activeSafety, true);
}

async function init() {
  const [toolsPayload, setupText, playground, safetyPayload] = await Promise.all([
    loadJson("tools.json"),
    fetch(`${BASE}data/setup.mcp.json.example`).then((r) => r.text()),
    loadJson("playground.json"),
    loadJson("safety-demos.json"),
  ]);

  tools = toolsPayload.tools;
  scenarios = playground.scenarios;
  safetyDemos = safetyPayload.demos;

  renderCatalog();
  renderScenarios();
  renderSafetyTabs();

  const setupCode = document.getElementById("setup-code");
  setupCode.textContent = setupText.trim();
  document.getElementById("copy-setup").addEventListener("click", async () => {
    await navigator.clipboard.writeText(setupCode.textContent);
    const btn = document.getElementById("copy-setup");
    const prev = btn.textContent;
    btn.textContent = "Copied";
    setTimeout(() => {
      btn.textContent = prev;
    }, 1200);
  });
  document.getElementById("run-scenario").addEventListener("click", runScenario);
  document.getElementById("safety-run").addEventListener("click", runSafety);
}

init().catch((err) => {
  console.error(err);
  const host = document.getElementById("catalog-groups");
  if (host) host.textContent = `Failed to load site data: ${err.message}`;
});
