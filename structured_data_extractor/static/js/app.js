'use strict';

// ── DOM refs ──────────────────────────────────────────────────────────────────
const dropZone       = document.getElementById('dropZone');
const fileInput      = document.getElementById('fileInput');
const fileChosen     = document.getElementById('fileChosen');
const fileNameEl     = document.getElementById('fileName');
const fileSizeEl     = document.getElementById('fileSize');
const fileRemove     = document.getElementById('fileRemove');
const btnExtract     = document.getElementById('btnExtract');
const btnSample      = document.getElementById('btnSample');
const errorBox       = document.getElementById('errorBox');
const errorMsg       = document.getElementById('errorMsg');
const pageLanding    = document.getElementById('pageLanding');
const pageResults    = document.getElementById('pageResults');
const landingLinks   = document.getElementById('landingLinks');
const resultsNav     = document.getElementById('resultsNav');
const btnNewResume   = document.getElementById('btnNewResume');
const fileInputB     = document.getElementById('fileInputB');
const compareBLabel  = document.getElementById('compareBLabel');
const compareLoading = document.getElementById('compareLoading');
const compareGrid    = document.getElementById('compareGrid');
const compareNameA   = document.getElementById('compareNameA');
const btnDownload    = document.getElementById('btnDownload');
const btnPrint       = document.getElementById('btnPrint');

let selectedFile = null;
let lastResult   = null;
let lastAts      = null;
let lastSource   = '';

// ── Skill category map ────────────────────────────────────────────────────────
const SKILL_CATS = {
  language: ['Python','Java','C++','C#','C','JavaScript','TypeScript','Go','Rust','Ruby','PHP','Swift','Kotlin','Scala','R','MATLAB','Perl','Bash','Shell','PowerShell','Objective-C','Dart','Lua'],
  web:      ['HTML','CSS','React','Angular','Vue','Vue.js','Next.js','Nuxt.js','Node.js','Express','Django','Flask','FastAPI','Spring Boot','Laravel','Rails','ASP.NET','GraphQL','REST APIs','WebSockets','Tailwind CSS','Bootstrap','jQuery','Webpack','Vite','Svelte'],
  data:     ['Machine Learning','Deep Learning','Natural Language Processing','NLP','Computer Vision','Reinforcement Learning','Data Science','Data Analysis','Data Engineering','Data Visualization','Pandas','NumPy','Scikit-learn','TensorFlow','PyTorch','Keras','Hugging Face','OpenCV','NLTK','spaCy','XGBoost','LightGBM','Spark','PySpark','Hadoop','Kafka','Airflow','dbt','LangChain','LlamaIndex','Streamlit','Tableau','Power BI','Looker','Matplotlib','Seaborn','Plotly'],
  cloud:    ['AWS','Azure','GCP','Google Cloud','Docker','Kubernetes','Terraform','Ansible','Jenkins','GitHub Actions','CI/CD','Linux','Nginx','Helm','Prometheus','Grafana','Elasticsearch'],
  database: ['SQL','MySQL','PostgreSQL','SQLite','MongoDB','Redis','Cassandra','DynamoDB','Oracle','MS SQL','BigQuery','Snowflake','Firebase'],
  tool:     ['Git','GitHub','GitLab','Jira','Confluence','Figma','Postman','VS Code','IntelliJ','Eclipse'],
  soft:     ['Communication','Problem Solving','Team Leadership','Agile','Scrum','Project Management','Critical Thinking','Public Speaking'],
};
const CAT_LABELS = { language:'Languages', web:'Web / Frameworks', data:'Data & ML', cloud:'Cloud & DevOps', database:'Databases', tool:'Tools', soft:'Soft Skills' };
const CAT_COLORS = { language:'#8b5cf6', web:'#10b981', data:'#f59e0b', cloud:'#0ea5e9', database:'#a855f7', tool:'#94a3b8', soft:'#eab308' };

function skillCategory(s) {
  const sl = s.toLowerCase();
  for (const [cat, list] of Object.entries(SKILL_CATS))
    if (list.some(k => k.toLowerCase() === sl)) return cat;
  return 'tool';
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatBytes(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1048576).toFixed(1) + ' MB';
}
function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function showError(msg) {
  if (!msg || !msg.trim()) return;
  errorMsg.textContent = msg;
  errorBox.hidden = false;
}
function hideError() { errorBox.hidden = true; }

// ── File handling ─────────────────────────────────────────────────────────────
function selectFile(file) {
  if (!file) return;
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['pdf','docx','txt'].includes(ext)) {
    showError('Unsupported file type. Please upload a PDF, DOCX or TXT file.');
    return;
  }
  hideError();
  selectedFile           = file;
  fileNameEl.textContent = file.name;
  fileSizeEl.textContent = formatBytes(file.size);
  dropZone.hidden        = true;
  fileChosen.hidden      = false;
}
function clearFile() {
  selectedFile = null; fileInput.value = '';
  dropZone.hidden = false; fileChosen.hidden = true;
  hideError();
}

fileInput.addEventListener('change', () => {
  if (fileInput.files && fileInput.files.length) selectFile(fileInput.files[0]);
});
fileRemove.addEventListener('click', e => { e.stopPropagation(); clearFile(); });
dropZone.addEventListener('click', e => {
  if (e.target.tagName === 'LABEL' || e.target.closest('label')) return;
  fileInput.click();
});
dropZone.addEventListener('dragover',  e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', e => { if (!dropZone.contains(e.relatedTarget)) dropZone.classList.remove('drag-over'); });
dropZone.addEventListener('drop', e => {
  e.preventDefault(); dropZone.classList.remove('drag-over');
  const f = e.dataTransfer.files && e.dataTransfer.files[0];
  if (f) selectFile(f);
});

// ── Loading ───────────────────────────────────────────────────────────────────
function setLoading(on) {
  btnExtract.disabled = on; btnSample.disabled = on;
  btnExtract.querySelector('.btn-label').hidden   =  on;
  btnExtract.querySelector('.btn-spinner').hidden = !on;
}

// ── API — now uses the combined /api/ats-check endpoint ───────────────────────
async function apiExtractFile(file) {
  const fd = new FormData();
  fd.append('file', file, file.name);
  const r = await fetch('/api/ats-check', { method: 'POST', body: fd });
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || `Server error ${r.status}`);
  return d; // { resume, ats }
}
async function apiExtractSample() {
  const r = await fetch('/api/ats-check/sample', { method: 'POST' });
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || 'Server error');
  return d; // { resume, ats }
}
// For compare we still use just extract
async function apiExtractFileOnly(file) {
  const fd = new FormData();
  fd.append('file', file, file.name);
  const r = await fetch('/api/extract', { method: 'POST', body: fd });
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || `Server error ${r.status}`);
  return d;
}

// ── Extract ───────────────────────────────────────────────────────────────────
btnExtract.addEventListener('click', async () => {
  hideError();
  if (!selectedFile) { showError('Please select a resume file first, or click "Try demo resume".'); return; }
  setLoading(true);
  try {
    const { resume, ats } = await apiExtractFile(selectedFile);
    lastSource = selectedFile.name;
    renderResults(resume, ats, lastSource);
  } catch(err) { showError(err.message || 'Extraction failed. Please try again.'); }
  finally { setLoading(false); }
});

btnSample.addEventListener('click', async () => {
  hideError(); setLoading(true);
  try {
    const { resume, ats } = await apiExtractSample();
    lastSource = 'Built-in sample resume';
    renderResults(resume, ats, lastSource);
  } catch(err) { showError(err.message || 'Failed to load sample.'); }
  finally { setLoading(false); }
});

// ── Score (overview ring) ─────────────────────────────────────────────────────
function calcScore(data) {
  const c = data.contact || {};
  const dims = [
    { label:'Contact',    max:20, val:([!!c.full_name,!!c.email,!!c.phone,!!c.location].filter(Boolean).length/4)*20 },
    { label:'Summary',    max:10, val:data.summary ? 10 : 0 },
    { label:'Skills',     max:25, val:Math.min(data.skills.length/10,1)*25 },
    { label:'Experience', max:25, val:Math.min(data.experience.length/2,1)*25 },
    { label:'Education',  max:15, val:Math.min(data.education.length,1)*15 },
    { label:'ATS check',  max:5,  val:data.validation && data.validation.is_valid ? 5 : 0 },
  ];
  return { total: Math.round(dims.reduce((s,d) => s+d.val, 0)), dims };
}
function gradeFromScore(n) {
  if (n >= 85) return { label:'Excellent', cls:'grade-excellent' };
  if (n >= 65) return { label:'Good',      cls:'grade-good'      };
  if (n >= 45) return { label:'Fair',      cls:'grade-fair'      };
  return              { label:'Weak',      cls:'grade-weak'      };
}

// ── Render results ─────────────────────────────────────────────────────────────
function renderResults(data, ats, source) {
  lastResult = data;
  lastAts    = ats;
  const contact = data.contact || {};

  pageLanding.hidden  = true;
  pageResults.hidden  = false;
  landingLinks.hidden = true;
  resultsNav.hidden   = false;
  btnNewResume.hidden = false;

  // Source banner
  document.getElementById('sourceBanner').innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
    Extraction complete &nbsp;·&nbsp; <strong>${esc(source)}</strong>`;

  // Overview header
  document.getElementById('ovHeadName').textContent = contact.full_name || 'Candidate';
  document.getElementById('ovHeadSub').textContent  = [contact.email, contact.location].filter(Boolean).join(' · ') || '—';

  // Score ring (r=42, circ≈264)
  const { total, dims } = calcScore(data);
  const grade  = gradeFromScore(total);
  const circ   = 264;
  const scoreColor = total >= 85 ? '#10b981' : total >= 65 ? '#4f46e5' : total >= 45 ? '#f59e0b' : '#ef4444';
  const ring   = document.getElementById('ringFill');
  ring.style.stroke = scoreColor;
  ring.style.strokeDashoffset = circ;
  setTimeout(() => { ring.style.strokeDashoffset = circ - (total/100)*circ; }, 80);
  document.getElementById('scoreNum').textContent = total;
  const gradeEl = document.getElementById('scoreGrade');
  gradeEl.textContent = grade.label; gradeEl.className = `score-grade ${grade.cls}`;

  // Score dims
  document.getElementById('scoreDims').innerHTML =
    `<div class="info-label" style="margin-bottom:12px">Score breakdown</div>` +
    dims.map(d => {
      const pct = Math.round((d.val/d.max)*100);
      return `<div class="sb-row"><span class="sb-label">${esc(d.label)}</span>
        <div class="sb-bar-wrap"><div class="sb-bar" style="width:${pct}%;background:${scoreColor}"></div></div>
        <span class="sb-pts">${Math.round(d.val)}</span></div>`;
    }).join('');

  // Contact
  document.getElementById('ovName').textContent     = contact.full_name || '—';
  document.getElementById('ovEmail').textContent    = contact.email     || '—';
  document.getElementById('ovPhone').textContent    = contact.phone     || '—';
  document.getElementById('ovLocation').textContent = contact.location  || '—';
  const summaryBlock = document.getElementById('ovSummary');
  if (data.summary) { document.getElementById('ovSummaryText').textContent = data.summary; summaryBlock.hidden = false; }
  else              { summaryBlock.hidden = true; }

  // Skills, Experience, Education
  renderSkills(data.skills);

  document.getElementById('expTimeline').innerHTML = data.experience.length
    ? data.experience.map(e => `
        <div class="exp-item">
          <div class="exp-role">${esc(e.job_title||'Role not specified')}</div>
          <div class="exp-company">${esc(e.company||'Company not specified')}</div>
          ${(e.start_date||e.end_date)?`<div class="exp-dates">${esc(e.start_date||'—')} → ${esc(e.end_date||'Present')}</div>`:''}
          ${e.description?`<div class="exp-desc">${esc(e.description)}</div>`:''}
        </div>`).join('')
    : '<p style="color:var(--ink-muted)">No experience entries detected.</p>';

  document.getElementById('eduList').innerHTML = data.education.length
    ? data.education.map(e => `
        <div class="edu-item">
          <div class="edu-icon">🎓</div>
          <div>
            <div class="edu-degree">${esc(e.degree||'Degree not specified')}</div>
            <div class="edu-inst">${esc(e.institution||'Institution not specified')}</div>
            ${e.graduation_year?`<div class="edu-year">Class of ${esc(e.graduation_year)}</div>`:''}
          </div>
        </div>`).join('')
    : '<p style="color:var(--ink-muted)">No education entries detected.</p>';

  // ATS check
  renderAts(ats);

  // Compare
  compareNameA.textContent = source;

  goToPage('overview');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Skills rendering ──────────────────────────────────────────────────────────
function renderSkills(skills) {
  const counts = {};
  for (const cat of Object.keys(SKILL_CATS)) counts[cat] = 0;
  skills.forEach(s => { counts[skillCategory(s)]++; });
  const maxCount = Math.max(...Object.values(counts), 1);

  const catsHtml = Object.entries(counts).filter(([,n])=>n>0).sort(([,a],[,b])=>b-a)
    .map(([cat,n]) => {
      const pct = Math.round((n/maxCount)*100);
      return `<div class="skill-cat-row">
        <span class="skill-cat-name">${esc(CAT_LABELS[cat])}</span>
        <div class="skill-cat-bar-wrap"><div class="skill-cat-bar" style="width:${pct}%;background:${CAT_COLORS[cat]}"></div></div>
        <span class="skill-cat-count">${n}</span>
      </div>`;
    }).join('');

  document.getElementById('skillCategories').innerHTML =
    catsHtml ? `<div class="info-label" style="margin-bottom:12px">By category</div>${catsHtml}` : '';
  document.getElementById('skillsWrap').innerHTML = skills.length
    ? skills.map(s=>`<span class="skill-chip cat-${skillCategory(s)}">${esc(s)}</span>`).join('')
    : '<p style="color:var(--ink-muted)">No skills detected.</p>';
}

// ── ATS rendering ─────────────────────────────────────────────────────────────
function renderAts(ats) {
  if (!ats) return;

  // Score ring (r=40, circ≈251)
  const atsCirc  = 251;
  const atsRing  = document.getElementById('atsRingFill');
  const atsColor = ats.overall_color === 'green' ? '#059669'
                 : ats.overall_color === 'amber' ? '#d97706' : '#dc2626';
  atsRing.style.stroke = atsColor;
  atsRing.style.strokeDashoffset = atsCirc;
  setTimeout(() => { atsRing.style.strokeDashoffset = atsCirc - (ats.percent/100)*atsCirc; }, 120);

  document.getElementById('atsPct').textContent = ats.percent + '%';

  const overallEl = document.getElementById('atsOverall');
  overallEl.textContent = ats.overall;
  overallEl.className   = `ats-overall ${ats.overall_color}`;

  document.getElementById('atsStats').innerHTML =
    `<span class="ats-stat-pass">✓ ${ats.passes} passed</span>
     <span class="ats-stat-warn">⚠ ${ats.warns} warnings</span>
     <span class="ats-stat-fail">✕ ${ats.fails} failed</span>`;

  // Top quick-fix tips: first suggestion from each failing check
  const fails = ats.categories.flatMap(c => c.checks)
    .filter(c => c.status !== 'pass' && c.suggestions.length > 0)
    .slice(0, 4);
  document.getElementById('atsTopTips').innerHTML = fails.length
    ? `<div class="ats-top-tips-title">Quick wins</div>` +
      fails.map(c => `<div class="ats-tip-quick">${esc(c.suggestions[0])}</div>`).join('')
    : `<div class="ats-top-tips-title">All checks passed 🎉</div>`;

  // Category sections
  const statusIcon = { pass: '✓', warn: '⚠', fail: '✕' };
  const iconCls    = { pass: 'icon-pass', warn: 'icon-warn', fail: 'icon-fail' };
  const ptsCls     = { pass: 'pts-pass',  warn: 'pts-warn',  fail: 'pts-fail'  };

  document.getElementById('atsCategoryList').innerHTML = ats.categories.map(cat => {
    const catScore = cat.checks.reduce((s,c) => s+c.score, 0);
    const catMax   = cat.checks.reduce((s,c) => s+c.max_score, 0);

    return `<div class="ats-category">
      <div class="ats-cat-title">
        ${esc(cat.name)}
        <span class="ats-cat-score">${catScore}/${catMax}</span>
      </div>
      ${cat.checks.map(c => `
        <div class="ats-check" data-id="${esc(c.id)}">
          <div class="ats-check-header">
            <div class="ats-check-icon ${iconCls[c.status]}">${statusIcon[c.status]}</div>
            <div class="ats-check-title">${esc(c.title)}</div>
            <div class="ats-check-msg">${esc(c.message)}</div>
            <span class="ats-check-pts ${ptsCls[c.status]}">${c.score}/${c.max_score}</span>
            ${c.suggestions.length ? '<span class="ats-chevron">›</span>' : ''}
          </div>
          ${c.suggestions.length ? `
            <div class="ats-check-body">
              <ul class="ats-suggestion-list">
                ${c.suggestions.map(s => `<li>${esc(s)}</li>`).join('')}
              </ul>
            </div>` : ''}
        </div>`).join('')}
    </div>`;
  }).join('');

  // Toggle expand/collapse on check cards
  document.querySelectorAll('.ats-check-header').forEach(hdr => {
    hdr.addEventListener('click', () => {
      const card = hdr.closest('.ats-check');
      if (card.querySelector('.ats-check-body')) card.classList.toggle('open');
    });
  });

  // Auto-open failing checks
  document.querySelectorAll('.ats-check').forEach(card => {
    const icon = card.querySelector('.ats-check-icon');
    if (icon && (icon.classList.contains('icon-fail') || icon.classList.contains('icon-warn'))) {
      card.classList.add('open');
    }
  });
}

// ── Page navigation ───────────────────────────────────────────────────────────
const PAGES = ['overview','skills','experience','education','ats','compare'];

function goToPage(name) {
  PAGES.forEach(p => {
    const el = document.getElementById(`rpage-${p}`);
    if (el) el.hidden = p !== name;
  });
  document.querySelectorAll('.rnav-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.page === name)
  );
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

document.querySelectorAll('.rnav-btn').forEach(btn =>
  btn.addEventListener('click', () => goToPage(btn.dataset.page))
);

document.getElementById('pageResults').addEventListener('click', e => {
  const btn = e.target.closest('[data-page]');
  if (btn && (btn.classList.contains('btn-next') || btn.classList.contains('btn-prev'))) {
    goToPage(btn.dataset.page);
  }
});

// ── New resume ────────────────────────────────────────────────────────────────
btnNewResume.addEventListener('click', () => {
  clearFile();
  pageLanding.hidden = false; pageResults.hidden = true;
  landingLinks.hidden = false; resultsNav.hidden = true;
  btnNewResume.hidden = true;
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ── Print ─────────────────────────────────────────────────────────────────────
btnPrint.addEventListener('click', () => {
  PAGES.forEach(p => { const el = document.getElementById(`rpage-${p}`); if (el) el.hidden = false; });
  window.print();
  setTimeout(() => goToPage('overview'), 600);
});

// ── Download JSON ─────────────────────────────────────────────────────────────
btnDownload.addEventListener('click', () => {
  if (!lastResult) return;
  const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: 'application/json' });
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), { href: url, download: 'resume_extracted.json' });
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
});

// ── Compare ───────────────────────────────────────────────────────────────────
fileInputB.addEventListener('change', async () => {
  if (!fileInputB.files || !fileInputB.files.length) return;
  const file = fileInputB.files[0];
  compareBLabel.textContent = file.name;
  compareLoading.hidden = false; compareGrid.hidden = true;
  try {
    const dataB = await apiExtractFileOnly(file);
    renderCompare(lastResult, lastSource, dataB, file.name);
  } catch(err) {
    compareLoading.hidden = true;
    showError('Compare error: ' + err.message);
  }
});

function renderCompare(dataA, srcA, dataB, srcB) {
  compareLoading.hidden = true;
  const scoreA = calcScore(dataA).total, scoreB = calcScore(dataB).total;
  const skA = new Set(dataA.skills.map(s=>s.toLowerCase()));
  const skB = new Set(dataB.skills.map(s=>s.toLowerCase()));

  function col(data, src, score, otherScore, mySet, otherSet) {
    const won = score >= otherScore, c = data.contact || {};
    const shared = data.skills.filter(s => otherSet.has(s.toLowerCase()));
    const unique = data.skills.filter(s => !otherSet.has(s.toLowerCase()));
    return `<div class="compare-col">
      <h3>${esc(src)} <span class="compare-score-badge ${won?'compare-win':'compare-lose'}">${score}/100</span></h3>
      <div class="compare-section">
        <div class="compare-section-title">Contact</div>
        ${[['Name',c.full_name],['Email',c.email],['Phone',c.phone],['Location',c.location]]
          .map(([l,v])=>`<div class="compare-stat-row"><span class="compare-stat-label">${esc(l)}</span><span class="compare-stat-val">${esc(v)||'—'}</span></div>`).join('')}
      </div>
      <div class="compare-section">
        <div class="compare-section-title">By the numbers</div>
        ${[['Skills',data.skills.length],['Experience',data.experience.length+' role'+(data.experience.length!==1?'s':'')],['Education',data.education.length+' degree'+(data.education.length!==1?'s':'')]]
          .map(([l,v])=>`<div class="compare-stat-row"><span class="compare-stat-label">${esc(l)}</span><span class="compare-stat-val">${esc(String(v))}</span></div>`).join('')}
      </div>
      <div class="compare-section">
        <div class="compare-section-title">Shared skills (${shared.length})</div>
        ${shared.length?shared.map(s=>`<span class="compare-skill-chip shared">${esc(s)}</span>`).join(''):'<span style="color:var(--ink-muted);font-size:13px">None</span>'}
      </div>
      <div class="compare-section">
        <div class="compare-section-title">Unique skills (${unique.length})</div>
        ${unique.length?unique.map(s=>`<span class="compare-skill-chip unique">${esc(s)}</span>`).join(''):'<span style="color:var(--ink-muted);font-size:13px">None</span>'}
      </div>
    </div>`;
  }
  compareGrid.innerHTML = col(dataA,srcA,scoreA,scoreB,skA,skB) + col(dataB,srcB,scoreB,scoreA,skB,skA);
  compareGrid.hidden = false;
}
