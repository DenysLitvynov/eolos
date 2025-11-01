// /js/scripts/perfil.js
// 模式：优先调用 API（PostgreSQL）；失败则自动降级到 PerfilFake（localStorage）

import { PeticionarioREST } from '/js/utilidades/peticionario_REST.js';
import '/js/logica_fake/perfil_fake.js';

// ============ 日志 ============
const LOG = (() => {
    const ENABLED = true;
    const tag = (lvl) => `[perfil:${lvl}]`;
    const ts = () => new Date().toISOString();
    const dump = (x) => { if (x !== undefined) try { console.log(x); } catch {} };
    return {
        group(title) { if (!ENABLED) return () => {}; console.groupCollapsed(`%c${title}`, 'color:#555'); return () => console.groupEnd(); },
        info(m, x) { if (ENABLED) { console.log(`${ts()} ${tag('INFO')} ℹ️ ${m}`); dump(x); } },
        ok(m, x) { if (ENABLED) { console.log(`${ts()} ${tag('OK')} ✅ ${m}`); dump(x); } },
        warn(m, x) { if (ENABLED) { console.warn(`${ts()} ${tag('WARN')} ⚠️ ${m}`); dump(x); } },
        err(m, x) { if (ENABLED) { console.error(`${ts()} ${tag('ERR')} ❌ ${m}`); dump(x); } },
        evt(m, x) { if (ENABLED) { console.log(`${ts()} ${tag('EVT')} ✳️ ${m}`); dump(x); } },
    };
})();

// ============ 常量 & DOM ============
const API_URL = '/api/v1/perfil';

const $ = (s) => document.querySelector(s);
const form = $('#registroForm');
const nombre = $('#nombre');
const apellido = $('#apellido'); // 你的表里有 apellido
const correo = $('#correo');
const targetaInp = $('#targeta_id'); // 与库保持 "targeta_id"
const contrasena = $('#contrasena');
const fecha = $('#fecha');
const btnGuardar = document.querySelector('.btn-primary');
const btnVolver = document.querySelector('.btn-segundo');

// ============ 悬浮提示（改进版） ============
function msgNode() {
    const oldInForm = document.querySelector('#registroForm #mensaje');
    if (oldInForm && oldInForm.parentNode) oldInForm.parentNode.removeChild(oldInForm);

    let n = document.querySelector('#mensaje');
    if (!n) {
        n = document.createElement('div');
        n.id = 'mensaje';
        Object.assign(n.style, {
            position: 'fixed',
            right: '20px',
            bottom: '20px',
            maxWidth: '420px',
            padding: '10px 16px',
            background: 'rgba(255,255,255,0.98)',
            border: '1px solid #ddd',
            borderRadius: '10px',
            boxShadow: '0 6px 18px rgba(0,0,0,.12)',
            fontSize: '14px',
            lineHeight: '1.25',
            zIndex: '2147483647',
            pointerEvents: 'auto',
            display: 'none',
        });

        const text = document.createElement('span');
        text.id = 'mensaje_texto';

        const close = document.createElement('button');
        close.textContent = '×';
        Object.assign(close.style, {
            marginLeft: '12px',
            border: 'none',
            background: 'transparent',
            cursor: 'pointer',
            fontSize: '18px',
            lineHeight: '1',
        });
        close.addEventListener('click', () => { n.style.display = 'none'; });

        n.appendChild(text);
        n.appendChild(close);
        document.body.appendChild(n);
    }
    return n;
}

function setMsg(text, { type = 'info', ms = null } = {}) {
    const n = msgNode();
    const textNode = n.querySelector('#mensaje_texto') || n;

    const colors = {
        ok: '#00aa55',
        err: 'crimson',
        warn: '#b36b00',
        info: '#0066cc',
    };

    const borderColors = {
        ok: '#b6efc1',
        err: '#f3b3b3',
        warn: '#f5d19a',
        info: '#cbd8ff',
    };

    textNode.textContent = text || '';
    n.style.borderColor = borderColors[type] || '#ddd';
    textNode.style.color = colors[type] || '#333';
    n.style.display = text ? 'flex' : 'none';
    n.style.alignItems = 'center';

    // 覆盖旧计时器
    if (setMsg._t) {
        clearTimeout(setMsg._t);
        setMsg._t = null;
    }

    if (ms) {
        setMsg._t = setTimeout(() => {
            n.style.display = 'none';
            setMsg._t = null;
        }, ms);
    }
}

// ============ 工具函数 ============
function lockUI(b) {
    [nombre, apellido, correo, targetaInp, contrasena, fecha, btnGuardar].forEach(el => el && (el.disabled = !!b));
}
function getUid() {
    let uid = localStorage.getItem('usuario_id');
    if (!uid) { uid = 'guest'; localStorage.setItem('usuario_id', uid); }
    return uid;
}
function normDateInput(v) {
    if (!v) return '';
    if (/^\d{4}-\d{2}-\d{2}$/.test(v)) return v;
    const d = new Date(v); if (isNaN(d)) return '';
    const y = d.getFullYear(), m = String(d.getMonth() + 1).padStart(2, '0'), dd = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${dd}`;
}

const http = new PeticionarioREST();
const fake = new window.PerfilFake();

function looksLikeDbDown(t = '') {
    const s = String(t).toLowerCase();
    return ['psycopg', 'connection refused', 'could not connect', 'timeout', 'database is not connected', 'sqlalchemy', 'migrations'].some(k => s.includes(k));
}
const safePreview = (o) => {
    try {
        const c = JSON.parse(JSON.stringify(o || {}));
        if (c.contrasena) c.contrasena = '***';
        return c;
    } catch { return o; }
};

// ============ API 调用 ============
async function apiGet(uid) {
    const url = `${API_URL}?usuario_id=${encodeURIComponent(uid)}`;
    const end = LOG.group(`GET ${url}`);
    try {
        const r = await fetch(url, { headers: { 'Accept': 'application/json' } });
        const raw = await r.text(); let data; try { data = raw ? JSON.parse(raw) : null; } catch { }
        if (!r.ok) {
            if (r.status === 404) LOG.warn('GET 404：请确认后端路由与查询参数');
            throw new Error(raw || `HTTP ${r.status}`);
        }
        LOG.ok('GET OK', safePreview(data));
        return data;
    } catch (e) {
        LOG.err('GET FAIL', e?.message);
        if (looksLikeDbDown(e?.message)) LOG.err('疑似数据库未连/迁移未执行/连接串错误');
        throw e;
    } finally { end(); }
}

async function apiPut(payload) {
    const end = LOG.group('PUT /perfil');
    try {
        const res = await http.hacerPeticionRest('PUT', API_URL, payload);
        LOG.ok('PUT OK', safePreview(res));
        return res;
    } catch (e) {
        LOG.err('PUT FAIL', e?.message);
        throw e;
    } finally { end(); }
}

// ============ fake 调用 ============
async function fakeGet(uid) {
    await fake.ensureSeed(uid);
    return fake.obtenerPerfil(uid);
}
async function fakePut(uid, payload) {
    return fake.actualizarPerfil(uid, payload);
}

// ============ 表单读/写 ============
function fillForm(d = {}) {
    if (nombre) nombre.value = d.nombre ?? '';
    if (apellido) apellido.value = d.apellido ?? '';
    if (correo) correo.value = d.correo ?? '';
    if (targetaInp) targetaInp.value = d.targeta_id ?? '';
    if (fecha) fecha.value = normDateInput(d.fecha ?? '');
    if (contrasena) contrasena.value = ''; // 安全：不回填
}
function readForm() {
    const v = {
        nombre: (nombre?.value || '').trim(),
        apellido: (apellido?.value || '').trim(),
        correo: (correo?.value || '').trim(),
        targeta_id: (targetaInp?.value || '').trim(),
        fecha: normDateInput((fecha?.value || '').trim()) || undefined,
    };
    const pass = (contrasena?.value || '').trim();
    if (pass) v.contrasena = pass;
    return v;
}

function validate(v) {
    if (!v.nombre || !v.correo || !v.targeta_id) return 'Todos los campos son obligatorios';
    return null;
}

// ============ 主流程 ============
async function cargarPerfil() {
    const uid = getUid();
    try {
        const data = await apiGet(uid);
        fillForm(data || {});
        setModeBadge('API');
        setMsg('Perfil cargado (API) ✅', { type: 'ok' });
    } catch (_) {
        const data = await fakeGet(uid);
        fillForm(data || {});
        setModeBadge('LOCAL');
        setMsg('Perfil cargado (local) ✅', { type: 'ok' });
    }
}

async function guardarPerfil() {
    const uid = getUid();
    const payload = readForm();
    const err = validate(payload);
    if (err) { setMsg(err, { type: 'err' }); return; }

    lockUI(true);
    setMsg('Guardando...', { type: 'info' });
    try {
        await apiPut({ ...payload, usuario_id: uid });
        setModeBadge('API');
        setMsg('Perfil guardado (API) ✅', { type: 'ok' });
    } catch (e) {
        await fakePut(uid, { ...payload, usuario_id: uid });
        setModeBadge('LOCAL');
        setMsg('Perfil guardado (local) ✅', { type: 'ok' });
    } finally {
        if (contrasena) contrasena.value = '';
        lockUI(false);
        try { await cargarPerfil(); } catch { }
    }
}

// ============ 模式徽章 ============
function setModeBadge(mode) {
    let h1 = document.querySelector('.auth-title');
    if (!h1) return;
    let b = h1.querySelector('.mode-badge');
    if (!b) {
        b = document.createElement('span');
        b.className = 'mode-badge';
        b.style.marginLeft = '8px';
        b.style.fontSize = '12px';
        b.style.padding = '2px 6px';
        b.style.borderRadius = '10px';
        h1.appendChild(b);
    }
    const api = mode === 'API';
    b.textContent = api ? 'API' : 'LOCAL';
    b.style.background = api ? '#e6ffed' : '#fff5e6';
    b.style.color = api ? '#095' : '#b36b00';
}

// ============ init ============
document.addEventListener('DOMContentLoaded', () => {
    if (form) form.addEventListener('submit', (e) => e.preventDefault());
    btnGuardar?.addEventListener('click', guardarPerfil);
    btnVolver?.addEventListener('click', () => (window.location.href = '/'));
    cargarPerfil();
});
