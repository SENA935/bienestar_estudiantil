const API_BASE = '/api';

function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

function getUser() {
    const u = localStorage.getItem('user');
    return u ? JSON.parse(u) : null;
}

function setUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

function checkAuth() {
    if (!getToken()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

async function apiRequest(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE}${url}`, {
            ...options,
            headers,
        });

        if (response.status === 401) {
            removeToken();
            window.location.href = '/login';
            return;
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast('Error de conexión con el servidor', 'error');
        return { success: false, message: 'Error de conexión' };
    }
}

function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

function openModal(id) {
    document.getElementById(id).classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
    document.body.style.overflow = '';
}

function confirmDelete(callback) {
    if (confirm('¿Está seguro de que desea eliminar este registro? Esta acción no se puede deshacer.')) {
        callback();
    }
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatTime(timeStr) {
    if (!timeStr) return '-';
    return timeStr;
}

function getStatusBadge(status) {
    const map = {
        'Activo': 'badge-success', 'Activa': 'badge-success',
        'Inactivo': 'badge-danger', 'Inactiva': 'badge-danger',
        'Programada': 'badge-info', 'En curso': 'badge-purple',
        'Finalizada': 'badge-success', 'Cancelada': 'badge-danger',
        'Realizada': 'badge-success', 'Pendiente': 'badge-warning',
        'Aprobada': 'badge-success', 'Rechazada': 'badge-danger',
        'En evaluación': 'badge-purple', 'Activa': 'badge-success',
        'Inactivo': 'badge-danger',
    };
    return `<span class="badge ${map[status] || 'badge-secondary'}">${status}</span>`;
}

function getTypeIcon(tipo) {
    const map = {
        'Nueva actividad': 'fa-calendar-plus text-blue',
        'Encuesta pendiente': 'fa-clipboard-list text-yellow',
        'Propuesta recibida': 'fa-lightbulb text-purple',
        'Actividad próxima': 'fa-clock text-green',
        'Aviso institucional': 'fa-bullhorn text-red',
    };
    return map[tipo] || 'fa-bell text-gray';
}

function getTypeBadgeClass(tipo) {
    const map = {
        'Nueva actividad': 'background: rgba(37,99,235,0.1); color: #2563EB',
        'Encuesta pendiente': 'background: rgba(245,158,11,0.1); color: #F59E0B',
        'Propuesta recibida': 'background: rgba(139,92,246,0.1); color: #8B5CF6',
        'Actividad próxima': 'background: rgba(16,185,129,0.1); color: #10B981',
        'Aviso institucional': 'background: rgba(239,68,68,0.1); color: #EF4444',
    };
    return map[tipo] || 'background: #F1F5F9; color: #64748B';
}

function initSidebar() {
    const user = getUser();
    if (user) {
        const nameEl = document.getElementById('sidebar-user-name');
        const roleEl = document.getElementById('sidebar-user-role');
        const avatarEl = document.getElementById('sidebar-avatar');
        const headerNameEl = document.getElementById('header-user-name');
        const headerRoleEl = document.getElementById('header-user-role');
        const headerAvatarEl = document.getElementById('header-avatar');
        const initials = (user.nombre?.[0] || '') + (user.apellido?.[0] || '');

        if (nameEl) nameEl.textContent = `${user.nombre} ${user.apellido}`;
        if (roleEl) roleEl.textContent = user.rol_nombre;
        if (avatarEl) avatarEl.textContent = initials;
        if (headerNameEl) headerNameEl.textContent = `${user.nombre} ${user.apellido}`;
        if (headerRoleEl) headerRoleEl.textContent = user.rol_nombre;
        if (headerAvatarEl) headerAvatarEl.textContent = initials;
    }

    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    const currentPage = window.location.pathname.replace('/', '');
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.dataset.page === currentPage) {
            item.classList.add('active');
        }
    });
}

function logout() {
    apiRequest('/auth/logout', { method: 'POST' }).finally(() => {
        removeToken();
        window.location.href = '/login';
    });
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('sidebar')) {
        initSidebar();
    }
});
