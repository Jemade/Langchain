import "./style.css";
type Run = {
  id: string;
  request: { shipment_id: string; category: string; details: string };
  status: string;
  draft?: string;
  evidence?: { source: string; text: string; score: number }[];
  trace?: unknown[];
  mode?: string;
};
let token = "";
const root = document.querySelector<HTMLDivElement>("#app")!;
root.innerHTML = `<header><a class="brand" href="/">FreightDesk<span>Dispatch operations</span></a><p>Exception review workspace</p><span class="mode">Sample policies · local workspace</span></header>
<main><div class="heading"><div><p class="eyebrow">OPERATIONS / EXCEPTIONS</p><h1>Keep the next step clear.</h1><p>Review shipment reports against policy before making a commitment.</p></div></div>
<section id="login"><label>Reviewer token <input id="token" type="password" autocomplete="off" placeholder="Paste your local token"></label><button id="connect">Open workspace</button><p>Token stays in memory and clears when you reload.</p></section>
<p id="notice" role="status" aria-live="polite"></p>
<div id="workspace" hidden><div class="columns"><section class="inbox"><h2>New exception</h2><form id="create"><label>Request reference<input name="reference" required maxlength="80" pattern="[A-Za-z0-9_-]+" placeholder="EXC-001"></label><label>Shipment reference<input name="shipment_id" required maxlength="80" placeholder="HRE-1042"></label><label>Exception type<select name="category"><option value="delay">Delivery delay</option><option value="damage">Damaged cargo</option><option value="documents">Missing documents</option></select></label><label>Verified report<textarea name="details" required minlength="10" maxlength="4000" rows="5" placeholder="What happened? What has the carrier confirmed?"></textarea></label><button>Prepare for review</button></form><div class="listheading"><h2>Recent requests</h2><button class="secondary" id="refresh">Refresh</button></div><div id="requests"></div></section>
<section class="review"><div class="reviewheading"><h2>Dispatcher review</h2><span id="status">Select a request</span></div><div id="detail"><p class="empty">Choose a request to inspect its draft, policy evidence and workflow trace.</p></div></section></div></div></main><footer>Training MVP. No email, carrier action, refund or cargo release is executed.</footer>`;
const el = <T extends HTMLElement>(id: string) =>
  document.getElementById(id) as T;
function notice(message: string) {
  el("notice").textContent = message;
}
async function api(path: string, body?: unknown): Promise<any> {
  const response = await fetch("/api" + path, {
    method: body ? "POST" : "GET",
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": "application/json",
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const result = await response.json();
  if (!response.ok)
    throw Error(
      typeof result.detail === "string"
        ? result.detail
        : "Please check the form values.",
    );
  return result;
}
function paragraph(parent: HTMLElement, text: string, className = "") {
  const p = document.createElement("p");
  p.textContent = text;
  p.className = className;
  parent.append(p);
}
async function refresh() {
  const runs: Run[] = await api("/requests");
  el("requests").replaceChildren();
  if (!runs.length)
    paragraph(
      el("requests"),
      "No requests yet. Add the first exception.",
      "empty",
    );
  for (const run of runs) {
    const button = document.createElement("button");
    button.className = "request";
    button.textContent =
      run.request.shipment_id +
      " / " +
      run.request.category +
      " / " +
      run.status.replaceAll("_", " ");
    button.onclick = () => show(run);
    el("requests").append(button);
  }
}
function show(run: Run) {
  el("status").textContent = run.status.replaceAll("_", " ");
  const detail = el("detail");
  detail.replaceChildren();
  paragraph(detail, run.request.shipment_id, "shipment");
  paragraph(detail, run.request.details);
  paragraph(
    detail,
    run.mode === "bedrock"
      ? "Model draft: verify every factual claim."
      : "Demo mode: deterministic policy-based draft.",
    "note",
  );
  const pre = document.createElement("pre");
  pre.textContent =
    run.draft || "Workflow pending. Retry the same request reference.";
  detail.append(pre);
  for (const e of run.evidence || []) {
    const d = document.createElement("details");
    const s = document.createElement("summary");
    s.textContent = e.source + " · BM25 score " + e.score;
    d.append(s);
    paragraph(d, e.text);
    detail.append(d);
  }
  const trace = document.createElement("details");
  const label = document.createElement("summary");
  label.textContent = "Workflow trace";
  trace.append(label);
  const log = document.createElement("pre");
  log.textContent = JSON.stringify(run.trace, null, 2);
  trace.append(log);
  detail.append(trace);
  if (run.status === "awaiting_review") {
    const input = document.createElement("textarea");
    input.placeholder = "Review notes (required)";
    input.setAttribute("aria-label", "Review notes");
    input.maxLength = 1000;
    detail.append(input);
    for (const approve of [true, false]) {
      const button = document.createElement("button");
      button.textContent = approve ? "Approve draft" : "Reject draft";
      button.className = approve ? "" : "secondary";
      button.onclick = async () => {
        button.disabled = true;
        try {
          show(
            await api("/requests/" + run.id + "/review", {
              approve,
              comment: input.value,
            }),
          );
          await refresh();
          notice("Review saved. No external action was taken.");
        } catch (e) {
          notice((e as Error).message);
        } finally {
          button.disabled = false;
        }
      };
      detail.append(button);
    }
  }
  if (run.status === "approved") {
    const button = document.createElement("button");
    button.textContent = "Download reviewed draft";
    button.onclick = async () => {
      try {
        const output = await api("/requests/" + run.id + "/export");
        const url = URL.createObjectURL(
          new Blob([JSON.stringify(output, null, 2)], {
            type: "application/json",
          }),
        );
        const a = document.createElement("a");
        a.href = url;
        a.download = "freightdesk-" + run.id + ".json";
        a.click();
        URL.revokeObjectURL(url);
      } catch (e) {
        notice((e as Error).message);
      }
    };
    detail.append(button);
  }
}
el("connect").onclick = async () => {
  token = el<HTMLInputElement>("token").value;
  try {
    await refresh();
    el("login").hidden = true;
    el("workspace").hidden = false;
    el<HTMLInputElement>("token").value = "";
    notice("Workspace opened.");
  } catch (e) {
    token = "";
    notice((e as Error).message);
  }
};
el("refresh").onclick = () => refresh().catch((e) => notice(e.message));
el<HTMLFormElement>("create").onsubmit = async (event) => {
  event.preventDefault();
  const form = el<HTMLFormElement>("create");
  const button = form.querySelector("button")!;
  button.disabled = true;
  try {
    show(await api("/requests", Object.fromEntries(new FormData(form))));
    await refresh();
    notice("Request prepared. Inspect the evidence before approving.");
  } catch (e) {
    notice((e as Error).message);
  } finally {
    button.disabled = false;
  }
};
