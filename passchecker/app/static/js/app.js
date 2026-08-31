// ============================================================
// PassStrength AI – Frontend Application (v2)
// ============================================================

const $ = id => document.getElementById(id);

// DOM refs
const passwordInput   = $('password-input');
const analyzeBtn      = $('analyze-btn');
const toggleVisBtn    = $('toggle-visibility');
const themeSwitch     = $('theme-switch');
const quickMeter      = $('quick-meter');

// Chart.js instance
let entropyChart = null;

// ── Debounce ──────────────────────────────────────────────
function debounce(fn, ms) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// ── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    updateRangeTrack();

    passwordInput.addEventListener('input', debounce(() => {
        if (passwordInput.value) analyzePassword(passwordInput.value);
        else resetUI();
    }, 320));

    analyzeBtn.addEventListener('click', () => {
        if (passwordInput.value) analyzePassword(passwordInput.value);
    });

    toggleVisBtn.addEventListener('click', togglePasswordVisibility);
    themeSwitch.addEventListener('change', toggleDarkMode);

    $('generate-btn').addEventListener('click', generatePassword);
    $('copy-btn').addEventListener('click', () => {
        const pwd = $('generated-password').textContent.trim();
        if (pwd && pwd !== 'Click Generate →') copyToClipboard(pwd);
    });

    const genLen = $('gen-length');
    genLen.addEventListener('input', () => {
        $('gen-length-val').textContent = genLen.value;
        updateRangeTrack();
    });
});

function updateRangeTrack() {
    const el = $('gen-length');
    const pct = ((el.value - el.min) / (el.max - el.min)) * 100;
    el.style.background = `linear-gradient(to right, var(--cyan) ${pct}%, rgba(255,255,255,0.1) ${pct}%)`;
}

// ── Chart.js ──────────────────────────────────────────────
function initChart() {
    const ctx = $('entropy-chart').getContext('2d');
    Chart.defaults.color = '#6b7db3';
    Chart.defaults.font.family = "'Inter', sans-serif";

    entropyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Shannon', 'Search Space'],
            datasets: [{
                data: [0, 0],
                backgroundColor: ['rgba(0,212,255,0.25)', 'rgba(0,255,136,0.25)'],
                borderColor:     ['#00d4ff', '#00ff88'],
                borderWidth: 1.5,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { font: { size: 11 } } },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { font: { size: 11 } }
                }
            },
            animation: { duration: 600, easing: 'easeOutQuart' }
        }
    });
}

// ── API: Analyze ──────────────────────────────────────────
async function analyzePassword(password) {
    setLoading(true);
    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        renderAll(data);
    } catch (err) {
        console.error('Analysis error:', err);
        showFeedbackError('Could not reach server. Is it running?');
    } finally {
        setLoading(false);
    }
}

// ── API: Generate ─────────────────────────────────────────
async function generatePassword() {
    const length    = parseInt($('gen-length').value);
    const uppercase = $('gen-uppercase').checked;
    const lowercase = $('gen-lowercase').checked;
    const digits    = $('gen-digits').checked;
    const symbols   = $('gen-symbols').checked;
    const excludeAmbiguous = $('gen-exclude-ambiguous').checked;

    if (!uppercase && !lowercase && !digits && !symbols) {
        $('generated-password').textContent = 'Select at least one character type.';
        return;
    }

    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ length, uppercase, lowercase, digits, symbols, exclude_ambiguous: excludeAmbiguous })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        const box = $('generated-password');
        box.textContent = data.password;
        box.classList.add('has-password');

        const badge = $('gen-strength');
        badge.textContent = data.strength;
        badge.style.color = strengthColor(data.strength);
        badge.style.borderColor = strengthColor(data.strength) + '44';
        badge.style.background = strengthColor(data.strength) + '18';
    } catch (err) {
        // Fallback: client-side generation
        clientSideGenerate(length, uppercase, lowercase, digits, symbols, excludeAmbiguous);
    }
}

function clientSideGenerate(length, uppercase, lowercase, digits, symbols, excludeAmbiguous) {
    const AMBIGUOUS = '0Ol1I';
    let pool = '';
    if (uppercase) pool += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    if (lowercase) pool += 'abcdefghijklmnopqrstuvwxyz';
    if (digits)    pool += '0123456789';
    if (symbols)   pool += '!@#$%^&*()_+-=[]{}|;:,.<>?';
    if (excludeAmbiguous) pool = pool.split('').filter(c => !AMBIGUOUS.includes(c)).join('');
    if (!pool) return;

    let pwd = '';
    const arr = new Uint32Array(length);
    crypto.getRandomValues(arr);
    for (let i = 0; i < length; i++) pwd += pool[arr[i] % pool.length];

    const box = $('generated-password');
    box.textContent = pwd;
    box.classList.add('has-password');
    $('gen-strength').textContent = length >= 16 ? 'Strong' : 'Medium';
}

// ── Render All ────────────────────────────────────────────
function renderAll(d) {
    updateStrength(d);
    updateMetrics(d);
    updateEntropy(d.shannon_entropy, d.search_space_entropy);
    updateCrackTimes(d.crack_times);
    updatePatterns(d.patterns);
    updateML(d.ml_prediction);
    updateFeedback(d.feedback);
    updateQuickMeter(d.complexity_score, d.overall_strength);
}

// ── Strength ──────────────────────────────────────────────
function updateStrength(d) {
    const label  = d.overall_strength;
    const score  = Math.round(d.complexity_score);
    const conf   = d.ml_prediction.confidence;

    // Label
    const labelEl = $('strength-label');
    labelEl.textContent = label;
    labelEl.className = 'strength-label ' + colorClass(label);

    // Confidence badge
    $('ml-confidence').textContent = `ML Confidence: ${(conf * 100).toFixed(1)}%`;

    // Animated score counter
    animateNum($('complexity-score'), score);

    // SVG ring (circumference = 2π × 50 ≈ 314)
    const ring = $('ring-fg');
    const offset = 314 - (score / 100) * 314;
    ring.style.strokeDashoffset = offset;
    ring.className = 'ring-fg ' + ringClass(label);

    // Bar fill
    const bar = $('strength-meter');
    bar.style.width = score + '%';
    bar.className = 'strength-bar-fill ' + fillClass(label);
}

function updateQuickMeter(score, label) {
    quickMeter.style.width = Math.min(100, score) + '%';
    quickMeter.style.background = strengthColor(label) === 'var(--red)'
        ? 'linear-gradient(90deg,#ff4060,#ff7a50)'
        : `linear-gradient(90deg, var(--cyan), ${strengthColor(label)})`;
}

// ── Metrics ───────────────────────────────────────────────
function updateMetrics(d) {
    animateNum($('metric-length'),    d.length);
    animateNum($('metric-uppercase'), d.uppercase_count);
    animateNum($('metric-lowercase'), d.lowercase_count);
    animateNum($('metric-digits'),    d.digit_count);
    animateNum($('metric-symbols'),   d.special_count);
    $('metric-unique').textContent = (d.unique_char_ratio * 100).toFixed(0) + '%';
}

// ── Entropy ───────────────────────────────────────────────
function updateEntropy(shannon, searchSpace) {
    $('shannon-val').textContent = parseFloat(shannon).toFixed(2);
    $('search-val').textContent  = parseFloat(searchSpace).toFixed(2);
    entropyChart.data.datasets[0].data = [
        parseFloat(shannon).toFixed(2),
        parseFloat(searchSpace).toFixed(2)
    ];
    entropyChart.update();
}

// ── Crack Times ───────────────────────────────────────────
function updateCrackTimes(ct) {
    const scenarios = [
        { label: '🌐 Online (1K/s)',        value: ct.online_1k },
        { label: '⚡ Fast Online (1M/s)',    value: ct.fast_online_1m },
        { label: '💻 Offline (100M/s)',      value: ct.offline_100m },
        { label: '🔥 Massive (10B/s)',       value: ct.massive_10b },
    ];

    $('crack-times').innerHTML = scenarios.map(s => {
        const cls = crackSeverityClass(s.value);
        return `<div class="crack-row ${cls}">
            <span class="crack-scenario">${s.label}</span>
            <span class="crack-time">${s.value}</span>
        </div>`;
    }).join('');
}

function crackSeverityClass(t) {
    const l = t.toLowerCase();
    if (l.includes('less than') || l.includes('second')) return 'severity-instant';
    if (l.includes('minute'))  return 'severity-minutes';
    if (l.includes('hour') || l.includes('day')) return 'severity-hours';
    return 'severity-safe';
}

// ── Patterns ──────────────────────────────────────────────
function updatePatterns(p) {
    const all = [];
    if (p.sequential.length)     all.push(...p.sequential.map(s    => ({ text: `↗ ${s}`, cls: 'chip-warning', label: 'Sequential' })));
    if (p.repeated.length)       all.push(...p.repeated.map(s      => ({ text: `∞ ${s}`, cls: 'chip-warning', label: 'Repeated' })));
    if (p.keyboard_walks.length) all.push(...p.keyboard_walks.map(s => ({ text: `⌨ ${s}`, cls: 'chip-warning', label: 'Keyboard' })));
    if (p.dictionary_words.length) all.push(...p.dictionary_words.map(s => ({ text: `📖 ${s}`, cls: 'chip-danger', label: 'Dictionary' })));
    if (p.leetspeak.length)      all.push(...p.leetspeak.map(s     => ({ text: `🔀 ${s}`, cls: 'chip-danger', label: 'Leetspeak' })));

    const wrap = $('patterns-list');
    wrap.innerHTML = all.length
        ? all.map(i => `<span class="chip ${i.cls}" title="${i.label}">${i.text}</span>`).join('')
        : '<span class="chip chip-success">✓ No patterns detected</span>';
}

// ── ML Prediction ─────────────────────────────────────────
function updateML(pred) {
    const entries = Object.entries(pred.probabilities);
    $('ml-predictions').innerHTML = entries.map(([lbl, prob]) => {
        const pct = (prob * 100).toFixed(1);
        const slug = lbl.toLowerCase().replace(' ', '-');
        return `<div class="ml-pred-row">
            <div class="ml-pred-label">
                <span>${lbl}</span>
                <span>${pct}%</span>
            </div>
            <div class="ml-pred-track">
                <div class="ml-pred-fill ml-bar-${slug}" style="width:${pct}%"></div>
            </div>
        </div>`;
    }).join('');
}

// ── Feedback ──────────────────────────────────────────────
function updateFeedback(items) {
    const icons = { warning: '⚠️', suggestion: '💡', info: 'ℹ️', success: '✅' };
    $('feedback-list').innerHTML = items.length
        ? items.map(f => `
            <li class="feedback-item feedback-${f.type} priority-${f.priority}">
                <span class="fi-icon">${icons[f.type] || 'ℹ️'}</span>
                <span>${f.message}</span>
            </li>`).join('')
        : '<li class="feedback-item feedback-success"><span class="fi-icon">✅</span><span>Excellent password! Hard to crack.</span></li>';
}

function showFeedbackError(msg) {
    $('feedback-list').innerHTML = `<li class="feedback-item feedback-warning"><span class="fi-icon">⚠️</span><span>${msg}</span></li>`;
}

// ── Toggle Visibility ─────────────────────────────────────
function togglePasswordVisibility() {
    const isPass = passwordInput.type === 'password';
    passwordInput.type = isPass ? 'text' : 'password';
    // Swap SVG eye icon
    $('eye-icon').innerHTML = isPass
        ? '<path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>'
        : '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
}

// ── Dark / Light Mode ─────────────────────────────────────
function toggleDarkMode() {
    document.body.classList.toggle('light-mode');
}

// ── Copy to Clipboard ─────────────────────────────────────
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        const btn = $('copy-btn');
        btn.classList.add('copy-success');
        btn.textContent = '✓ Copied!';
        setTimeout(() => {
            btn.classList.remove('copy-success');
            btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> Copy`;
        }, 2200);
    });
}

// ── Loading state ─────────────────────────────────────────
function setLoading(on) {
    document.querySelectorAll('.card').forEach(c => c.classList.toggle('loading', on));
}

// ── Reset ─────────────────────────────────────────────────
function resetUI() {
    $('strength-label').textContent = 'Awaiting Input';
    $('strength-label').className = 'strength-label label-default';
    $('ml-confidence').textContent = 'ML Confidence: --%';

    $('complexity-score').textContent = '0';
    const ring = $('ring-fg');
    ring.style.strokeDashoffset = '314';
    ring.className = 'ring-fg';

    $('strength-meter').style.width = '0%';
    $('strength-meter').className = 'strength-bar-fill';

    quickMeter.style.width = '0%';

    ['metric-length','metric-uppercase','metric-lowercase','metric-digits','metric-symbols'].forEach(id => $( id).textContent = '0');
    $('metric-unique').textContent = '0%';
    $('shannon-val').textContent = '0.00';
    $('search-val').textContent  = '0.00';
    updateEntropy(0, 0);

    $('crack-times').innerHTML = '<div class="crack-row skeleton-row"></div>'.repeat(4);
    $('patterns-list').innerHTML = '<span class="muted-hint">Enter a password to detect patterns</span>';
    $('ml-predictions').innerHTML = '<span class="muted-hint">Awaiting input…</span>';
    $('feedback-list').innerHTML = '<li class="feedback-item feedback-info"><span class="fi-icon">ℹ️</span><span>Enter a password above to receive personalised recommendations.</span></li>';
}

// ── Helpers ───────────────────────────────────────────────
function animateNum(el, target) {
    const current = parseInt(el.textContent) || 0;
    if (current === target) return;
    const step = target > current ? 1 : -1;
    let val = current;
    const iv = setInterval(() => {
        val += step;
        el.textContent = val;
        if (val === target) clearInterval(iv);
    }, 12);
}

function colorClass(label) {
    const map = {
        'Very Weak': 'color-very-weak', 'Weak': 'color-weak',
        'Medium': 'color-medium', 'Strong': 'color-strong', 'Very Strong': 'color-very-strong'
    };
    return map[label] || '';
}

function fillClass(label) {
    const map = {
        'Very Weak': 'fill-very-weak', 'Weak': 'fill-weak',
        'Medium': 'fill-medium', 'Strong': 'fill-strong', 'Very Strong': 'fill-very-strong'
    };
    return map[label] || '';
}

function ringClass(label) {
    const map = {
        'Very Weak': 'ring-very-weak', 'Weak': 'ring-weak',
        'Medium': 'ring-medium', 'Strong': 'ring-strong', 'Very Strong': 'ring-very-strong'
    };
    return map[label] || '';
}

function strengthColor(label) {
    const map = {
        'Very Weak': 'var(--red)', 'Weak': 'var(--amber)',
        'Medium': 'var(--cyan)', 'Strong': 'var(--green)', 'Very Strong': 'var(--green)'
    };
    return map[label] || 'var(--text-muted)';
}
