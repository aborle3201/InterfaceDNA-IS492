/* InterfaceDNA Checkpoint 2 prototype
   Scripted with synthetic Demo University data. No real records are accessed and no action is sent. */

"use strict";

const RUN = window.RUN;
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
const esc = (value) => String(value).replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

const JOURNEYS = {
  drop: {
    label: "Course drop",
    persona: "alex",
    stages: ["Goal", "Verify", "Review", "Confirm", "Done"],
    goal: "Can I drop CS 411?",
    headline: "Decide whether to drop a course without hunting across university systems.",
    description: "InterfaceDNA combines the student record, course information, and approved policy before showing consequences and asking the student to decide."
  },
  grad: {
    label: "Graduation readiness",
    persona: "maya",
    stages: ["Goal", "Verify", "Review", "Plan", "Done"],
    goal: "What do I still need to graduate?",
    headline: "Turn a degree audit into a focused graduation-readiness view.",
    description: "InterfaceDNA retrieves the student’s academic context, maps it to the governing catalog, and surfaces remaining requirements with provenance."
  },
  hold: {
    label: "Registration hold",
    persona: "jordan",
    stages: ["Goal", "Verify", "Resolve", "Confirm", "Done"],
    goal: "Why can’t I register, and what should I do next?",
    headline: "Resolve registration blockers with the right office and the right next step.",
    description: "InterfaceDNA identifies the hold, explains who owns it, and coordinates only the actions the student can safely take."
  }
};

const PERSONA_GUIDE = {
  alex: {
    title: "Alex · enrollment-sensitive student",
    model: "“Show me the consequence of this decision using my actual record, but let me decide.”",
    tasks: [
      ["goal", "Ask a course-drop question"],
      ["verify", "See verified student context and policy provenance"],
      ["why", "Interrogate at least one consequence"],
      ["confirm", "Keep final decision rights at the confirmation gate"]
    ],
    success: "A clear answer without guessing, hidden policy provenance, or silent action."
  },
  maya: {
    title: "Maya · graduating senior",
    model: "“Tell me exactly what remains and where that conclusion came from.”",
    tasks: [
      ["goal", "Ask what remains for graduation"],
      ["verify", "Verify the degree audit and catalog year"],
      ["why", "Inspect why a requirement is marked satisfied or remaining"],
      ["confirm", "Approve a plan instead of letting AI choose coursework"]
    ],
    success: "A concise graduation plan with visible evidence and escalation when records are incomplete."
  },
  jordan: {
    title: "Jordan · student with registration holds",
    model: "“Tell me which office owns each blocker and what I can do now.”",
    tasks: [
      ["goal", "Ask why registration is blocked"],
      ["verify", "Identify the actual holds from the student record"],
      ["why", "Inspect why each office is responsible"],
      ["confirm", "Confirm only the request the student is allowed to initiate"]
    ],
    success: "Less portal-hopping, no invented clearance, and the right escalation path."
  }
};

const freshState = () => ({
  journey: "drop",
  persona: "alex",
  stage: 0,
  failure: "",
  why: new Set(),
  completed: new Set(),
  confirmChecked: false,
  planChecked: false,
  holdChecked: false,
  previousStage: 0
});

let S = freshState();

function student() { return RUN.students[S.persona]; }
function journey() { return JOURNEYS[S.journey]; }
function policy(key) { return RUN.policies[key]; }

function mark(key) { S.completed.add(key); }
function toast(message) {
  const el = $("#toast");
  el.textContent = message;
  el.hidden = false;
  window.clearTimeout(toast._timer);
  toast._timer = window.setTimeout(() => { el.hidden = true; }, 2600);
}

function setJourney(key, keepPersona = false) {
  S.journey = key;
  if (!keepPersona) S.persona = JOURNEYS[key].persona;
  S.stage = 0;
  S.failure = "";
  S.why.clear();
  S.completed.clear();
  S.confirmChecked = false;
  S.planChecked = false;
  S.holdChecked = false;
  $("#persona").value = S.persona;
  $("#failure").value = "";
  render();
}

function go(stage) {
  S.previousStage = S.stage;
  S.stage = Math.max(0, Math.min(stage, journey().stages.length - 1));
  if (S.stage >= 1) mark("goal");
  if (S.stage >= 2) mark("verify");
  render();
  $("#content")?.focus({preventScroll:true});
  window.scrollTo({top: 0, behavior: "smooth"});
}

function badge(text, type = "neutral") {
  return `<span class="badge ${type}">${esc(text)}</span>`;
}

function sourceCard(title, source, version, label, verified = true) {
  return `<div class="source-card">
    <div><strong>${esc(title)}</strong><span>${esc(source)} · Version ${esc(version)}<br>${esc(label)}</span></div>
    ${badge(verified ? "Approved source" : "Unverified", verified ? "success" : "danger")}
  </div>`;
}

function whyButton(key, label = "Why?") {
  return `<button type="button" class="btn btn-link" data-why="${esc(key)}" aria-expanded="${S.why.has(key)}">${esc(label)}</button>`;
}

function whyPanel(key, html) {
  return S.why.has(key) ? `<div class="why-panel">${html}</div>` : "";
}

function action(label, actionName, kind = "primary", disabled = false, extra = "") {
  return `<button type="button" class="btn btn-${kind}" data-action="${esc(actionName)}" ${disabled ? "disabled" : ""} ${extra}>${esc(label)}</button>`;
}

function renderStages() {
  const stages = journey().stages;
  $("#stages").innerHTML = stages.map((label, i) => `<li class="${i < S.stage ? "done" : ""}" ${i === S.stage ? 'aria-current="step"' : ""}>${esc(label)}</li>`).join("");
  $$('[data-journey]').forEach((b) => b.classList.toggle("active", b.dataset.journey === S.journey));
}

function renderRail() {
  const p = PERSONA_GUIDE[S.persona];
  const tasks = p.tasks.map(([key, text]) => `<li class="${S.completed.has(key) ? "done" : ""}"><span class="task-dot">${S.completed.has(key) ? "✓" : ""}</span><span>${esc(text)}</span></li>`).join("");
  const trust = `
    <div class="rail-card">
      <h2>Trust cues in this prototype</h2>
      <ul>
        <li><b>Provenance:</b> important claims show an approved policy or student-record source.</li>
        <li><b>Uncertainty:</b> conflicting or missing information becomes an “I’m not sure” state.</li>
        <li><b>Decision rights:</b> consequential actions require explicit student confirmation.</li>
      </ul>
    </div>`;
  const roles = `
    <div class="rail-card">
      <h2>Human–AI role split</h2>
      <div class="role-split">
        <div class="role-box"><h3>AI owns</h3><ul><li>retrieval</li><li>organization</li><li>dependency checks</li><li>attention support</li></ul></div>
        <div class="role-box"><h3>Student owns</h3><ul><li>goals</li><li>trade-offs</li><li>final judgment</li><li>confirmation</li></ul></div>
      </div>
    </div>`;
  $("#rail").innerHTML = `
    <div class="rail-card">
      <h2>${esc(p.title)}</h2>
      <p>${esc(p.model)}</p>
      <ul class="task-list">${tasks}</ul>
      <p style="margin-top:12px"><b>Success:</b> ${esc(p.success)}</p>
    </div>
    ${trust}
    ${roles}
    <div class="rail-card">
      <h2>Prototype boundary</h2>
      <p>Everything shown uses synthetic Demo University records and scripted responses. The prototype demonstrates interaction logic, not live university integration.</p>
    </div>`;
}

function goalView() {
  const j = journey();
  const st = student();
  return `<section class="hero">
    <span class="eyebrow">${esc(j.label)} · Goal-first interface</span>
    <h1>${esc(j.headline)}</h1>
    <p>${esc(j.description)}</p>
    <div class="goal-box">
      <label class="goal-label" for="goal-input">Student goal</label>
      <input class="goal-input" id="goal-input" value="${esc(j.goal)}" aria-label="Student goal">
      <p class="fine" style="margin:10px 0 0">Playing as ${esc(st.name)} · ${esc(st.persona)} · ${esc(st.major)}</p>
    </div>
    <div class="hero-actions">${action("Check my situation", "start", "primary")} ${action("How InterfaceDNA works", "show-method", "secondary")}</div>
    ${S.why.has("method") ? `<div class="why-panel" style="margin-top:16px"><b>Goal → verified context → focused decision support.</b><br>InterfaceDNA first identifies what must be known for this goal, retrieves only approved student/policy context, organizes the relevant consequences, then returns control to the student before any consequential action.</div>` : ""}
  </section>`;
}

function dropVerify() {
  const st = RUN.students.alex;
  const p = policy("courseDrop");
  if (S.failure === "service-outage") return outageView("Student Record Service", "The system cannot verify Alex’s current credit load, so InterfaceDNA stops before giving a drop recommendation.");
  return `<section class="card">
    <div class="card-title-row"><div><span class="eyebrow">Verification</span><h2>Checking only what matters for this decision</h2><p class="muted">The system retrieves authorized context instead of asking the student to re-enter information the university already has.</p></div>${badge("3 sources checked", "primary")}</div>
    <div class="verify-list">
      <div class="verify-row"><span class="status-icon">✓</span><div><div class="verify-title">Student enrollment record</div><div class="verify-sub">${st.currentCredits} enrolled credits in ${RUN.meta.term}</div></div>${badge("Verified", "success")}</div>
      <div class="verify-row"><span class="status-icon">✓</span><div><div class="verify-title">Course record</div><div class="verify-sub">CS 411 · 4 credits · Major required</div></div>${badge("Verified", "success")}</div>
      <div class="verify-row"><span class="status-icon">✓</span><div><div class="verify-title">Course-drop policy</div><div class="verify-sub">Approved policy version ${p.version}</div></div>${badge("Approved", "success")}</div>
    </div>
    ${sourceCard("Course Enrollment & Drop Policy", p.source, p.version, p.urlLabel)}
    <div class="btn-row" style="margin-top:18px">${action("Continue to consequences", "next", "primary")} ${action("Back", "back", "secondary")}</div>
  </section>`;
}

function dropReview() {
  if (S.failure === "policy-conflict") return policyConflictView();
  const st = RUN.students.alex;
  const p = policy("courseDrop");
  const after = st.currentCredits - 4;
  return `<section class="card">
    <div class="card-title-row"><div><span class="eyebrow">Decision summary</span><h2>If you drop CS 411</h2><p class="muted">A compact view of consequences, not a recommendation to act.</p></div>${badge("Personalized", "primary")}</div>
    <div class="grid-3" style="margin-top:18px">
      <div class="metric"><div class="metric-label">Credit load</div><div class="metric-value mono">${st.currentCredits} → ${after}</div><div class="metric-note">At the synthetic full-time threshold</div></div>
      <div class="metric"><div class="metric-label">Degree impact</div><div class="metric-value">Required course</div><div class="metric-note">Would need to be completed later</div></div>
      <div class="metric"><div class="metric-label">Verified deadline</div><div class="metric-value" style="font-size:18px">${esc(p.deadline)}</div><div class="metric-note">From approved policy v${esc(p.version)}</div></div>
    </div>
    <div class="consequence-list">
      <div class="consequence"><div class="consequence-label">Enrollment status</div><div><div class="consequence-main">You would remain at 12 enrolled credits.</div><div class="consequence-detail">The simulated full-time threshold in the approved policy is 12 credits.</div>${whyPanel("drop-credits", `<b>Reasoning receipt</b><span class="equation">${st.currentCredits} current credits − 4 CS 411 credits = ${after} credits</span>Threshold source: ${esc(p.source)}, version ${esc(p.version)}.`)}</div><div>${whyButton("drop-credits")}</div></div>
      <div class="consequence"><div class="consequence-label">Graduation progress</div><div><div class="consequence-main">CS 411 is marked as major required.</div><div class="consequence-detail">Dropping it does not remove the requirement; it moves completion to a later term.</div>${whyPanel("drop-degree", `<b>Why this appears:</b> the course record labels CS 411 as “Major required.” InterfaceDNA is surfacing the dependency, not deciding whether delaying it is acceptable for you.`)}</div><div>${whyButton("drop-degree")}</div></div>
      <div class="consequence"><div class="consequence-label">Action boundary</div><div><div class="consequence-main">No course change has been made.</div><div class="consequence-detail">The system can prepare the request, but only you can confirm it.</div>${whyPanel("drop-control", `<b>Meta-coordination:</b> AI owns retrieval and organization; the student owns final decision rights. This prevents the model from turning advice into an unreviewed action.`)}</div><div>${whyButton("drop-control")}</div></div>
    </div>
    ${sourceCard("Course Enrollment & Drop Policy", p.source, p.version, p.urlLabel)}
    <div class="callout" style="margin-top:14px"><span class="callout-icon">i</span><div><strong>Want to stress-test trust calibration?</strong><p>Use the top Failure menu → “Conflicting drop policies.” The interface should stop and escalate instead of choosing a date.</p></div></div>
    <div class="btn-row" style="margin-top:18px">${action("Review before action", "next", "primary")} ${action("Back to verification", "back", "secondary")}</div>
  </section>`;
}

function policyConflictView() {
  const c = policy("courseDropConflict");
  mark("why");
  return `<section class="card warn">
    <div class="card-title-row"><div><span class="eyebrow" style="color:var(--danger)">Uncertainty state</span><h2>I’m not sure which drop deadline controls.</h2><p class="muted">Two retrieved sources disagree, so InterfaceDNA will not silently pick the answer that looks newer or more convenient.</p></div>${badge("Escalation required", "danger")}</div>
    <div class="conflict-grid">
      <div class="conflict"><span class="fine">${esc(c.sourceA.title)} · v${esc(c.sourceA.version)}</span><strong>${esc(c.sourceA.date)}</strong></div>
      <div class="conflict"><span class="fine">${esc(c.sourceB.title)} · v${esc(c.sourceB.version)}</span><strong>${esc(c.sourceB.date)}</strong></div>
    </div>
    <div class="callout"><span class="callout-icon">!</span><div><strong>Safe next step</strong><p>Verify the controlling deadline with the Office of the Registrar before continuing. The course-drop action is disabled until the conflict is resolved.</p></div></div>
    ${whyPanel("conflict", `<b>Theory interpretation:</b> this is a memory/provenance and meta-coordination problem. A correct hybrid system should expose the disagreement, preserve student awareness, and escalate to the authoritative office rather than inventing certainty.`)}
    <div class="btn-row" style="margin-top:16px">${whyButton("conflict", "Why stop here?")} ${action("Simulate Registrar clarification", "resolve-conflict", "primary")} ${action("Back", "back", "secondary")}</div>
  </section>`;
}

function dropConfirm() {
  const st = RUN.students.alex;
  return `<section class="confirm-box">
    <span class="eyebrow" style="color:var(--danger)">Student decision required</span>
    <h2 style="margin:8px 0">Confirm the simulated drop request</h2>
    <p class="muted">InterfaceDNA has prepared the action, but it will not represent the course as dropped until the connected university system returns confirmation.</p>
    <div class="grid-2" style="margin-top:18px">
      <div class="metric"><div class="metric-label">Course</div><div class="metric-value" style="font-size:20px">CS 411</div><div class="metric-note">4 credits · Major required</div></div>
      <div class="metric"><div class="metric-label">After request</div><div class="metric-value mono">12 credits</div><div class="metric-note">If the university system accepts the request</div></div>
    </div>
    <label class="confirm-check"><input type="checkbox" id="drop-confirm" ${S.confirmChecked ? "checked" : ""}><span>I reviewed the consequences and understand that this prototype is a simulation.</span></label>
    <div class="btn-row">${action("Confirm simulated request", "confirm-drop", "danger", !S.confirmChecked)} ${action("Cancel", "cancel", "secondary")}</div>
  </section>`;
}

function dropDone() {
  mark("confirm"); mark("done");
  return `<section class="card success success-hero">
    <div class="success-icon">✓</div>
    <span class="eyebrow" style="color:var(--success)">Simulation complete</span>
    <h2 style="font-size:30px;margin:8px 0">Request accepted by the simulated university system</h2>
    <p class="muted">In the target product, InterfaceDNA would wait for the university system response before showing completion. This prototype has not changed any real enrollment.</p>
    <div class="btn-row" style="justify-content:center;margin-top:20px">${action("Try graduation readiness", "to-grad", "primary")} ${action("Restart this journey", "restart", "secondary")}</div>
  </section>`;
}

function gradVerify() {
  const st = RUN.students.maya;
  const p = policy("graduation");
  if (S.failure === "missing-record") return missingRecordView();
  return `<section class="card">
    <div class="card-title-row"><div><span class="eyebrow">Verification</span><h2>Match the degree audit to the governing catalog</h2><p class="muted">Graduation advice is only as reliable as the record and catalog context behind it.</p></div>${badge("Catalog year matched", "success")}</div>
    <div class="verify-list">
      <div class="verify-row"><span class="status-icon">✓</span><div><div class="verify-title">Degree audit</div><div class="verify-sub">${st.completedCredits} completed credits · ${st.currentCredits} currently enrolled</div></div>${badge("Verified", "success")}</div>
      <div class="verify-row"><span class="status-icon">✓</span><div><div class="verify-title">Catalog year</div><div class="verify-sub">${esc(st.catalogYear)} requirements</div></div>${badge("Matched", "success")}</div>
      <div class="verify-row"><span class="status-icon">✓</span><div><div class="verify-title">Current-term enrollment</div><div class="verify-sub">IS 492, IS 455, STAT 385</div></div>${badge("Verified", "success")}</div>
    </div>
    ${sourceCard(p.title, p.source, p.version, p.urlLabel)}
    <div class="btn-row" style="margin-top:18px">${action("Build readiness summary", "next", "primary")} ${action("Back", "back", "secondary")}</div>
  </section>`;
}

function gradReview() {
  const st = RUN.students.maya;
  const g = st.graduation;
  const percent = Math.min(100, Math.round((g.completed / g.totalRequired) * 100));
  return `<section class="card">
    <div class="card-title-row"><div><span class="eyebrow">Graduation readiness</span><h2>You are on track if current coursework is completed.</h2><p class="muted">The summary separates completed, in-progress, and still-dependent requirements.</p></div>${badge("Evidence-backed", "primary")}</div>
    <div class="grid-3" style="margin-top:18px">
      <div class="metric"><div class="metric-label">Completed</div><div class="metric-value mono">${g.completed} / ${g.totalRequired}</div><div class="progress-bar" style="margin-top:10px"><span style="width:${percent}%"></span></div></div>
      <div class="metric"><div class="metric-label">In progress</div><div class="metric-value mono">${g.inProgress}</div><div class="metric-note">Current term</div></div>
      <div class="metric"><div class="metric-label">Current status</div><div class="metric-value" style="font-size:20px">On track</div><div class="metric-note">Conditional on current course completion</div></div>
    </div>
    <div class="table-wrap" style="margin-top:18px"><table><thead><tr><th>Requirement</th><th>Status</th><th>Evidence</th><th>Interrogate</th></tr></thead><tbody>
      ${g.requirements.map((r, i) => `<tr><td><b>${esc(r.name)}</b></td><td>${badge(r.status, r.status === "Satisfied" ? "success" : "warning")}</td><td>${esc(r.detail)}</td><td>${whyButton(`grad-${i}`)}${whyPanel(`grad-${i}`, `<b>Why this status:</b> InterfaceDNA combined the degree-audit row for “${esc(r.name)}” with the ${esc(st.catalogYear)} catalog rule. It does not infer completion from unrelated courses.`)}</td></tr>`).join("")}
    </tbody></table></div>
    ${sourceCard("Bachelor's Degree Requirements", RUN.policies.graduation.source, RUN.policies.graduation.version, RUN.policies.graduation.urlLabel)}
    <div class="btn-row" style="margin-top:18px">${action("Create my graduation plan", "next", "primary")} ${action("Back", "back", "secondary")}</div>
  </section>`;
}

function gradPlan() {
  return `<section class="card">
    <div class="card-title-row"><div><span class="eyebrow">Student-approved plan</span><h2>Finish the current term, then re-check the audit.</h2><p class="muted">The AI can organize a plan, but it does not enroll the student or declare graduation eligibility.</p></div>${badge("Student reviews", "primary")}</div>
    <div class="checklist">
      <div class="check-row"><span class="checkmark">1</span><div><b>Complete IS 492</b><div class="fine">Capstone is in progress and remains a dependency.</div></div></div>
      <div class="check-row"><span class="checkmark">2</span><div><b>Complete current 12-credit term</b><div class="fine">Projected total exceeds the 120-credit synthetic university minimum.</div></div></div>
      <div class="check-row"><span class="checkmark">3</span><div><b>Run final degree-audit check after grades post</b><div class="fine">Final eligibility belongs to the university’s official audit/registrar process.</div></div></div>
    </div>
    <label class="confirm-check"><input type="checkbox" id="plan-confirm" ${S.planChecked ? "checked" : ""}><span>I reviewed this as a planning aid, not an official graduation clearance.</span></label>
    <div class="btn-row">${action("Save simulated plan", "confirm-plan", "primary", !S.planChecked)} ${action("Back", "back", "secondary")}</div>
  </section>`;
}

function gradDone() {
  mark("confirm"); mark("done");
  return `<section class="card success success-hero"><div class="success-icon">✓</div><span class="eyebrow" style="color:var(--success)">Plan saved</span><h2 style="font-size:30px;margin:8px 0">Graduation-readiness plan saved to the prototype</h2><p class="muted">No official graduation clearance was issued. The target system would re-check official records after current-term grades post.</p><div class="btn-row" style="justify-content:center;margin-top:20px">${action("Try registration hold", "to-hold", "primary")} ${action("Restart", "restart", "secondary")}</div></section>`;
}

function missingRecordView() {
  mark("why");
  return `<section class="card warn">
    <div class="card-title-row"><div><span class="eyebrow" style="color:var(--danger)">Incomplete context</span><h2>I’m not sure whether the transfer-credit requirement is satisfied.</h2><p class="muted">The degree audit references transfer coursework, but the supporting equivalency record is unavailable.</p></div>${badge("Do not guess", "danger")}</div>
    <div class="callout"><span class="callout-icon">!</span><div><strong>What InterfaceDNA can still say</strong><p>The verified requirements can be summarized, but the graduation-readiness conclusion remains provisional until the missing record is resolved.</p></div></div>
    ${whyPanel("missing-grad", `<b>Why this matters:</b> a general AI assistant might fill the missing context with assumptions. InterfaceDNA treats missing institutional memory as a first-class uncertainty state and escalates rather than hallucinating.`)}
    <div class="btn-row" style="margin-top:16px">${whyButton("missing-grad", "Why not infer it?")} ${action("Simulate record restored", "resolve-missing", "primary")} ${action("Back", "back", "secondary")}</div>
  </section>`;
}

function holdVerify() {
  const st = RUN.students.jordan;
  if (S.failure === "service-outage") return outageView("Registration Holds Service", "InterfaceDNA can see that registration is blocked, but the live hold details cannot be verified right now.");
  return `<section class="card">
    <div class="card-title-row"><div><span class="eyebrow">Verification</span><h2>Two holds are blocking registration.</h2><p class="muted">Each blocker stays attached to the office that owns it.</p></div>${badge("2 holds found", "warning")}</div>
    <div class="verify-list">
      ${st.holds.map((h, i) => `<div class="verify-row"><span class="status-icon warn">${i+1}</span><div><div class="verify-title">${esc(h.type)}</div><div class="verify-sub">${esc(h.reason)} · Owner: ${esc(h.office)}</div></div>${badge(h.status, "warning")}</div>`).join("")}
    </div>
    ${sourceCard(RUN.policies.registration.title, RUN.policies.registration.source, RUN.policies.registration.version, RUN.policies.registration.urlLabel)}
    <div class="btn-row" style="margin-top:18px">${action("Show resolution steps", "next", "primary")} ${action("Back", "back", "secondary")}</div>
  </section>`;
}

function holdResolve() {
  const holds = RUN.students.jordan.holds;
  return `<section class="card">
    <div class="card-title-row"><div><span class="eyebrow">Resolution plan</span><h2>One request can be initiated here; one must stay with Student Accounts.</h2><p class="muted">The interface coordinates the work without pretending every hold has the same permissions.</p></div>${badge("Role partitioned", "primary")}</div>
    <div class="grid-2" style="margin-top:18px">
      <div class="metric"><div class="metric-label">${esc(holds[0].type)}</div><div class="metric-value" style="font-size:19px">Academic Advising</div><div class="metric-note">InterfaceDNA can prepare a simulated clearance-review request.</div>${whyButton("hold-advising", "Why this office?")}${whyPanel("hold-advising", `<b>Ownership:</b> the hold record explicitly lists Academic Advising as the responsible office. The AI is routing based on verified metadata, not guessing from the hold name.`)}</div>
      <div class="metric"><div class="metric-label">${esc(holds[1].type)}</div><div class="metric-value" style="font-size:19px">Student Accounts</div><div class="metric-note">This prototype cannot clear or request removal of an account hold.</div>${whyButton("hold-accounts", "Why can’t AI clear it?")}${whyPanel("hold-accounts", `<b>Decision boundary:</b> the hold is owned by Student Accounts and may depend on information or permissions unavailable to the assistant. InterfaceDNA surfaces the correct office rather than claiming success.`)}</div>
    </div>
    <div class="callout" style="margin-top:16px"><span class="callout-icon">→</span><div><strong>Recommended sequence</strong><p>Request the advising review first, then complete the Student Accounts review. Re-check registration only after both university systems confirm clearance.</p></div></div>
    <div class="btn-row" style="margin-top:18px">${action("Prepare advising request", "next", "primary")} ${action("Back", "back", "secondary")}</div>
  </section>`;
}

function holdConfirm() {
  return `<section class="confirm-box">
    <span class="eyebrow">Student decision required</span><h2 style="margin:8px 0">Send a simulated advising-review request?</h2><p class="muted">This only represents the request the student is authorized to initiate. It does not clear either hold.</p>
    <div class="source-card"><div><strong>Request destination</strong><span>Academic Advising · Required semester planning check-in</span></div>${badge("Student may initiate", "success")}</div>
    <label class="confirm-check"><input type="checkbox" id="hold-confirm" ${S.holdChecked ? "checked" : ""}><span>I understand this is a simulated request and that the hold remains until the university office confirms clearance.</span></label>
    <div class="btn-row">${action("Confirm simulated request", "confirm-hold", "primary", !S.holdChecked)} ${action("Cancel", "cancel", "secondary")}</div>
  </section>`;
}

function holdDone() {
  mark("confirm"); mark("done");
  return `<section class="card success success-hero"><div class="success-icon">✓</div><span class="eyebrow" style="color:var(--success)">Request prepared</span><h2 style="font-size:30px;margin:8px 0">Advising review requested in the simulation</h2><p class="muted">The registration block is still shown as active because the university office has not returned a clearance confirmation. Student Accounts remains a separate next step.</p><div class="btn-row" style="justify-content:center;margin-top:20px">${action("Restart all journeys", "reset-all", "primary")} ${action("Back to holds", "restart", "secondary")}</div></section>`;
}

function outageView(service, detail) {
  mark("why");
  return `<section class="card warn"><div class="card-title-row"><div><span class="eyebrow" style="color:var(--danger)">Verification unavailable</span><h2>I’m not sure because ${esc(service)} is unavailable.</h2><p class="muted">${esc(detail)}</p></div>${badge("No unverified answer", "danger")}</div><div class="callout"><span class="callout-icon">↻</span><div><strong>Fallback</strong><p>Keep the student’s goal and progress, show what could not be verified, and offer a retry or the authoritative office rather than fabricating a result.</p></div></div>${whyPanel("outage", `<b>Complementarity:</b> the AI should reduce work when institutional memory is available, but it should not replace missing institutional memory with model recall.`)}<div class="btn-row" style="margin-top:16px">${whyButton("outage", "Why stop?")} ${action("Retry successfully", "resolve-outage", "primary")} ${action("Back", "back", "secondary")}</div></section>`;
}

function renderContent() {
  const s = S.stage;
  if (s === 0) return goalView();
  if (S.journey === "drop") return [null, dropVerify, dropReview, dropConfirm, dropDone][s]();
  if (S.journey === "grad") return [null, gradVerify, gradReview, gradPlan, gradDone][s]();
  return [null, holdVerify, holdResolve, holdConfirm, holdDone][s]();
}

function render() {
  renderStages();
  renderRail();
  $("#content").innerHTML = renderContent();
  $("#persona").value = S.persona;
  $("#failure").value = S.failure;
}

// ---------- Events ----------

document.addEventListener("click", (event) => {
  const journeyButton = event.target.closest("[data-journey]");
  if (journeyButton) {
    setJourney(journeyButton.dataset.journey);
    return;
  }

  const why = event.target.closest("[data-why]");
  if (why) {
    const key = why.dataset.why;
    if (S.why.has(key)) S.why.delete(key); else { S.why.add(key); mark("why"); }
    render();
    return;
  }

  const target = event.target.closest("[data-action]");
  if (!target) return;
  const name = target.dataset.action;

  if (name === "show-method") { S.why.has("method") ? S.why.delete("method") : S.why.add("method"); render(); return; }
  if (name === "start") { mark("goal"); go(1); return; }
  if (name === "next") { go(S.stage + 1); return; }
  if (name === "back") { go(S.stage - 1); return; }
  if (name === "cancel") { toast("No action taken. Student control preserved."); go(2); return; }
  if (name === "restart") { S.stage = 0; S.failure = ""; S.why.clear(); S.confirmChecked = S.planChecked = S.holdChecked = false; $("#failure").value = ""; render(); return; }
  if (name === "reset-all") { S = freshState(); $("#persona").value = "alex"; $("#failure").value = ""; render(); return; }
  if (name === "to-grad") { setJourney("grad"); return; }
  if (name === "to-hold") { setJourney("hold"); return; }

  if (name === "resolve-conflict") {
    S.failure = "";
    $("#failure").value = "";
    toast("Simulated clarification: approved policy v2026.09 controls. Returning to the consequence summary.");
    render();
    return;
  }
  if (name === "resolve-missing") {
    S.failure = "";
    $("#failure").value = "";
    toast("Synthetic transfer-credit record restored.");
    render();
    return;
  }
  if (name === "resolve-outage") {
    S.failure = "";
    $("#failure").value = "";
    toast("Synthetic university service restored.");
    render();
    return;
  }

  if (name === "confirm-drop") {
    if (!S.confirmChecked) { toast("Review and check the confirmation box first."); return; }
    mark("confirm"); go(4); return;
  }
  if (name === "confirm-plan") {
    if (!S.planChecked) { toast("Review and check the planning disclaimer first."); return; }
    mark("confirm"); go(4); return;
  }
  if (name === "confirm-hold") {
    if (!S.holdChecked) { toast("Review and check the confirmation box first."); return; }
    mark("confirm"); go(4); return;
  }
});

document.addEventListener("change", (event) => {
  if (event.target.id === "persona") {
    S.persona = event.target.value;
    const corresponding = Object.entries(JOURNEYS).find(([, value]) => value.persona === S.persona)?.[0];
    if (corresponding) S.journey = corresponding;
    S.stage = 0; S.failure = ""; S.completed.clear(); S.why.clear();
    $("#failure").value = "";
    render();
    return;
  }
  if (event.target.id === "failure") {
    S.failure = event.target.value;
    if (S.failure === "policy-conflict") { S.journey = "drop"; S.persona = "alex"; S.stage = 2; mark("goal"); mark("verify"); }
    if (S.failure === "missing-record") { S.journey = "grad"; S.persona = "maya"; S.stage = 1; mark("goal"); }
    if (S.failure === "service-outage") { S.journey = "hold"; S.persona = "jordan"; S.stage = 1; mark("goal"); }
    $("#persona").value = S.persona;
    render();
    return;
  }
  if (event.target.id === "drop-confirm") { S.confirmChecked = event.target.checked; render(); return; }
  if (event.target.id === "plan-confirm") { S.planChecked = event.target.checked; render(); return; }
  if (event.target.id === "hold-confirm") { S.holdChecked = event.target.checked; render(); return; }
});

$("#theme").addEventListener("click", () => {
  const dark = document.documentElement.dataset.theme === "dark";
  document.documentElement.dataset.theme = dark ? "light" : "dark";
  $("#theme").textContent = dark ? "Dark" : "Light";
  $("#theme").setAttribute("aria-pressed", String(!dark));
});

$("#reset").addEventListener("click", () => {
  S = freshState();
  $("#persona").value = "alex";
  $("#failure").value = "";
  render();
  toast("Prototype reset.");
});

render();
