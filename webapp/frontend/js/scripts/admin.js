// js/scripts/admin.js
// Autor: jinwei
// Fecha: 07-12-2025
// Descripción: Lógica de la pantalla "Listado de usuarios" (panel admin).

// ==================== CONFIG ====================

const ADMIN_API_BASE = "/api/admin_api"; // 对应后端 routers/admin_api.py 的前缀
const tokenKey = "token";

/** 统一加上 JWT 头 */
function getAuthHeaders() {
    const token = localStorage.getItem(tokenKey);
    const headers = {
        "Content-Type": "application/json",
    };
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    return headers;
}

/** 真实后端 API 客户端 */
const AdminServiceReal = {
    async listarUsuarios() {
        const res = await fetch(`${ADMIN_API_BASE}/usuarios`, {
            method: "GET",
            headers: getAuthHeaders(),
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || `Error al obtener usuarios (status ${res.status})`);
        }
        return await res.json();
    },

    async crearUsuario(payload) {
        const res = await fetch(`${ADMIN_API_BASE}/usuarios`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(payload),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            throw new Error(data.detail || `Error al crear usuario (status ${res.status})`);
        }
        return data;
    },

    async actualizarUsuario(usuario_id, payload) {
        const res = await fetch(`${ADMIN_API_BASE}/usuarios/${usuario_id}`, {
            method: "PUT",
            headers: getAuthHeaders(),
            body: JSON.stringify(payload),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            throw new Error(data.detail || `Error al actualizar usuario (status ${res.status})`);
        }
        return data;
    },

    async eliminarUsuario(usuario_id) {
        const res = await fetch(`${ADMIN_API_BASE}/usuarios/${usuario_id}`, {
            method: "DELETE",
            headers: getAuthHeaders(),
        });
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || `Error al eliminar usuario (status ${res.status})`);
        }
        return true;
    },
};

/** 最终真正用的 service（可能是真，也可能是 fake） */
let AdminService = null;

/**
 * 自动选择用真实后端还是 fake：
 * 1. 先试着请求后端 /usuarios
 *    - 如果网络错误或 5xx → 认为后端挂了，有 fake 就切 fake
 *    - 如果 2xx / 4xx（比如 401,403）→ 说明后端活着，用真实后端
 * 2. 如果页面根本没加载 admin-fake.js，就只能用真实后端
 */
async function elegirServicioAdmin() {
    const fakeDisponible = typeof window.AdminApiFake !== "undefined";

    try {
        const res = await fetch(`${ADMIN_API_BASE}/usuarios`, {
            method: "GET",
            headers: getAuthHeaders(),
        });

        if (res.status < 500) {
            console.log("⚡ Backend admin disponible → usando API real");
            AdminService = AdminServiceReal;
            return;
        }

        throw new Error(`status ${res.status}`);
    } catch (err) {
        console.warn("⚠ No se puede usar backend real:", err);

        if (fakeDisponible) {
            console.warn("👉 Usando AdminApiFake (datos simulados)");
            AdminService = window.AdminApiFake;

            document.body.insertAdjacentHTML(
                "beforeend",
                `<div style="
                    position:fixed;right:12px;bottom:12px;
                    background:#f97316;color:#fff;
                    padding:6px 10px;border-radius:999px;
                    font-size:12px;z-index:9999;
                ">
                    MODO FAKE (sin backend)
                </div>`
            );
        } else {
            console.error("❌ No hay backend ni fake: AdminServiceReal será usado igualmente (pero fallará)");
            AdminService = AdminServiceReal;
        }
    }
}

// ==================== DOM ELEMENTS ====================

const tbody = document.getElementById("users-tbody");

// 创建用户 modal
const modalBackdrop = document.getElementById("modal-backdrop");
const btnOpenModal = document.getElementById("btn-open-modal");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnCancelModal = document.getElementById("btn-cancel-modal");
const createUserForm = document.getElementById("create-user-form");
const createRoleSelect = document.getElementById("rol");

// 编辑用户 modal
const editModalBackdrop = document.getElementById("edit-user-modal");
const btnCloseEditModal = document.getElementById("btn-close-edit-modal");
const btnCancelEdit = document.getElementById("btn-cancel-edit");
const editUserForm = document.getElementById("edit-user-form");

const editNameInput = document.getElementById("edit-name");
const editLastNameInput = document.getElementById("edit-lastname");
const editEmailInput = document.getElementById("edit-email");
const editCardInput = document.getElementById("edit-card");
const editRoleSelect = document.getElementById("edit-role");

// ==================== STATE ====================

let users = [];
let editingUser = null;

// ==================== RENDER ====================

function renderUsers() {
    tbody.innerHTML = "";

    users.forEach((user, index) => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
      <td>${user.nombre ?? ""}</td>
      <td>${user.apellido ?? ""}</td>
      <td class="col-id">${user.usuario_id}</td>
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
    `;

        tbody.appendChild(tr);
    });
}

// ==================== MODALS: CREAR ====================

function openCreateModal() {
    modalBackdrop.classList.remove("hidden");
}

function closeCreateModal() {
    modalBackdrop.classList.add("hidden");
    createUserForm.reset();
}

btnOpenModal?.addEventListener("click", openCreateModal);
btnCloseModal?.addEventListener("click", closeCreateModal);
btnCancelModal?.addEventListener("click", closeCreateModal);

modalBackdrop?.addEventListener("click", (e) => {
    if (e.target === modalBackdrop) closeCreateModal();
});

// ==================== MODALS: EDITAR ====================

function openEditModal(user) {
    editingUser = user;

    editNameInput.value = user.nombre ?? "";
    editLastNameInput.value = user.apellido ?? "";
    editEmailInput.value = user.correo ?? "";
    editCardInput.value = user.targeta_id ?? "";
    editRoleSelect.value = user.rol ?? "usuario";

    editModalBackdrop.classList.remove("hidden");
}

function closeEditModal() {
    editingUser = null;
    editModalBackdrop.classList.add("hidden");
    editUserForm.reset();
}

btnCloseEditModal?.addEventListener("click", closeEditModal);
btnCancelEdit?.addEventListener("click", closeEditModal);

editModalBackdrop?.addEventListener("click", (e) => {
    if (e.target === editModalBackdrop) closeEditModal();
});

// ==================== LOAD USERS ====================

async function cargarUsuarios() {
    if (!AdminService) {
        console.error("AdminService aún no está listo");
        return;
    }

    try {
        users = await AdminService.listarUsuarios();
        renderUsers();
    } catch (err) {
        console.error(err);
        alert("Error al cargar usuarios (ver consola).");
    }
}

// ==================== CREATE USER ====================
createUserForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!AdminService) return;

    const nombre = e.target.nombre.value.trim();
    const apellido = e.target.apellido.value.trim();
    const email = e.target.email.value.trim();
    const cardId = e.target.cardId.value.trim();
    const password = e.target.password.value.trim();

    if (!nombre || !apellido || !email || !password) {
        alert("Por favor, rellena los campos obligatorios.");
        return;
    }

    // 你后端的 rol 有默认值，这里不传也可以
    const payload = {
        nombre,
        apellido,
        correo: email,
        targeta_id: cardId || null,
        contrasena: password,
    };

    try {
        const nuevo = await AdminService.crearUsuario(payload);
        users.push(nuevo);
        renderUsers();
        closeCreateModal();
    } catch (err) {
        console.error(err);
        alert(err.message || "Error al crear el usuario.");
    }
});


// ==================== EDIT USER (submit) ====================

editUserForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!AdminService || !editingUser) return;

    const payload = {
        nombre: editNameInput.value.trim(),
        apellido: editLastNameInput.value.trim(),
        correo: editEmailInput.value.trim(),
        targeta_id: editCardInput.value.trim() || null,
        rol: editRoleSelect.value,
        // 👇 不再修改密码，所以不传 contrasena_nueva
    };

    try {
        const actualizado = await AdminService.actualizarUsuario(
            editingUser.usuario_id,
            payload
        );

        users = users.map((u) =>
            u.usuario_id === actualizado.usuario_id ? actualizado : u
        );

        renderUsers();
        closeEditModal();
    } catch (err) {
        console.error(err);
        alert(err.message || "Error al actualizar usuario.");
    }
});

// ==================== TABLE ACTIONS (edit / delete) ====================

tbody?.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn || !AdminService) return;

    const index = Number(btn.dataset.index);
    const action = btn.dataset.action;
    const user = users[index];
    if (!user) return;

    if (action === "edit") {
        openEditModal(user);
    } else if (action === "delete") {
        if (!confirm(`¿Eliminar al usuario ${user.nombre ?? ""}?`)) return;
        try {
            await AdminService.eliminarUsuario(user.usuario_id);
            users.splice(index, 1);
            renderUsers();
        } catch (err) {
            console.error(err);
            alert(err.message || "Error al eliminar usuario.");
        }
    }
});

// ==================== INIT ====================

document.addEventListener("DOMContentLoaded", async () => {
    await elegirServicioAdmin();
    await cargarUsuarios();
});
