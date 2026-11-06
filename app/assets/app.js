'use strict';
// InterfaceDNA Student Services: choose a student -> choose a service -> describe
// the goal -> review the adaptive page -> confirm. Hash routes keep the browser
// back button working: #/, #/sources, #/s/ID, #/s/ID/ask/TASK, #/s/ID/result, #/s/ID/done

const $ = id => document.getElementById(id);
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));

const STEPS = ['Choose a student', 'Choose a service', 'Describe your goal', 'Review your page', 'Confirm'];
// Students set up for the presentation scenarios get their scenario's question first.
const FEATURED = {
  S00001: {task: 'drop', question: 'Can I drop CS 411?'},
  S00004: {task: 'drop', question: 'Can I drop CS 440?'},
};
const TASKS = {
  drop: {icon: '−', title: 'Drop a course', desc: 'See credit, visa, tuition and deadline consequences before you drop.',
    suggest: p => droppable(p).slice(0, 3).map(c => `Can I drop ${c.code}?`).concat(droppable(p)[0] ? [`What happens if I withdraw from ${droppable(p)[0].code}?`] : ['Can I drop a course?'])},
  graduation: {icon: '✓', title: 'Graduation check', desc: 'Compare your record with your degree requirements.',
    suggest: () => ['What do I still need to graduate?', 'Am I on track to graduate in December?']},
  hold: {icon: '!', title: 'Registration & holds', desc: 'See holds that could block Spring 2027 registration.',
    suggest: () => ['Why can’t I register for spring?', 'Do I have any holds on my account?']},
  courses: {icon: '⌕', title: 'Find courses', desc: 'Search the class schedule by term, subject, credit hours or topic.',
    suggest: () => [`Show me 3 credit courses I can take in ${S.term}`, `What 400-level CS courses are offered in ${S.term}?`, 'Tell me about CS 425']},
  policy: {icon: '§', title: 'Policies & deadlines', desc: 'Ask about deadlines, refunds, full-time rules or registration dates.',
    suggest: () => [`What are the drop deadlines for ${S.term}?`, 'How many credits do international students need?', 'When does spring registration open?']},
  any: {icon: '?', title: 'Something else', desc: 'Describe what you want to do in your own words.',
    suggest: p => ['What do I still need to graduate?', droppable(p)[0] ? `Can I drop ${droppable(p)[0].code}?` : 'Can I drop a course?', 'Why can’t I register?']},
};
const GROUPS = [
  ['Stops this action', c => c.blocks],
  ['Needs attention', c => !c.blocks && c.level === 'warn'],
  ['Not verified by the sources', c => !c.blocks && c.level === 'unknown'],
  ['Good to know', c => !c.blocks && c.level === 'info'],
  ['Verified', c => !c.blocks && c.level === 'ok'],
];
const LEVEL = {ok: ['Verified', 'ok'], info: ['Note', 'info'], warn: ['Needs attention', 'warn'], block: ['Blocks action', 'block'], unknown: ['Not verified', '']};

const droppable = p => p.term_courses.filter(c => c.status !== 'Completed');
const S = {
  term: null, terms: [], current: null,
  students: [], profile: null, rulesDate: null, sourcesData: null,
  filter: {q: '', program: '', status: ''}, page: 0,
  task: 'any', question: '', busy: false, error: '',
  sid: null, result: null, intent: null, entities: {}, interpretation: '', usage: null, receipt: null, action: '',
};

// ---- API ---------------------------------------------------------------------
async function api(path, body) {
  const resp = await fetch(path, body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : undefined);
  let data;
  try { data = await resp.json(); } catch { throw Error('The server returned an invalid response.'); }
  if (!resp.ok) {
    if (typeof data.detail === 'string') throw Error(data.detail);
    const field = Array.isArray(data.detail) && data.detail[0]?.loc?.at(-1);
    throw Error(field === 'message' ? 'Please describe your goal in 3 to 1,000 characters.' : 'Request failed. Please try again.');
  }
  return data;
}
async function loadProfile(id) {
  if (S.profile?.id === id && S.profile.term === S.term) return S.profile;
  S.profile = await api(`/api/students/${encodeURIComponent(id)}?term=${encodeURIComponent(S.term)}`);
  return S.profile;
}
const termInfo = () => S.terms.find(t => t.term === S.term) || {};
const STATUS_WORD = {past: 'past', current: 'current', upcoming: 'upcoming'};
function fillTerms() {
  $('term').innerHTML = S.terms.map(t => `<option value="${esc(t.term)}" ${t.term === S.term ? 'selected' : ''}>${esc(t.term)} (${STATUS_WORD[t.status]})</option>`).join('');
  $('term-dates').textContent = termInfo().display || '';
}
async function setTerm(term) {
  S.term = term;
  try { localStorage.setItem('idna-term', term); } catch {}
  fillTerms();
  Object.assign(S, {sid: null, result: null, receipt: null, error: '', page: 0});
  S.students = await api(`/api/students?term=${encodeURIComponent(term)}`);
  // A page built for one term doesn't carry over to another: go back to the dashboard.
  const m = location.hash.match(/^#\/s\/(S\d{5})\/(result|done)$/);
  if (m) go(`#/s/${m[1]}`, true); else route();
}

// ---- Shell -------------------------------------------------------------------
function notify(msg) { const el = $('toast'); el.textContent = msg; el.hidden = false; clearTimeout(notify.t); notify.t = setTimeout(() => el.hidden = true, 3500); }
function setSteps(active) {
  $('steps').innerHTML = STEPS.map((s, i) => `<li class="${i < active ? 'done' : ''}" ${i === active ? 'aria-current="step"' : ''}>${esc(s)}</li>`).join('');
}
function setChrome(route) {
  const p = S.profile;
  const onStudent = route.startsWith('#/s/') && p;
  $('whoami').hidden = !onStudent;
  if (onStudent) $('whoami').innerHTML = `Viewing as <strong>${esc(p.name)}</strong> · ${esc(p.id)}<br><button type="button" id="switch">Switch student</button>`;
  const dash = $('nav-dashboard');
  dash.hidden = !p;
  if (p) dash.href = `#/s/${p.id}`;
  document.querySelectorAll('[data-nav]').forEach(a => a.removeAttribute('aria-current'));
  const current = route === '#/sources' ? 'sources' : route.startsWith('#/s/') ? 'dashboard' : 'home';
  document.querySelector(`[data-nav="${current}"]`)?.setAttribute('aria-current', 'page');
  $('demo').hidden = !route.endsWith('/result');
}
function render(html, step, focus = true) {
  setSteps(step);
  $('main').innerHTML = html;
  setChrome(location.hash || '#/');
  if (focus) ($('main').querySelector('h1') || $('main')).focus?.();
}
const level = l => l === 'GR' ? 'Graduate' : 'Undergraduate';
const gpa = g => g == null ? '—' : Number(g).toFixed(2);
const longDate = iso => new Date(`${iso}T12:00:00`).toLocaleDateString('en-US', {month: 'long', day: 'numeric', year: 'numeric'});
const crumbs = (...parts) => `<nav class="crumbs" aria-label="Breadcrumb">${parts.map(([label, href]) => href ? `<a href="${href}">${esc(label)}</a>` : esc(label)).join(' / ')}</nav>`;

// ---- Step 1: choose a student ------------------------------------------------
function filtered() {
  const {q, program, status} = S.filter;
  const needle = q.trim().toLowerCase();
  return S.students.filter(s =>
    (!needle || s.name.toLowerCase().includes(needle) || s.id.toLowerCase().includes(needle)) &&
    (!program || s.program === program) &&
    (!status || (status === 'visa' && s.visa) || (status === 'holds' && s.holds) || (status === 'part' && s.term_credits < 12)));
}
function viewHome() {
  const programs = [...new Map(S.students.map(s => [s.program, s.program_name])).entries()];
  render(`
    <section class="hero">
      <h1 tabindex="-1">Student Services</h1>
      <p>Plan a course drop, check your graduation progress or sort out a registration hold. Describe what you want to do,
      and InterfaceDNA builds a page for that task from your record and quoted university policy, then asks you to confirm before anything happens.</p>
      <div class="facts">
        <span><strong>${esc(S.term)}</strong>${esc(termInfo().display || '')}</span>
        ${(termInfo().key_dates || []).filter(d => !d.past).slice(0, 3).map(d =>
          `<span><strong>${esc(d.display.replace(/, \d{4}$/, ''))}</strong>${esc(d.label)}</span>`).join('')}
      </div>
    </section>
    <h2>Student directory</h2>
    <div class="filters">
      <input type="search" id="q" placeholder="Search by name or ID" aria-label="Search students" value="${esc(S.filter.q)}">
      <select id="program" aria-label="Program"><option value="">All programs</option>${programs.map(([c, n]) => `<option value="${esc(c)}" ${S.filter.program === c ? 'selected' : ''}>${esc(n)}</option>`).join('')}</select>
      <select id="status" aria-label="Filter"><option value="">Everyone</option>
        <option value="visa" ${S.filter.status === 'visa' ? 'selected' : ''}>F-1 / J-1 students</option>
        <option value="holds" ${S.filter.status === 'holds' ? 'selected' : ''}>Has holds</option>
        <option value="part" ${S.filter.status === 'part' ? 'selected' : ''}>Under 12 hours</option></select>
    </div>
    <div id="directory"></div>`, 0);
  renderDirectory();
  $('q').addEventListener('input', e => { S.filter.q = e.target.value; S.page = 0; renderDirectory(); });
  $('program').addEventListener('change', e => { S.filter.program = e.target.value; S.page = 0; renderDirectory(); });
  $('status').addEventListener('change', e => { S.filter.status = e.target.value; S.page = 0; renderDirectory(); });
}
function renderDirectory() {
  const rows = filtered(), per = 15, pages = Math.max(1, Math.ceil(rows.length / per));
  S.page = Math.min(S.page, pages - 1);
  const shown = rows.slice(S.page * per, S.page * per + per);
  $('directory').innerHTML = `
    <div class="table-wrap"><table>
      <thead><tr><th>ID</th><th>Name</th><th>Program</th><th>Level</th><th>Visa</th><th>${esc(S.term)} hours</th><th>Holds</th><th>GPA</th></tr></thead>
      <tbody>${shown.map(s => `<tr class="pick" tabindex="0" data-student="${esc(s.id)}">
        <td>${esc(s.id)}</td><td><strong>${esc(s.name)}</strong></td><td>${esc(s.program_name)}</td><td>${esc(level(s.level))}</td>
        <td>${s.visa ? `<span class="badge info">${esc(s.visa)}</span>` : '<span class="muted">Domestic</span>'}</td>
        <td>${esc(s.term_credits || '—')}</td><td>${s.holds ? `<span class="badge warn">${esc(s.holds)}</span>` : '<span class="muted">—</span>'}</td>
        <td>${esc(gpa(s.gpa))}</td></tr>`).join('') || '<tr><td colspan="8" class="muted">No students match.</td></tr>'}</tbody>
    </table></div>
    <div class="pager"><span>${rows.length} students · page ${S.page + 1} of ${pages}</span>
      <span class="actions" style="margin:0"><button type="button" class="btn secondary" id="prev" ${S.page === 0 ? 'disabled' : ''}>Previous</button>
      <button type="button" class="btn secondary" id="next" ${S.page >= pages - 1 ? 'disabled' : ''}>Next</button></span></div>`;
  $('directory').querySelectorAll('tr[data-student]').forEach(tr => {
    tr.addEventListener('click', () => go(`#/s/${tr.dataset.student}`));
    tr.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(`#/s/${tr.dataset.student}`); } });
  });
  $('prev').addEventListener('click', () => { S.page--; renderDirectory(); });
  $('next').addEventListener('click', () => { S.page++; renderDirectory(); });
}

// ---- Step 2: dashboard -------------------------------------------------------
function requestsCard(p) {
  const rows = p.requests || [];
  return `<section class="card"><h2>My requests</h2>
    ${rows.length ? `<div class="table-wrap"><table><thead><tr><th>Date</th><th>Request</th><th>Term</th><th>Receipt</th><th>Status</th></tr></thead><tbody>
      ${rows.map(r => `<tr><td>${esc(new Date(r.created_at).toLocaleDateString('en-US', {month: 'long', day: 'numeric', year: 'numeric'}))}</td><td>${esc(r.details.description)}</td><td>${esc(r.term)}</td>
        <td><code title="${esc(r.receipt)}">${esc(r.receipt.slice(0, 8))}</code></td><td><span class="badge ok">Recorded</span></td></tr>`).join('')}
    </tbody></table></div>` : '<p class="muted">No requests yet. Requests you confirm appear here with their receipt.</p>'}</section>`;
}
function scheduleCard(p) {
  const info = p.term_info || {}, past = info.status === 'past';
  const dropRequested = new Set((p.requests || []).filter(r => r.intent === 'drop' && r.term === p.term).map(r => r.entities.course_code));
  const title = past ? `${p.term} courses` : info.status === 'upcoming' ? `${p.term} registration` : `${p.term} schedule`;
  const rows = p.term_courses;
  const note = info.note ? `<div class="alert info small">${esc(info.note)}</div>` : '';
  if (!rows.length) return `<section class="card"><h2>${esc(title)}</h2>${note}<p class="muted">No courses ${past ? 'taken' : 'registered'} for ${esc(p.term)}.</p></section>`;
  return `<section class="card"><h2>${esc(title)}</h2>${note}<div class="table-wrap"><table><thead><tr><th>Course</th><th>Title</th><th>Hours</th><th>${past ? 'Grade' : 'Status'}</th></tr></thead><tbody>
    ${rows.map(c => `<tr><td><strong>${esc(c.code)}</strong></td><td>${esc(c.title)}</td><td>${esc(c.credits)}</td><td>${past ? esc(c.grade || '—') : dropRequested.has(c.code) ? '<span class="badge warn">Drop requested</span>' : `<span class="badge ${c.status === 'Registered' ? 'info' : 'ok'}">${esc(c.status)}</span>`}</td></tr>`).join('')}
    <tr><td></td><td><strong>Total</strong></td><td><strong>${esc(p.term_credits)}</strong></td><td></td></tr></tbody></table></div>
    <p class="muted small" style="margin-top:8px">Course titles and credit hours from the 2026–2027 Academic Catalog.</p></section>`;
}
function viewDashboard(p) {
  const upcoming = p.key_dates.filter(d => !d.past), past = p.key_dates.filter(d => d.past);
  const dateRow = d => `<li class="${d.past ? 'past' : ''}"><span class="when">${esc(d.display.replace(/, \d{4}$/, ''))}</span>
    <span>${esc(d.label)}<br><span class="muted small">${esc(d.source.publisher)}, ${esc(d.source.title)}, p. ${esc(d.source.page)}</span></span></li>`;
  render(`
    ${crumbs(['Students', '#/'], [p.name])}
    <div class="page-head"><div><h1 tabindex="-1">Welcome, ${esc(p.name.split(' ')[0])}</h1>
      <p>${esc(p.program_name)} · ${esc(level(p.level))} · ${esc(p.term)}</p></div></div>
    ${p.holds.length ? `<div class="alert warn"><strong>${p.holds.length} active hold(s)</strong> may block ${esc('Spring 2027')} registration. Use <em>Registration &amp; holds</em> below to see what they mean.</div>` : ''}
    <div class="grid two">
      <div>
        <section class="card"><h2>What would you like to do?</h2>
          <p class="muted">Pick a service, or describe your goal in your own words. The next page is built around your answer.</p>
          <div class="tiles">${Object.entries(TASKS).map(([k, t]) => `
            <button type="button" class="tile" data-task="${k}"><span class="icon" aria-hidden="true">${t.icon}</span>
              <h3>${esc(t.title)}</h3><p>${esc(t.desc)}</p></button>`).join('')}</div>
        </section>
        ${scheduleCard(p)}
        ${requestsCard(p)}
      </div>
      <div>
        <section class="card profile"><h2>Student record</h2>
          <dl><dt>Name</dt><dd>${esc(p.name)}</dd><dt>ID</dt><dd>${esc(p.id)}</dd>
          <dt>Program</dt><dd>${esc(p.program_name)}</dd><dt>Level</dt><dd>${esc(level(p.level))}</dd>
          <dt>Visa</dt><dd>${esc(p.visa || 'Domestic')}</dd>${p.assistantship ? '<dt>Funding</dt><dd>Assistantship</dd>' : ''}
          <dt>Admitted</dt><dd>${esc(p.admit_term)}</dd><dt>GPA</dt><dd>${esc(gpa(p.gpa))}</dd>
          <dt>Holds</dt><dd>${p.holds.length ? p.holds.map(h => esc(h.type)).join(', ') : 'None'}</dd></dl>
        </section>
        <section class="card"><h2>Key dates</h2>
          <p class="muted small">${esc(p.term)} academic calendar, as of ${esc(longDate(p.rules_date))}.</p>
          <ul class="dates">${upcoming.map(dateRow).join('') || '<li><span></span><span class="muted">No upcoming dates.</span></li>'}</ul>
          ${past.length ? `<details style="margin-top:10px"><summary class="muted small">${past.length} past dates</summary><ul class="dates">${past.map(dateRow).join('')}</ul></details>` : ''}
        </section>
      </div>
    </div>`, 1);
  $('main').querySelectorAll('[data-task]').forEach(b => b.addEventListener('click', () => go(`#/s/${p.id}/ask/${b.dataset.task}`)));
}

// ---- Step 3: describe the goal -----------------------------------------------
function viewAsk(p, task) {
  const t = TASKS[task] || TASKS.any;
  const demo = FEATURED[p.id]?.task === task && S.term === S.current ? [FEATURED[p.id].question] : [];
  const suggestions = [...new Set([...demo, ...t.suggest(p)].filter(Boolean))];
  const key = `${p.id}|${S.term}`;
  if (S.task !== task || S.askedFor !== key || !S.question) { S.task = task; S.askedFor = key; S.question = suggestions[0] || ''; }
  render(`
    ${crumbs(['Students', '#/'], [p.name, `#/s/${p.id}`], [t.title])}
    <div class="page-head"><div><h1 tabindex="-1">${esc(t.title)}</h1><p>${esc(t.desc)}${task === 'drop' ? ` Term: <strong>${esc(S.term)}</strong>.` : ''}</p></div></div>
    <div class="grid two">
      <section class="card">
        <label class="field" for="question">What do you want to do?</label>
        <textarea id="question" maxlength="1000">${esc(S.question)}</textarea>
        <div class="chips" aria-label="Suggestions">${suggestions.map(s => `<button type="button" class="chip">${esc(s)}</button>`).join('')}</div>
        ${S.error ? `<div class="alert block" role="alert" style="margin-top:14px">${esc(S.error)}</div>` : ''}
        <div class="actions"><button type="button" class="btn primary" id="analyze" ${S.busy ? 'disabled' : ''}>${S.busy ? 'Building your page…' : 'Build my page'}</button>
          <a class="btn secondary" href="#/s/${esc(p.id)}">Back</a></div>
        ${S.busy ? `<ul class="progress" aria-live="polite">
          <li class="active">Understanding your goal (live AI)</li><li class="active">Checking ${esc(p.name.split(' ')[0])}'s record</li>
          <li class="active">Checking quoted university policy</li></ul>` : ''}
      </section>
      <aside class="card"><h3>How this works</h3>
        <p class="small muted">A language model (Groq) reads only your question to work out the task and any course you name. It never sees your record and never decides the outcome.</p>
        <p class="small muted">Rules then check ${esc(p.name.split(' ')[0])}'s record against quoted university policy, and anything the sources don't answer is marked <em>Not verified</em>.</p>
        <p class="small muted"><strong>Don't include sensitive personal information in your question.</strong></p>
      </aside>
    </div>`, 2, !S.busy);
  $('question').addEventListener('input', e => S.question = e.target.value);
  $('main').querySelectorAll('.chip').forEach(c => c.addEventListener('click', () => { S.question = c.textContent; $('question').value = S.question; $('question').focus(); }));
  $('analyze').addEventListener('click', () => analyze(p, task));
}
async function analyze(p, task) {
  if (S.busy) return;
  if (S.question.trim().length < 3) { S.error = 'Please describe your goal in 3 to 1,000 characters.'; return viewAsk(p, task); }
  Object.assign(S, {busy: true, error: '', sid: null, result: null, receipt: null});
  viewAsk(p, task);
  try {
    const d = await api('/api/start', {message: S.question, student_id: p.id, term: S.term});
    Object.assign(S, {receipt: null, resultTerm: d.term, sid: d.session_id, result: d.result, intent: d.intent, entities: d.entities || {}, interpretation: d.interpretation, usage: d.model_usage});
    $('failure').value = 'none';
    S.busy = false;
    go(`#/s/${p.id}/result`);
  } catch (e) {
    S.busy = false; S.error = e.message; viewAsk(p, task);
  }
}

// ---- Step 4: adaptive page ---------------------------------------------------
function heading() {
  if (S.intent === 'drop') return S.entities.course_code ? `Dropping ${S.entities.course_code}` : 'Dropping a course';
  if (S.intent === 'course_info') return S.entities.course_code || 'Course details';
  if (S.intent === 'course_search') return `Courses for ${S.resultTerm}`;
  return {graduation: 'Your graduation requirements', hold: 'Your registration holds',
    policy: 'University policies and deadlines'}[S.intent] || 'We couldn’t match that request';
}
function coursesTable(r) {
  if (!r.courses) return '';
  const shown = r.courses.slice(0, 150);
  return `<section class="group"><h3>Courses</h3>${shown.length ? `<div class="table-wrap"><table>
    <thead><tr><th>Course</th><th>Title</th><th>Hours</th><th>Your record</th></tr></thead><tbody>
    ${shown.map(c => `<tr><td><strong>${esc(c.code)}</strong></td><td>${esc(c.title)}${c.prerequisite ? `<div class="muted small">Prerequisite: ${esc(c.prerequisite)}</div>` : ''}</td>
      <td>${esc(c.credits || '—')}</td><td>${c.record ? `<span class="badge">${esc(c.record)}</span>` : '<span class="badge ok">Available</span>'}</td></tr>`).join('')}
    </tbody></table></div>${r.courses.length > shown.length ? `<p class="muted small">Showing ${shown.length} of ${r.courses.length}. Add a subject, level or topic to narrow the list.</p>` : ''}`
    : '<p class="muted">No courses match. Try fewer filters or another term.</p>'}</section>`;
}
function viewResult(p) {
  const r = S.result;
  if (!r) return go(`#/s/${p.id}`, true);
  // Number sources in the order the checks cite them; ones used only for the figures go last.
  const order = [...new Set((r.checks || []).flatMap(c => c.cites || []))];
  const sources = [...(r.sources || [])].sort((a, b) =>
    (order.includes(a.key) ? order.indexOf(a.key) : order.length) - (order.includes(b.key) ? order.indexOf(b.key) : order.length));
  const srcIndex = Object.fromEntries(sources.map((s, i) => [s.key, i + 1]));
  const status = r.status === 'ready'
    ? ['ok', 'You can review and confirm this request.']
    : r.status === 'info' ? ['info', 'Here’s what the sources say.'] : ['block', `This action isn’t available. ${r.reason || ''}`];
  const checkHtml = c => {
    const [lbl, cls] = LEVEL[c.level] || LEVEL.info;
    const refs = (c.cites || []).map(k => srcIndex[k]).filter(Boolean);
    return `<article class="check ${c.level}"><h4>${esc(c.title)} <span class="badge ${cls}">${esc(lbl)}</span></h4><p>${esc(c.text)}</p>
      ${refs.length ? `<div class="refs">Source ${refs.map(n => `<button type="button" class="linklike" data-src="${n}" aria-label="Show source ${n}">[${n}]</button>`).join('')}</div>` : ''}</article>`;
  };
  const groups = GROUPS.map(([title, test]) => [title, (r.checks || []).filter(test)]).filter(([, cs]) => cs.length);
  render(`
    ${crumbs(['Students', '#/'], [p.name, `#/s/${p.id}`], [TASKS[S.task]?.title || 'Request', `#/s/${p.id}/ask/${S.task}`], ['Your page'])}
    <div class="page-head"><div><h1 tabindex="-1">${esc(heading())}</h1><p>${esc(r.summary)}</p></div>
      <a class="btn secondary" href="#/s/${esc(p.id)}/ask/${esc(S.task)}">Change my question</a></div>
    <div class="interpretation"><span class="badge accent">AI interpretation</span> ${esc(S.interpretation)}
      <span class="badge">term: ${esc(S.resultTerm || S.term)}</span><span class="badge">intent: ${esc(S.intent)}</span>${S.entities.course_code ? `<span class="badge">course: ${esc(S.entities.course_code)}</span>` : ''}
      ${S.usage ? `<span>· ${esc(S.usage.model)}</span>` : ''}</div>
    <div class="alert ${status[0]}" role="status"><strong>${esc(status[1])}</strong></div>
    <div class="grid two">
      <div>
        ${(r.metrics || []).length ? `<div class="metrics">${r.metrics.map(m => `<div class="metric${String(m.value).length > 14 ? ' long' : ''}"><strong>${esc(m.value)}</strong><span>${esc(m.label)}</span></div>`).join('')}</div>` : ''}
        ${coursesTable(r)}
        ${groups.map(([title, cs]) => `<section class="group"><h3>${esc(title)}</h3>${cs.map(checkHtml).join('')}</section>`).join('')}
        ${S.receipt ? `<div class="alert ok" style="margin-top:22px"><strong>Already confirmed.</strong> Receipt <code>${esc(S.receipt)}</code>.</div>
          <div class="actions"><a class="btn secondary" href="#/s/${esc(p.id)}">Back to dashboard</a></div>` : r.status === 'ready' ? `
          <section class="confirm-box" style="margin-top:22px"><h2>Confirm</h2>
            <p>${esc(r.action)}</p>
            <label><input type="checkbox" id="ack"> <span>I reviewed the information, consequences and sources above, and I authorize this request.</span></label>
            <div class="actions"><button type="button" class="btn primary" id="confirm" disabled>Confirm request</button>
              <a class="btn secondary" href="#/s/${esc(p.id)}">Not now</a></div>
          </section>` : `<div class="actions"><a class="btn secondary" href="#/s/${esc(p.id)}">Back to dashboard</a></div>`}
        ${S.error ? `<div class="alert block" role="alert" style="margin-top:14px">${esc(S.error)}</div>` : ''}
      </div>
      <aside>
        <section class="card"><h2>Sources</h2>
          ${sources.length ? sources.map((s, i) => `<div class="source" id="src-${i + 1}"><strong>[${i + 1}] ${esc(s.title)}</strong>
            <div class="meta">${esc(s.publisher)} · page ${esc(s.page)} · retrieved ${esc(s.retrieved)}</div>
            ${s.url ? `<div class="meta"><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url)}</a></div>` : ''}
            <details><summary class="small">Quoted text</summary><blockquote>${esc(s.quote)}</blockquote></details></div>`).join('')
            : '<p class="muted small">No university source applies to this result.</p>'}
        </section>
        <section class="card profile"><h3>${esc(p.name)}</h3>
          <p class="small muted">${esc(p.program_name)} · ${esc(p.visa || 'Domestic')} · ${esc(p.term_credits)} hours in ${esc(p.term)}</p></section>
      </aside>
    </div>`, 3);
  $('main').querySelectorAll('[data-src]').forEach(a => a.addEventListener('click', () => {
    const el = $(`src-${a.dataset.src}`); el.querySelector('details').open = true; el.scrollIntoView({behavior: 'smooth', block: 'center'});
  }));
  const ack = $('ack');
  if (ack) {
    ack.addEventListener('change', () => $('confirm').disabled = !ack.checked);
    $('confirm').addEventListener('click', () => confirmAction(p));
  }
}
async function confirmAction(p) {
  $('confirm').disabled = true;
  try {
    const d = await api('/api/confirm', {session_id: S.sid, confirmation: true});
    S.receipt = d.receipt; S.action = d.description; S.error = '';
    S.profile = null;  // reload so My requests and the schedule show this request
    go(`#/s/${p.id}/done`);
  } catch (e) { S.error = e.message; viewResult(p); }
}
async function applyFault(mode) {
  if (!S.sid || !location.hash.endsWith('/result')) { notify('Build a page first, then inject a failure.'); $('failure').value = 'none'; return; }
  try {
    const d = await api('/api/fault', {session_id: S.sid, mode});
    S.result = d.result; S.error = ''; viewResult(S.profile);
  } catch (e) { notify(e.message); $('failure').value = 'none'; }
}

// ---- Step 5: receipt ---------------------------------------------------------
function viewDone(p) {
  if (!S.receipt) return go(`#/s/${p.id}`, true);
  render(`
    ${crumbs(['Students', '#/'], [p.name, `#/s/${p.id}`], ['Confirmation'])}
    <section class="card receipt"><div class="tick" aria-hidden="true">✓</div>
      <h1 tabindex="-1">Request recorded</h1>
      <p>${esc(S.action)}</p>
      <p>Receipt <code>${esc(S.receipt)}</code></p>
      <div class="alert info" style="text-align:left">Keep this receipt number for your records.</div>
      <div class="actions" style="justify-content:center"><a class="btn primary" href="#/s/${esc(p.id)}">Back to dashboard</a>
        <a class="btn secondary" href="#/">Choose another student</a></div>
    </section>`, 5);
}

// ---- Policy sources page -----------------------------------------------------
function viewSources() {
  const data = S.sourcesData;
  render(`
    ${crumbs(['Students', '#/'], ['Policy sources'])}
    <div class="page-head"><div><h1 tabindex="-1">Policy sources</h1>
      <p>Every university rule this portal uses, with the exact quoted text and where it comes from.</p></div></div>
    ${data ? `<section class="card">${data.facts.map(f => `<div class="source"><strong>${esc(f.title)}</strong>
      <div class="meta">${esc(f.publisher)} · page ${esc(f.page)} · retrieved ${esc(f.retrieved)}${f.url ? ` · <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.url)}</a>` : ''}</div>
      <blockquote>${esc(f.quote)}</blockquote></div>`).join('')}</section>
    <section class="card"><h2>Degree programs</h2>${data.programs.map(pr => `<div class="source"><strong>${esc(pr.name)}</strong>
      <div class="meta">Academic Catalog ${esc(pr.catalog)} · pages ${esc(pr.pages)} · ${pr.audit_supported ? 'degree check available' : 'degree check not available online yet'}</div>
      ${pr.summary ? `<p class="small" style="margin:6px 0 0">${esc(pr.summary)}</p>` : ''}
      ${!pr.audit_supported && pr.required ? `<p class="small muted" style="margin:4px 0 0">Required: ${pr.required.map(q => esc(q.label)).join(', ')}</p>` : ''}</div>`).join('')}</section>
    <section class="card"><h2>Class schedules</h2>
      <p class="muted small">Courses offered each term, from Course Explorer.</p>
      ${Object.entries(data.schedules).map(([term, subjects]) => `<h3 style="margin-top:14px">${esc(term)}</h3>
        ${Object.entries(subjects).map(([subj, v]) => `<details class="source"><summary><strong>${esc(subj)}</strong> · ${v.courses.length} courses
          <span class="meta">· retrieved ${esc(v.retrieved)}</span></summary>
          <div class="meta"><a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(v.url)}</a></div>
          <table style="margin-top:8px"><tbody>${v.courses.map(c => `<tr><td style="width:90px"><strong>${esc(c)}</strong></td><td>${esc(v.titles?.[c] || '')}</td></tr>`).join('')}</tbody></table></details>`).join('')}`).join('')}
    </section>` : '<p class="muted">Loading…</p>'}`, 0);
}

// ---- Router ------------------------------------------------------------------
function go(hash, replace = false) {
  if (replace) { history.replaceState(null, '', hash); route(); } else location.hash = hash;
}
async function route() {
  const hash = location.hash || '#/';
  const m = hash.match(/^#\/s\/(S\d{5})(?:\/(ask)\/(\w+)|\/(result|done))?$/);
  try {
    if (hash === '#/sources') return viewSources();
    if (!m) return viewHome();
    const p = await loadProfile(m[1]);
    if (m[2]) return viewAsk(p, m[3]);
    if (m[4] === 'result') return viewResult(p);
    if (m[4] === 'done') return viewDone(p);
    S.error = '';
    return viewDashboard(p);
  } catch (e) {
    notify(e.message || 'Something went wrong.');
    if (hash !== '#/') go('#/', true);
  }
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  $('theme').setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
  try { localStorage.setItem('idna-theme', theme); } catch {}
}
$('theme').addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme === 'dark' ||
    (!document.documentElement.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches);
  setTheme(dark ? 'light' : 'dark');
});
try { const t = localStorage.getItem('idna-theme'); if (t) setTheme(t); } catch {}
$('failure').addEventListener('change', e => applyFault(e.target.value));
$('term').addEventListener('change', e => setTerm(e.target.value).catch(err => notify(err.message)));
document.addEventListener('click', e => { if (e.target.id === 'switch') { S.profile = null; go('#/'); } });
window.addEventListener('hashchange', route);

(async () => {
  try {
    const [terms, health, sources] = await Promise.all([api('/api/terms'), api('/health'), api('/api/sources')]);
    let saved = null;
    try { saved = localStorage.getItem('idna-term'); } catch {}
    Object.assign(S, {terms: terms.terms, current: terms.current, rulesDate: health.rules_date, sourcesData: sources,
      term: terms.terms.some(t => t.term === saved) ? saved : terms.current});
    fillTerms();
    S.students = await api(`/api/students?term=${encodeURIComponent(S.term)}`);
    $('today').textContent = `Today: ${longDate(health.rules_date)}`;
  } catch { notify('Could not reach the server.'); }
  route();
})();
