// /js/scripts/perfil.js  —— 纯前端 fake，无需后端
// 依赖：你的 HTML 中存在这些 id：#nombre #correo #targeta_id #contrasena #fecha
//       按钮 class：.btn-primary（保存），.btn-segundo（返回）
// <script type="module" src="/js/scripts/perfil.js"></script>

///////////////////////////
// 假后端：PerfilFake
///////////////////////////
class PerfilFake {
    constructor(prefix = 'perfil_') {
        this.prefix = prefix;
    }
    _key(uid) {
        return `${this.prefix}${uid}`;
    }
    _delay(ms = 120) {
        return new Promise(r => setTimeout(r, ms));
    }
    async ensureSeed(uid) {
        const key = this._key(uid);
        if (!localStorage.getItem(key)) {
            const sample = {
                usuario_id: uid,
                nombre: 'Juan Pérez',
                correo: 'juanba@gmail.com',
                targeta_id: '12345HDC',
                fecha: '1990-01-01' // YYYY-MM-DD
                // contrasena: 不回显，保存时才写入
            };
            localStorage.setItem(key, JSON.stringify(sample));
        }
    }
    async obtenerPerfil(uid) {
        await this._delay();
        if (!uid) throw new Error('usuario_id requerido');
        const raw = localStorage.getItem(this._key(uid));
        return raw ? JSON.parse(raw) : null;
    }
    async actualizarPerfil(uid, datos) {
        await this._delay();
        if (!uid) throw new Error('usuario_id requerido');
        const key = this._key(uid);
        const base = localStorage.getItem(key);
        const perfil = base ? JSON.parse(base) : { usuario_id: uid };

        const allowed = ['nombre', 'correo', 'targeta_id', 'contrasena', 'fecha'];
        allowed.forEach(k => {
            if (k in datos) {
                if (k === 'contrasena' && (!datos[k] || datos[k] === '')) return; // 不存空密码
                perfil[k] = datos[k];
            }
        });

        localStorage.setItem(key, JSON.stringify(perfil));
        return perfil;
    }
}

///////////////////////////
// UI 逻辑（与你的 HTML 对应）
///////////////////////////
const $ = s => document.querySelector(s);

const nombre     = $('#nombre');
const correo     = $('#correo');
const targeta    = $('#targeta_id');
const contrasena = $('#contrasena');
const fecha      = $('#fecha');
const btnGuardar = document.querySelector('.btn-primary');
const btnVolver  = document.querySelector('.btn-segundo');
const form       = $('#registroForm');

const api = new PerfilFake();

function getUid() {
    let uid = localStorage.getItem('usuario_id');
    if (!uid) { uid = 'guest'; localStorage.setItem('usuario_id', uid); }
    return uid;
}

// 简易消息：如果没有#mensaje，就自动创建一个
function getMsgNode() {
    let n = document.querySelector('#mensaje');
    if (!n) {
        n = document.createElement('p');
        n.id = 'mensaje';
        n.style.marginTop = '10px';
        n.style.fontSize = '14px';
        n.style.minHeight = '18px';
        form?.appendChild(n);
    }
    return n;
}
function setMsg(text, isError = false, timeout = 2500) {
    const n = getMsgNode();
    n.textContent = text || '';
    n.style.color = isError ? 'crimson' : '#0a0';
    if (timeout) {
        clearTimeout(setMsg._t);
        setMsg._t = setTimeout(() => { n.textContent = ''; }, timeout);
    }
}
function lockUI(lock) {
    [nombre, correo, targeta, contrasena, fecha, btnGuardar].forEach(el => el && (el.disabled = !!lock));
}

function normDateInput(v) {
    if (!v) return '';
    if (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v)) return v;
    const d = new Date(v);
    if (isNaN(d)) return '';
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${dd}`;
}

function validarCampos({ nombre, correo }) {
    if (!nombre || !nombre.trim()) return 'Nombre y apellido es obligatorio';
    if (!correo || !correo.trim()) return 'Correo o teléfono es obligatorio';
    // 允许邮件或电话号码（简单规则）
    const esEmail = /\S+@\S+\.\S+/.test(correo);
    const esTel   = /^[0-9+\s-]{6,}$/.test(correo);
    if (!esEmail && !esTel) return 'Ingrese un correo válido o un número de teléfono';
    return null;
}

async function cargarPerfil() {
    const uid = getUid();
    await api.ensureSeed(uid);
    try {
        lockUI(true);
        setMsg('Cargando perfil...');
        const p = await api.obtenerPerfil(uid);
        if (!p) {
            setMsg('No hay datos. Completa y guarda.', true, 4000);
            return;
        }
        if (nombre)     nombre.value     = p.nombre || '';
        if (correo)     correo.value     = p.correo || '';
        if (targeta)    targeta.value    = p.targeta_id || '';
        if (fecha)      fecha.value      = normDateInput(p.fecha);
        if (contrasena) contrasena.value = ''; // 不回显密码
        setMsg('Perfil cargado ✅');
    } catch (e) {
        console.error('[perfil] cargar error:', e);
        setMsg('Error al cargar', true, 4000);
    } finally {
        lockUI(false);
    }
}

async function guardarPerfil() {
    const uid = getUid();
    const payload = {
        nombre:     (nombre?.value || '').trim(),
        correo:     (correo?.value || '').trim(),
        targeta_id: (targeta?.value || '').trim(),
        fecha:       fecha?.value || ''
    };
    const pass = (contrasena?.value || '').trim();
    if (pass) payload.contrasena = pass;

    const err = validarCampos({ nombre: payload.nombre, correo: payload.correo });
    if (err) return setMsg(err, true);

    try {
        lockUI(true);
        setMsg('Guardando...');
        await api.actualizarPerfil(uid, payload);
        if (contrasena) contrasena.value = ''; // 保存后清空
        setMsg('Perfil guardado ✅');
        await cargarPerfil(); // 立即刷新数据
    } catch (e) {
        console.error('[perfil] guardar error:', e);
        setMsg('Error al guardar', true, 4000);
    } finally {
        lockUI(false);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // 阻止回车提交刷新
    form?.addEventListener('submit', e => e.preventDefault());
    btnGuardar?.addEventListener('click', guardarPerfil);
    btnVolver?.addEventListener('click', () => { window.location.href = '/'; });
    cargarPerfil();
});
