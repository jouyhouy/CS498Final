import "./style.css";
import { explorerService } from "./services/explorerService.js";

const PREDEFINED_QUERIES = [
  {
    id: "top-country",
    label: "Top Tweet Country",
    description: "Find the country with the highest number of tweets.",
    params: []
  },
  {
    id: "most-active-user",
    label: "Most Active User",
    description: "Find the user who posted the most tweets.",
    params: []
  },
  {
    id: "top-hashtags",
    label: "Top Hashtags",
    description: "Find the most frequent hashtags (deduplicated per tweet).",
    params: [
      {
        name: "limit",
        label: "Limit",
        defaultValue: "10",
        placeholder: "10"
      }
    ]
  }
];

const state = {
  view: "collections",
  loading: false,
  error: "",
  collections: [],
  expandedCollection: null,
  selectedQueryId: PREDEFINED_QUERIES[0].id,
  queryParams: {
    limit: "10"
  },
  queryResult: null,
  queryRunning: false
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function selectedQuery() {
  return PREDEFINED_QUERIES.find((q) => q.id === state.selectedQueryId) ?? PREDEFINED_QUERIES[0];
}

function summaryCardsHtml() {
  const totalDocs = state.collections.reduce((sum, col) => sum + Number(col.count ?? 0), 0);
  return `
    <div class="summary-grid">
      <article class="summary-card">
        <div class="icon blue">🗂️</div>
        <div>
          <p class="summary-label">Collections</p>
          <p class="summary-value">${state.collections.length}</p>
        </div>
      </article>
      <article class="summary-card">
        <div class="icon green">📄</div>
        <div>
          <p class="summary-label">Total Documents</p>
          <p class="summary-value">${totalDocs.toLocaleString()}</p>
        </div>
      </article>
    </div>
  `;
}

function collectionListHtml() {
  if (!state.collections.length) {
    return `<div class="empty-block">No collections found.</div>`;
  }

  return `
    <ul class="collection-list">
      ${state.collections
        .map((collection) => {
          const expanded = state.expandedCollection === collection.name;
          const sampleDoc = collection.sampleDoc ? JSON.stringify(collection.sampleDoc, null, 2) : "No sample document";

          return `
          <li>
            <button class="collection-row" data-action="toggle-collection" data-name="${collection.name}">
              <span class="left">
                <span class="db-dot">●</span>
                <span class="collection-name">${collection.name}</span>
                <span class="pill">${Number(collection.count ?? 0).toLocaleString()} docs</span>
              </span>
              <span class="expand-icon">${expanded ? "▾" : "▸"}</span>
            </button>
            ${
              expanded
                ? `<div class="collection-detail">
                  <p class="mini-title">Sample document</p>
                  <pre>${escapeHtml(sampleDoc)}</pre>
                </div>`
                : ""
            }
          </li>
        `;
        })
        .join("")}
    </ul>
  `;
}

function collectionsViewHtml() {
  return `
    <section class="card-section">
      ${summaryCardsHtml()}
      <div class="card">
        <div class="card-header">
          <h2>Collections</h2>
          <span class="caption">MongoDB Explorer-style overview</span>
        </div>
        ${collectionListHtml()}
      </div>
    </section>
  `;
}

function queryListHtml() {
  return `
    <div class="query-list card">
      <div class="card-header small">
        <h3>Queries</h3>
      </div>
      ${PREDEFINED_QUERIES.map(
        (query) => `
        <button
          class="query-option ${query.id === state.selectedQueryId ? "active" : ""}"
          data-action="select-query"
          data-query-id="${query.id}"
        >
          <span class="q-title">${query.label}</span>
          <span class="q-desc">${query.description}</span>
        </button>
      `
      ).join("")}
    </div>
  `;
}

function queryParamsHtml(query) {
  if (!query.params?.length) {
    return "";
  }

  return `
    <div class="query-params">
      ${query.params
        .map(
          (param) => `
          <label>
            <span>${param.label}</span>
            <input
              type="text"
              value="${escapeHtml(state.queryParams[param.name] ?? param.defaultValue ?? "")}"
              data-action="param-input"
              data-param-name="${param.name}"
              placeholder="${escapeHtml(param.placeholder ?? "")}" 
            />
          </label>
        `
        )
        .join("")}
    </div>
  `;
}

function renderRowsTable(rows) {
  if (!rows.length) {
    return `<div class="empty-block">No result rows returned.</div>`;
  }

  const columns = [...new Set(rows.flatMap((row) => Object.keys(row)))];
  return `
    <div class="result-table-wrap">
      <table class="result-table">
        <thead>
          <tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row) => `
              <tr>
                ${columns
                  .map((column) => {
                    const value = row[column] ?? "";
                    const printed = typeof value === "object" ? JSON.stringify(value) : String(value);
                    return `<td>${escapeHtml(printed)}</td>`;
                  })
                  .join("")}
              </tr>
            `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function queryResultHtml() {
  if (state.queryRunning) {
    return `<div class="card"><div class="status">Running query...</div></div>`;
  }

  if (!state.queryResult) {
    return `<div class="card"><div class="empty-block">Run a query to see results.</div></div>`;
  }

  return `
    <div class="card">
      <div class="card-header">
        <h3>Results — ${state.queryResult.count} row${state.queryResult.count === 1 ? "" : "s"}</h3>
        <span class="caption">${state.queryResult.executionMs} ms${
    state.queryResult.source ? ` · ${state.queryResult.source}` : ""
  }</span>
      </div>
      ${renderRowsTable(state.queryResult.rows)}
    </div>
  `;
}

function queriesViewHtml() {
  const query = selectedQuery();
  return `
    <section class="queries-grid">
      ${queryListHtml()}

      <div class="query-main">
        <div class="card">
          <div class="card-header">
            <h2>${query.label}</h2>
            <span class="caption">${query.description}</span>
          </div>
          ${queryParamsHtml(query)}
          <button class="primary" data-action="run-query" ${state.queryRunning ? "disabled" : ""}>Run Query</button>
        </div>

        ${queryResultHtml()}
      </div>
    </section>
  `;
}

function appShell(content) {
  return `
    <div class="app-shell">
      <header class="topbar">
        <div class="brand">
          <span class="brand-icon">🧭</span>
          <span>MongoDB Explorer</span>
        </div>
        <nav class="nav">
          <button class="nav-item ${state.view === "collections" ? "active" : ""}" data-action="switch-view" data-view="collections">Collections</button>
          <button class="nav-item ${state.view === "queries" ? "active" : ""}" data-action="switch-view" data-view="queries">Queries</button>
        </nav>
      </header>

      <main class="page-wrap">
        <div class="page-header">
          <h1>${state.view === "collections" ? "MongoDB Dashboard" : "Predefined Queries"}</h1>
          <p>${
            state.view === "collections"
              ? "Live overview of your database collections"
              : "Run curated queries backed by your Python aggregation pipelines"
          }</p>
        </div>

        ${state.error ? `<div class="error-box">${escapeHtml(state.error)}</div>` : ""}
        ${content}
      </main>
    </div>
  `;
}

function bindEvents() {
  document.querySelectorAll("[data-action='switch-view']").forEach((button) => {
    button.addEventListener("click", () => {
      state.view = button.dataset.view;
      state.error = "";
      paint();
    });
  });

  document.querySelectorAll("[data-action='toggle-collection']").forEach((button) => {
    button.addEventListener("click", () => {
      const name = button.dataset.name;
      state.expandedCollection = state.expandedCollection === name ? null : name;
      paint();
    });
  });

  document.querySelectorAll("[data-action='select-query']").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedQueryId = button.dataset.queryId;
      const query = selectedQuery();
      state.queryParams = {};
      query.params?.forEach((param) => {
        state.queryParams[param.name] = param.defaultValue ?? "";
      });
      state.queryResult = null;
      paint();
    });
  });

  document.querySelectorAll("[data-action='param-input']").forEach((input) => {
    input.addEventListener("input", () => {
      const name = input.dataset.paramName;
      state.queryParams[name] = input.value;
    });
  });

  document.querySelector("[data-action='run-query']")?.addEventListener("click", async () => {
    state.queryRunning = true;
    state.error = "";
    state.queryResult = null;
    paint();

    try {
      state.queryResult = await explorerService.runPredefinedQuery({
        queryId: state.selectedQueryId,
        params: state.queryParams
      });
    } catch (error) {
      state.error = error instanceof Error ? error.message : "Query failed.";
    } finally {
      state.queryRunning = false;
      paint();
    }
  });
}

async function paint() {
  const app = document.querySelector("#app");
  if (!app) {
    return;
  }

  if (state.loading) {
    app.innerHTML = appShell("<div class='card'><div class='status'>Loading data...</div></div>");
    return;
  }

  const content = state.view === "collections" ? collectionsViewHtml() : queriesViewHtml();
  app.innerHTML = appShell(content);
  bindEvents();
}

async function init() {
  state.loading = true;
  await paint();

  try {
    state.collections = await explorerService.listCollections();
    if (state.collections.length) {
      state.expandedCollection = state.collections[0].name;
    }
  } catch (error) {
    state.error = error instanceof Error ? error.message : "Failed to load collections.";
  } finally {
    state.loading = false;
    await paint();
  }
}

init();