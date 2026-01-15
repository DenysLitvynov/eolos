/**
 * recompensas-admin.js
 * Gestión de recompensas para administradores
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';
let currentPage = 1;
const ITEMS_PER_PAGE = 10;
let allRewards = [];
let currentRewardId = null;

// ============================================
// INICIALIZACIÓN
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadRewards();
});

function initializeEventListeners() {
    // Modal crear
    document.getElementById('btn-open-modal').addEventListener('click', openCreateModal);
    document.getElementById('btn-close-modal').addEventListener('click', closeCreateModal);
    document.getElementById('btn-cancel-modal').addEventListener('click', closeCreateModal);
    document.getElementById('create-reward-form').addEventListener('submit', handleCreateReward);

    // Modal editar
    document.getElementById('btn-close-edit-modal').addEventListener('click', closeEditModal);
    document.getElementById('btn-cancel-edit').addEventListener('click', closeEditModal);
    document.getElementById('edit-reward-form').addEventListener('submit', handleEditReward);

    // Modal eliminar
    document.getElementById('btn-close-delete-modal').addEventListener('click', closeDeleteModal);
    document.getElementById('btn-cancel-delete').addEventListener('click', closeDeleteModal);
    document.getElementById('btn-confirm-delete').addEventListener('click', handleDeleteReward);

    // Paginación
    document.getElementById('btn-prev').addEventListener('click', () => changePage(-1));
    document.getElementById('btn-next').addEventListener('click', () => changePage(1));

    // Cerrar modales con click fuera
    document.getElementById('modal-backdrop').addEventListener('click', (e) => {
        if (e.target.id === 'modal-backdrop') closeCreateModal();
    });
    document.getElementById('edit-reward-modal').addEventListener('click', (e) => {
        if (e.target.id === 'edit-reward-modal') closeEditModal();
    });
    document.getElementById('delete-modal').addEventListener('click', (e) => {
        if (e.target.id === 'delete-modal') closeDeleteModal();
    });
}

// ============================================
// CARGAR RECOMPENSAS
// ============================================
async function loadRewards() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/recompensas/obtener_recompensas`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Error al cargar recompensas');

        allRewards = await response.json();
        renderRewards();
    } catch (error) {
        console.error('Error:', error);
        showError('create-form-error', 'Error al cargar las recompensas');
    }
}

function renderRewards() {
    const tbody = document.getElementById('rewards-tbody');
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const pageRewards = allRewards.slice(start, end);

    tbody.innerHTML = pageRewards.map(reward => {
        const estado = getRewardStatus(reward);
        return `
            <tr>
                <td>${escapeHtml(reward.titulo)}</td>
                <td class="description-cell">${escapeHtml(reward.descripcion)}</td>
                <td>${reward.criterio_num_km} km</td>
                <td>${formatDate(reward.fecha_inicio)}</td>
                <td>${formatDate(reward.fecha_fin)}</td>
                <td><span class="status-badge status-${estado.class}">${estado.text}</span></td>
                <td>
                    <button class="btn-icon" onclick="openEditModal('${reward.recompensa_id}')" title="Editar">
                        ✏️
                    </button>
                    <button class="btn-icon btn-danger" onclick="openDeleteModal('${reward.recompensa_id}', '${escapeHtml(reward.titulo)}')" title="Eliminar">
                        🗑️
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    updatePaginationInfo();
}

function getRewardStatus(reward) {
    const now = new Date();
    const inicio = new Date(reward.fecha_inicio);
    const fin = new Date(reward.fecha_fin);

    if (now < inicio) {
        return { text: 'Próxima', class: 'pending' };
    } else if (now > fin) {
        return { text: 'Expirada', class: 'expired' };
    } else {
        return { text: 'Activa', class: 'active' };
    }
}

function updatePaginationInfo() {
    const totalPages = Math.ceil(allRewards.length / ITEMS_PER_PAGE);
    document.getElementById('page-info').textContent = `Página ${currentPage} de ${totalPages}`;
    document.getElementById('btn-prev').disabled = currentPage === 1;
    document.getElementById('btn-next').disabled = currentPage >= totalPages;
}

function changePage(delta) {
    currentPage += delta;
    renderRewards();
}

// ============================================
// CREAR RECOMPENSA
// ============================================
function openCreateModal() {
    document.getElementById('modal-backdrop').classList.remove('hidden');
    document.getElementById('create-reward-form').reset();
    clearErrors();
    
    // Establecer fecha mínima como hoy
    const now = new Date();
    const dateStr = now.toISOString().slice(0, 16);
    document.getElementById('fecha_inicio').min = dateStr;
}

function closeCreateModal() {
    document.getElementById('modal-backdrop').classList.add('hidden');
    clearErrors();
}

async function handleCreateReward(e) {
    e.preventDefault();
    clearErrors();

    const formData = {
        titulo: document.getElementById('titulo').value.trim(),
        descripcion: document.getElementById('descripcion').value.trim(),
        criterio_num_km: parseFloat(document.getElementById('criterio_km').value),
        fecha_inicio: new Date(document.getElementById('fecha_inicio').value).toISOString(),
        fecha_fin: new Date(document.getElementById('fecha_fin').value).toISOString()
    };

    // Validación
    const errors = validateRewardForm(formData);
    if (Object.keys(errors).length > 0) {
        displayErrors(errors);
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/recompensas/crear`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al crear recompensa');
        }

        closeCreateModal();
        await loadRewards();
        showSuccessNotification('Recompensa creada exitosamente');
    } catch (error) {
        showError('create-form-bottom-error', error.message);
    }
}

// ============================================
// EDITAR RECOMPENSA
// ============================================
window.openEditModal = function(rewardId) {
    const reward = allRewards.find(r => r.recompensa_id === rewardId);
    if (!reward) return;

    document.getElementById('edit-reward-id').value = reward.recompensa_id;
    document.getElementById('edit-titulo').value = reward.titulo;
    document.getElementById('edit-descripcion').value = reward.descripcion;
    document.getElementById('edit-criterio-km').value = reward.criterio_num_km;
    
    // Formatear fechas para datetime-local
    document.getElementById('edit-fecha-inicio').value = formatDateForInput(reward.fecha_inicio);
    document.getElementById('edit-fecha-fin').value = formatDateForInput(reward.fecha_fin);

    document.getElementById('edit-reward-modal').classList.remove('hidden');
    clearErrors();
};

function closeEditModal() {
    document.getElementById('edit-reward-modal').classList.add('hidden');
    clearErrors();
}

async function handleEditReward(e) {
    e.preventDefault();
    clearErrors();

    const rewardId = document.getElementById('edit-reward-id').value;
    const formData = {
        titulo: document.getElementById('edit-titulo').value.trim(),
        descripcion: document.getElementById('edit-descripcion').value.trim(),
        criterio_num_km: parseFloat(document.getElementById('edit-criterio-km').value),
        fecha_inicio: new Date(document.getElementById('edit-fecha-inicio').value).toISOString(),
        fecha_fin: new Date(document.getElementById('edit-fecha-fin').value).toISOString()
    };

    // Validación
    const errors = validateRewardForm(formData, 'edit');
    if (Object.keys(errors).length > 0) {
        displayErrors(errors, 'edit');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/recompensas/actualizar/${rewardId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al actualizar recompensa');
        }

        closeEditModal();
        await loadRewards();
        showSuccessNotification('Recompensa actualizada exitosamente');
    } catch (error) {
        showError('edit-form-bottom-error', error.message);
    }
}

// ============================================
// ELIMINAR RECOMPENSA
// ============================================
window.openDeleteModal = function(rewardId, rewardName) {
    currentRewardId = rewardId;
    document.getElementById('delete-reward-name').textContent = rewardName;
    document.getElementById('delete-modal').classList.remove('hidden');
};

function closeDeleteModal() {
    document.getElementById('delete-modal').classList.add('hidden');
    currentRewardId = null;
}

async function handleDeleteReward() {
    if (!currentRewardId) return;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/recompensas/eliminar/${currentRewardId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al eliminar recompensa');
        }

        closeDeleteModal();
        await loadRewards();
        showSuccessNotification('Recompensa eliminada exitosamente');
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar la recompensa: ' + error.message);
    }
}

// ============================================
// VALIDACIÓN
// ============================================
function validateRewardForm(data, prefix = '') {
    const errors = {};

    if (!data.titulo || data.titulo.length < 3) {
        errors[`${prefix ? prefix + '-' : ''}titulo`] = 'El título debe tener al menos 3 caracteres';
    }

    if (!data.descripcion || data.descripcion.length < 10) {
        errors[`${prefix ? prefix + '-' : ''}descripcion`] = 'La descripción debe tener al menos 10 caracteres';
    }

    if (!data.criterio_num_km || data.criterio_num_km <= 0 || data.criterio_num_km > 500) {
        errors[`${prefix ? prefix + '-' : ''}criterio_km`] = 'Los kilómetros deben estar entre 0.1 y 500';
    }

    if (!data.fecha_inicio) {
        errors[`${prefix ? prefix + '-' : ''}fecha_inicio`] = 'Selecciona una fecha de inicio';
    }

    if (!data.fecha_fin) {
        errors[`${prefix ? prefix + '-' : ''}fecha_fin`] = 'Selecciona una fecha de fin';
    }

    if (data.fecha_inicio && data.fecha_fin && new Date(data.fecha_fin) <= new Date(data.fecha_inicio)) {
        errors[`${prefix ? prefix + '-' : ''}fecha_fin`] = 'La fecha de fin debe ser posterior a la de inicio';
    }

    return errors;
}

function displayErrors(errors, prefix = '') {
    for (const [field, message] of Object.entries(errors)) {
        const errorElement = document.getElementById(`err-${field}`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    }
}

function clearErrors() {
    document.querySelectorAll('.field-error').forEach(el => {
        el.textContent = '';
        el.style.display = 'none';
    });
    document.querySelectorAll('.form-error, .form-bottom-error').forEach(el => {
        el.textContent = '';
        el.classList.add('hidden');
    });
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.remove('hidden');
    }
}

// ============================================
// UTILIDADES
// ============================================
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateForInput(dateString) {
    const date = new Date(dateString);
    return date.toISOString().slice(0, 16);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showSuccessNotification(message) {
    // Puedes implementar tu propio sistema de notificaciones
    alert(message);
}

// Exponer funciones globales necesarias
window.openEditModal = openEditModal;
window.openDeleteModal = openDeleteModal;