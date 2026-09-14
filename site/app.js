const SECRET_RE =
  /\b(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|postgresql:\/\/[^\s"']+|Bearer\s+[A-Za-z0-9._\-]+)/gi;

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
let activeSystem = "all";
let scenarios = [];
let activeScenario = null;

function renderFilters() {
  const host = document.getElementById("system-filters");
  const systems = ["all", ...new Set(tools.map((t) => t.system))];
  host.replaceChildren(
    ...systems.map((sys) =>
      el(
        "button",
        {
          type: "button",
          className: `filter-btn${activeSystem === sys ? " active" : ""}`,
          role: "tab",
          "aria-selected": String(activeSystem === sys),
          onClick: () => {
            activeSystem = sys;
            renderFilters();
            renderTools();
          },
        },
        [sys]
      )
    )
  );
}

function renderTools() {
  const host = document.getElementById("tool-list");
  const filtered = tools.filter((t) => activeSystem === "all" || t.system === activeSystem);
  host.replaceChildren(
    ...filtered.map((tool) => {
      const inputs = el(
        "ul",
        { className: "kv" },
        tool.inputs.map((inp) => {
          const bits = [inp.type];
          if (inp.required) bits.push("required");
          if (inp.default !== undefined) bits.push(`default=${JSON.stringify(inp.default)}`);
          const detail = `${bits.join(" · ")}${inp.description ? ` — ${inp.description}` : ""}`;
          return el("li", {}, [
            el("code", { text: inp.name }),
            el("span", { text: detail }),
          ]);
        })
      );
      const safety = el(
        "ul",
        { className: "chips" },
        (tool.safety || []).map((s) => el("li", { text: s }))
      );
      const body = el("div", { className: "tool-body" }, [
        el("h4", { text: "Inputs" }),
        inputs,
        el("h4", { text: "Output" }),
        el("p", { className: "muted", text: tool.outputs }),
        el("h4", { text: "Safety" }),
        safety,
      ]);
      return el("details", { className: "tool" }, [
        el("summary", {}, [
          el("span", { className: "tool-name", text: tool.name }),
          el("span", { className: "tool-system", text: tool.system }),
          el("span", { className: "tool-summary", text: tool.summary }),
        ]),
        body,
      ]);
    })
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

function renderEvents(payload) {
  document.getElementById("events-caption").textContent = payload.caption;
  const tbody = document.querySelector("#events-table tbody");
  tbody.replaceChildren(
    ...payload.events.map((ev) =>
      el("tr", {}, [
        el("td", { text: ev.ts }),
        el("td", { text: ev.tool }),
        el("td", {
          className: ev.ok ? "ok-true" : "ok-false",
          text: String(ev.ok),
        }),
        el("td", { text: `${ev.latency_ms} ms` }),
        el("td", { text: ev.error || "—" }),
      ])
    )
  );
}

async function init() {
  const [toolsPayload, setupText, playground, events] = await Promise.all([
    loadJson("tools.json"),
    fetch(`${BASE}data/setup.mcp.json.example`).then((r) => r.text()),
    loadJson("playground.json"),
    loadJson("sample-events.json"),
  ]);

  tools = toolsPayload.tools;
  scenarios = playground.scenarios;
  renderFilters();
  renderTools();
  renderScenarios();
  renderEvents(events);

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
}

init().catch((err) => {
  console.error(err);
  document.getElementById("tool-list").textContent = `Failed to load site data: ${err.message}`;
});
