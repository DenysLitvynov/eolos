// js/scripts/admin.js
// Autor: jinwei
// Fecha: 07-12-2025
// Descripción: Lógica de la pantalla "Listado de usuarios" (panel admin).

// ==================== CONFIGURACIÓN ====================

const ADMIN_API_BASE = "/api/admin_api";
const tokenKey = "token";

// Paginación
const PAGE_SIZE = 100;  // tamaño de página
let currentOffset = 0;
let hasNextPage = true;

// Construye headers con JWT Bearer
function getAuthHeaders() {
    const token = localStorage.getItem(tokenKey);
    const headers = { "Content-Type": "application/json" };
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
}

// Error tipado para APIs
class ApiError extends Error {
    constructor(status, data) {
        const msg = buildHumanMessage(status, data);
        super(msg);
        this.name = "ApiError";
        this.status = status;
        this.data = data;
    }
}

// Mensaje humano desde respuesta de FastAPI
function buildHumanMessage(status, data) {
    if (!data) return "";
    const detail = data.detail ?? data;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return "Hay errores en el formulario.";
    if (typeof detail === "object" && detail && Object.keys(detail).length === 0) return "";
    return `Error (status ${status})`;
}

// Mapea errores de validación (422) de FastAPI -> {campo: [msgs]}
function mapFastApiValidationErrors(data) {
    const out = {};
    const detail = data?.detail;
    if (!Array.isArray(detail)) return out;

    for (const item of detail) {
        const loc = item?.loc || [];
        const msg = item?.msg || "Valor inválido";
        const idx = loc.indexOf("body");
        const field = idx >= 0 ? loc[idx + 1] : loc[loc.length - 1];
        if (!field) continue;
        if (!out[field]) out[field] = [];
        out[field].push(msg);
    }
    return out;
}

// ==================== API ====================

const AdminServiceReal = {
    // Lista usuarios con limit/offset
    async listarUsuarios(limit = PAGE_SIZE, offset = 0) {
        const res = await fetch(
            `${ADMIN_API_BASE}/usuarios?limit=${encodeURIComponent(limit)}&offset=${encodeURIComponent(offset)}`,
            { method: "GET", headers: getAuthHeaders() }
        );
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new ApiError(res.status, data);
        return data;
    },

    async crearUsuario(payload) {
        const res = await fetch(`${ADMIN_API_BASE}/usuarios`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(payload),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new ApiError(res.status, data);
        return data;
    },

    async actualizarUsuario(usuario_id, payload) {
        const res = await fetch(`${ADMIN_API_BASE}/usuarios/${usuario_id}`, {
            method: "PUT",
            headers: getAuthHeaders(),
            body: JSON.stringify(payload),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new ApiError(res.status, data);
        return data;
    },

    async eliminarUsuario(usuario_id) {
        const res = await fetch(`${ADMIN_API_BASE}/usuarios/${usuario_id}`, {
            method: "DELETE",
            headers: getAuthHeaders(),
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new ApiError(res.status, data);
        }
        return true;
    },
};

// ==================== SERVICIO (REAL/FAKE) ====================

let AdminService = null;

// Cache de primera página para acelerar render
let _firstPageCache = null;

async function elegirServicioAdmin() {
    const fakeDisponible = typeof window.AdminApiFake !== "undefined";

    try {
        // Pedimos primera página para saber si backend está OK
        const res = await fetch(
            `${ADMIN_API_BASE}/usuarios?limit=${encodeURIComponent(PAGE_SIZE)}&offset=0`,
            { method: "GET", headers: getAuthHeaders() }
        );

        if (res.status < 500) {
            AdminService = AdminServiceReal;
            const data = await res.json().catch(() => null);
            if (Array.isArray(data)) _firstPageCache = data;
            return;
        }

        throw new Error(`status ${res.status}`);
    } catch (err) {
        if (fakeDisponible) {
            AdminService = window.AdminApiFake;
            document.body.insertAdjacentHTML(
                "beforeend",
                `<div style="
          position:fixed;right:12px;bottom:12px;
          background:#f97316;color:#fff;
          padding:6px 10px;border-radius:999px;
          font-size:12px;z-index:9999;
        ">MODO FAKE (sin backend)</div>`
            );
        } else {
            AdminService = AdminServiceReal;
        }
    }
}

// ==================== DOM ====================

const tbody = document.getElementById("users-tbody");

// Paginación
const btnPrev = document.getElementById("btn-prev");
const btnNext = document.getElementById("btn-next");
const pageInfo = document.getElementById("page-info");

// Modal crear
const modalBackdrop = document.getElementById("modal-backdrop");
const btnOpenModal = document.getElementById("btn-open-modal");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnCancelModal = document.getElementById("btn-cancel-modal");
const createUserForm = document.getElementById("create-user-form");

// Inputs crear
const createNombre = document.getElementById("nombre");
const createApellido = document.getElementById("apellido");
const createEmail = document.getElementById("email");
const createCardId = document.getElementById("cardId");
const createPassword = document.getElementById("password");
const createPassword2 = document.getElementById("password2");

// Botones mostrar/ocultar (crear)
const btnToggleCreatePwd = document.getElementById("toggle-create-password");
const btnToggleCreatePwd2 = document.getElementById("toggle-create-password2");

// Errores crear
const errNombre = document.getElementById("err-nombre");
const errApellido = document.getElementById("err-apellido");
const errEmail = document.getElementById("err-email");
const errCardId = document.getElementById("err-cardId");
const errPassword = document.getElementById("err-password");
const errPassword2 = document.getElementById("err-password2");
const createBottomError = document.getElementById("create-form-bottom-error");

// Modal editar
const editModalBackdrop = document.getElementById("edit-user-modal");
const btnCloseEditModal = document.getElementById("btn-close-edit-modal");
const btnCancelEdit = document.getElementById("btn-cancel-edit");
const editUserForm = document.getElementById("edit-user-form");

// Inputs editar
const editNameInput = document.getElementById("edit-name");
const editLastNameInput = document.getElementById("edit-lastname");
const editEmailInput = document.getElementById("edit-email");
const editCardInput = document.getElementById("edit-card");
const editRoleSelect = document.getElementById("edit-role");

// Errores editar
const errEditName = document.getElementById("err-edit-name");
const errEditLast = document.getElementById("err-edit-lastname");
const errEditEmail = document.getElementById("err-edit-email");
const errEditCard = document.getElementById("err-edit-card");
const errEditRole = document.getElementById("err-edit-role");
const editBottomError = document.getElementById("edit-form-bottom-error");

// ==================== STATE ====================

let users = [];
let editingUser = null;

// ==================== RENDER ====================

function renderUsers() {
    tbody.innerHTML = users
        .map(
            (user, index) => `
      <tr>
        <td>${user.nombre ?? ""}</td>
        <td>${user.apellido ?? ""}</td>
        <td class="col-id">${user.usuario_id ?? ""}</td>
        <td class="col-id">${user.targeta_id ?? ""}</td>
        <td>${user.rol ?? ""}</td>
        <td>${user.correo ?? ""}</td>
        <td>
          <div class="action-group">
            <button class="icon-btn" data-action="edit" data-index="${index}" title="Editar">
              <img src="../../images/editar.png" alt="Editar" class="table-icon" />
            </button>
            <button class="icon-btn" data-action="delete" data-index="${index}" title="Eliminar">
              <img src="../../images/eliminar.png" alt="Eliminar" class="table-icon" />
            </button>
          </div>
        </td>
      </tr>`
        )
        .join("");
}

function renderLoadingRow() {
    tbody.innerHTML = `
    <tr>
      <td colspan="7" style="padding:16px;color:#64748b;">
        Cargando usuarios...
      </td>
    </tr>
  `;
}

function setPagingUI({ loading = false } = {}) {
    const page = Math.floor(currentOffset / PAGE_SIZE) + 1;
    if (pageInfo) pageInfo.textContent = `Página ${page}`;

    if (btnPrev) btnPrev.disabled = loading || currentOffset <= 0;
    if (btnNext) btnNext.disabled = loading || !hasNextPage;
}

// ==================== UI ERRORES ====================

function setFieldError(inputEl, errEl, msg) {
    if (!inputEl || !errEl) return;
    errEl.textContent = msg || "";
    if (msg) inputEl.classList.add("input-error");
    else inputEl.classList.remove("input-error");
}

function showBottomError(el, msg) {
    if (!el) return;
    if (!msg || msg === "{}") {
        el.textContent = "";
        el.classList.add("hidden");
        return;
    }
    el.textContent = msg;
    el.classList.remove("hidden");
}

function clearCreateErrors() {
    setFieldError(createNombre, errNombre, "");
    setFieldError(createApellido, errApellido, "");
    setFieldError(createEmail, errEmail, "");
    setFieldError(createCardId, errCardId, "");
    setFieldError(createPassword, errPassword, "");
    setFieldError(createPassword2, errPassword2, "");
    showBottomError(createBottomError, "");
}

function clearEditErrors() {
    setFieldError(editNameInput, errEditName, "");
    setFieldError(editLastNameInput, errEditLast, "");
    setFieldError(editEmailInput, errEditEmail, "");
    setFieldError(editCardInput, errEditCard, "");
    setFieldError(editRoleSelect, errEditRole, "");
    showBottomError(editBottomError, "");
}

// ==================== VALIDACIONES ====================

// Regla de contraseña (misma que backend)
function passwordRuleOk(pwd) {
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;
    return re.test(pwd);
}

// Regla tarjeta: 8 dígitos + 1 letra
function cardIdRuleOk(cardId) {
    const re = /^\d{8}[A-Za-z]$/;
    return re.test(cardId);
}

// Normaliza rol para backend (técnico -> tecnico)
function normalizeRole(raw) {
    if (!raw) return "usuario";
    const v = String(raw).trim().toLowerCase();
    if (v === "técnico") return "tecnico";
    return v;
}

// Validación del formulario de creación (incluye repetir contraseña)
function validateCreateForm() {
    clearCreateErrors();

    const nombre = createNombre.value.trim();
    const apellido = createApellido.value.trim();
    const email = createEmail.value.trim();
    const cardId = createCardId.value.trim();
    const pwd = createPassword.value.trim();
    const pwd2 = createPassword2.value.trim();

    let ok = true;

    if (!nombre) {
        setFieldError(createNombre, errNombre, "Este campo es obligatorio");
        ok = false;
    }

    if (!apellido) {
        setFieldError(createApellido, errApellido, "Este campo es obligatorio");
        ok = false;
    }

    if (!email) {
        setFieldError(createEmail, errEmail, "Este campo es obligatorio");
        ok = false;
    } else if (!email.includes("@") || !createEmail.checkValidity()) {
        setFieldError(createEmail, errEmail, "Debe ser un correo válido (incluye @)");
        ok = false;
    }

    if (!cardId) {
        setFieldError(createCardId, errCardId, "Este campo es obligatorio");
        ok = false;
    } else if (!cardIdRuleOk(cardId)) {
        setFieldError(createCardId, errCardId, "Formato: 8 dígitos + 1 letra (ej: 12345655L)");
        ok = false;
    }

    if (!pwd) {
        setFieldError(createPassword, errPassword, "Este campo es obligatorio");
        ok = false;
    } else if (!passwordRuleOk(pwd)) {
        setFieldError(
            createPassword,
            errPassword,
            "Mín. 8 caracteres, con mayúscula, minúscula, número y símbolo (@$!%*?&)"
        );
        ok = false;
    }

    if (!pwd2) {
        setFieldError(createPassword2, errPassword2, "Debes repetir la contraseña");
        ok = false;
    } else if (pwd && pwd2 && pwd !== pwd2) {
        setFieldError(createPassword2, errPassword2, "Debe coincidir con la contraseña anterior");
        ok = false;
    }

    return ok;
}

// Validación del formulario de edición
function validateEditForm() {
    clearEditErrors();

    const nombre = editNameInput.value.trim();
    const apellido = editLastNameInput.value.trim();
    const email = editEmailInput.value.trim();
    const cardId = editCardInput.value.trim();
    const rol = normalizeRole(editRoleSelect.value);

    let ok = true;

    if (!nombre) {
        setFieldError(editNameInput, errEditName, "Este campo es obligatorio");
        ok = false;
    }
    if (!apellido) {
        setFieldError(editLastNameInput, errEditLast, "Este campo es obligatorio");
        ok = false;
    }
    if (!email) {
        setFieldError(editEmailInput, errEditEmail, "Este campo es obligatorio");
        ok = false;
    } else if (!email.includes("@") || !editEmailInput.checkValidity()) {
        setFieldError(editEmailInput, errEditEmail, "Debe ser un correo válido (incluye @)");
        ok = false;
    }

    if (rol === "usuario") {
        if (!cardId) {
            setFieldError(editCardInput, errEditCard, "Este campo es obligatorio para rol 'usuario'");
            ok = false;
        } else if (!cardIdRuleOk(cardId)) {
            setFieldError(editCardInput, errEditCard, "Formato: 8 dígitos + 1 letra (ej: 12345655L)");
            ok = false;
        }
    } else {
        if (cardId && !cardIdRuleOk(cardId)) {
            setFieldError(editCardInput, errEditCard, "Formato: 8 dígitos + 1 letra (ej: 12345655L)");
            ok = false;
        }
    }

    return ok;
}

// ==================== ERRORES BACKEND -> UI ====================

function applyBackendErrorsToCreateForm(apiErr) {
    const map = mapFastApiValidationErrors(apiErr?.data);

    if (map.nombre?.length) setFieldError(createNombre, errNombre, map.nombre[0]);
    if (map.apellido?.length) setFieldError(createApellido, errApellido, map.apellido[0]);
    if (map.correo?.length) setFieldError(createEmail, errEmail, map.correo[0]);
    if (map.targeta_id?.length) setFieldError(createCardId, errCardId, map.targeta_id[0]);
    if (map.contrasena?.length) setFieldError(createPassword, errPassword, map.contrasena[0]);

    const detail = apiErr?.data?.detail;
    if (typeof detail === "string") {
        const lower = detail.toLowerCase();
        if (lower.includes("correo")) setFieldError(createEmail, errEmail, detail);
        else if (lower.includes("contrase")) setFieldError(createPassword, errPassword, detail);
        else if (lower.includes("tarjeta") || lower.includes("targeta")) setFieldError(createCardId, errCardId, detail);
        else showBottomError(createBottomError, detail);
        return;
    }

    if (!Object.keys(map).length) {
        showBottomError(createBottomError, apiErr.message || "Error en el registro. Verifica los datos.");
    }
}

function applyBackendErrorsToEditForm(apiErr) {
    const map = mapFastApiValidationErrors(apiErr?.data);

    if (map.nombre?.length) setFieldError(editNameInput, errEditName, map.nombre[0]);
    if (map.apellido?.length) setFieldError(editLastNameInput, errEditLast, map.apellido[0]);
    if (map.correo?.length) setFieldError(editEmailInput, errEditEmail, map.correo[0]);
    if (map.targeta_id?.length) setFieldError(editCardInput, errEditCard, map.targeta_id[0]);
    if (map.rol?.length) setFieldError(editRoleSelect, errEditRole, map.rol[0]);

    const detail = apiErr?.data?.detail;
    if (typeof detail === "string") {
        const lower = detail.toLowerCase();
        if (lower.includes("correo")) setFieldError(editEmailInput, errEditEmail, detail);
        else if (lower.includes("tarjeta") || lower.includes("targeta")) setFieldError(editCardInput, errEditCard, detail);
        else showBottomError(editBottomError, detail);
        return;
    }

    if (!Object.keys(map).length) {
        showBottomError(editBottomError, apiErr.message || "Error al guardar. Verifica los datos.");
    }
}

// ==================== MOSTRAR / OCULTAR CONTRASEÑA ====================

function togglePassword(inputEl, btnEl) {
    if (!inputEl || !btnEl) return;
    const isPassword = inputEl.type === "password";
    inputEl.type = isPassword ? "text" : "password";
    btnEl.textContent = isPassword ? "Ocultar" : "Mostrar";
}

btnToggleCreatePwd?.addEventListener("click", () => togglePassword(createPassword, btnToggleCreatePwd));
btnToggleCreatePwd2?.addEventListener("click", () => togglePassword(createPassword2, btnToggleCreatePwd2));

// ==================== MODALES ====================

function openCreateModal() {
    clearCreateErrors();
    modalBackdrop.classList.remove("hidden");
}

function closeCreateModal() {
    modalBackdrop.classList.add("hidden");
    createUserForm?.reset();
    clearCreateErrors();

    // Restablecer botones y tipos
    if (createPassword) createPassword.type = "password";
    if (createPassword2) createPassword2.type = "password";
    if (btnToggleCreatePwd) btnToggleCreatePwd.textContent = "Mostrar";
    if (btnToggleCreatePwd2) btnToggleCreatePwd2.textContent = "Mostrar";
}

btnOpenModal?.addEventListener("click", openCreateModal);
btnCloseModal?.addEventListener("click", closeCreateModal);
btnCancelModal?.addEventListener("click", closeCreateModal);

modalBackdrop?.addEventListener("click", (e) => {
    if (e.target === modalBackdrop) closeCreateModal();
});

// Limpiar errores al escribir (crear)
[createNombre, createApellido, createEmail, createCardId, createPassword, createPassword2].forEach((el) => {
    el?.addEventListener("input", () => {
        if (el === createNombre) setFieldError(createNombre, errNombre, "");
        if (el === createApellido) setFieldError(createApellido, errApellido, "");
        if (el === createEmail) setFieldError(createEmail, errEmail, "");
        if (el === createCardId) setFieldError(createCardId, errCardId, "");
        if (el === createPassword) setFieldError(createPassword, errPassword, "");
        if (el === createPassword2) setFieldError(createPassword2, errPassword2, "");
        showBottomError(createBottomError, "");
    });
});

function openEditModal(user) {
    editingUser = user;
    clearEditErrors();

    editNameInput.value = user.nombre ?? "";
    editLastNameInput.value = user.apellido ?? "";
    editEmailInput.value = user.correo ?? "";
    editCardInput.value = user.targeta_id ?? "";
    editRoleSelect.value = normalizeRole(user.rol ?? "usuario");

    editModalBackdrop.classList.remove("hidden");
}

function closeEditModal() {
    editingUser = null;
    editModalBackdrop.classList.add("hidden");
    editUserForm?.reset();
    clearEditErrors();
}

btnCloseEditModal?.addEventListener("click", closeEditModal);
btnCancelEdit?.addEventListener("click", closeEditModal);

editModalBackdrop?.addEventListener("click", (e) => {
    if (e.target === editModalBackdrop) closeEditModal();
});

// Limpiar errores al escribir (editar)
[editNameInput, editLastNameInput, editEmailInput, editCardInput, editRoleSelect].forEach((el) => {
    el?.addEventListener("input", () => {
        if (el === editNameInput) setFieldError(editNameInput, errEditName, "");
        if (el === editLastNameInput) setFieldError(editLastNameInput, errEditLast, "");
        if (el === editEmailInput) setFieldError(editEmailInput, errEditEmail, "");
        if (el === editCardInput) setFieldError(editCardInput, errEditCard, "");
        if (el === editRoleSelect) setFieldError(editRoleSelect, errEditRole, "");
        showBottomError(editBottomError, "");
    });
});

// ==================== CARGA DE USUARIOS (PAGINACIÓN) ====================

async function cargarUsuariosPagina(offset) {
    if (!AdminService) return;

    currentOffset = Math.max(0, offset);
    renderLoadingRow();
    hasNextPage = true;
    setPagingUI({ loading: true });

    try {
        const data = await AdminService.listarUsuarios(PAGE_SIZE, currentOffset);
        users = Array.isArray(data) ? data : [];
        renderUsers();

        // Si viene menos de PAGE_SIZE, no hay “siguiente”
        hasNextPage = users.length === PAGE_SIZE;

        setPagingUI({ loading: false });
    } catch (err) {
        console.error(err);
        tbody.innerHTML = `
      <tr><td colspan="7" style="padding:16px;color:#b91c1c;">
        Error al cargar usuarios.
      </td></tr>
    `;
        hasNextPage = false;
        setPagingUI({ loading: false });
    }
}

btnPrev?.addEventListener("click", async () => {
    if (currentOffset <= 0) return;
    await cargarUsuariosPagina(currentOffset - PAGE_SIZE);
});

btnNext?.addEventListener("click", async () => {
    if (!hasNextPage) return;
    await cargarUsuariosPagina(currentOffset + PAGE_SIZE);
});

// ==================== CREAR USUARIO ====================

createUserForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!AdminService) return;

    if (!validateCreateForm()) return;

    const payload = {
        nombre: createNombre.value.trim(),
        apellido: createApellido.value.trim(),
        correo: createEmail.value.trim(),
        targeta_id: createCardId.value.trim(),
        contrasena: createPassword.value.trim(),
    };

    try {
        await AdminService.crearUsuario(payload);

        // Cierra modal y refresca la página actual (NO insertamos al principio)
        closeCreateModal();
        await cargarUsuariosPagina(currentOffset);

    } catch (err) {
        console.error(err);
        if (err instanceof ApiError) applyBackendErrorsToCreateForm(err);
        else showBottomError(createBottomError, err?.message || "Error en el registro. Verifica los datos.");
    }
});

// ==================== EDITAR USUARIO ====================

editUserForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!AdminService || !editingUser) return;

    if (!validateEditForm()) return;

    const rol = normalizeRole(editRoleSelect.value);
    const cardValue = editCardInput.value.trim();

    const payload = {
        nombre: editNameInput.value.trim(),
        apellido: editLastNameInput.value.trim(),
        correo: editEmailInput.value.trim(),
        rol,
        targeta_id: cardValue === "" ? null : cardValue,
    };

    try {
        await AdminService.actualizarUsuario(editingUser.usuario_id, payload);
        closeEditModal();
        await cargarUsuariosPagina(currentOffset);
    } catch (err) {
        console.error(err);
        if (err instanceof ApiError) applyBackendErrorsToEditForm(err);
        else showBottomError(editBottomError, err?.message || "Error al guardar. Verifica los datos.");
    }
});

// ==================== ACCIONES DE TABLA ====================

tbody?.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn || !AdminService) return;

    const index = Number(btn.dataset.index);
    const action = btn.dataset.action;
    const user = users[index];
    if (!user) return;

    if (action === "edit") {
        openEditModal(user);
        return;
    }

    if (action === "delete") {
        if (!confirm(`¿Eliminar al usuario ${user.nombre ?? ""}?`)) return;

        try {
            await AdminService.eliminarUsuario(user.usuario_id);

            // Refresca la página actual; si queda vacía, vuelve a la anterior
            await cargarUsuariosPagina(currentOffset);
            if (users.length === 0 && currentOffset > 0) {
                await cargarUsuariosPagina(currentOffset - PAGE_SIZE);
            }
        } catch (err) {
            console.error(err);
            alert(err?.message || "Error al eliminar usuario.");
        }
    }
});

// ==================== INIT ====================

document.addEventListener("DOMContentLoaded", async () => {
    await elegirServicioAdmin();

    // Si ya tenemos cache de primera página, pintamos sin esperar otra petición
    if (Array.isArray(_firstPageCache)) {
        users = _firstPageCache;
        _firstPageCache = null;

        currentOffset = 0;
        hasNextPage = users.length === PAGE_SIZE;

        renderUsers();
        setPagingUI({ loading: false });
    } else {
        await cargarUsuariosPagina(0);
    }
});
