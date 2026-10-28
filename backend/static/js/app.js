const API_BASE = '';

class Auth {
    static getToken() { return localStorage.getItem('token'); }
    static setToken(t) { localStorage.setItem('token', t); }
    static removeToken() { localStorage.removeItem('token'); localStorage.removeItem('usuario'); }
    static getUsuario() { const u = localStorage.getItem('usuario'); return u ? JSON.parse(u) : null; }
    static setUsuario(u) { localStorage.setItem('usuario', JSON.stringify(u)); }
    static isLoggedIn() { return !!this.getToken(); }
    static getRol() { const u = this.getUsuario(); return u ? u.rol_nombre : null; }
    static checkAuth() { if (!this.isLoggedIn()) { window.location.href = '/login'; return false; } return true; }
}

class Api {
    static async request(url, options = {}) {
        const token = Auth.getToken();
        const headers = { 'Content-Type': 'application/json', ...options.headers };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        try {
            const r = await fetch(`${API_BASE}${url}`, { ...options, headers });
            if (r.status === 401) { Auth.removeToken(); window.location.href = '/login'; return null; }
            if (r.headers.get('content-type')?.includes('text/csv')) return r;
            return await r.json();
        } catch (e) {
            console.error('API Error:', e);
            Toast.show('Error de conexión', 'error');
            return { success: false, message: 'Error de conexión' };
        }
    }
    static get(u) { return this.request(u); }
    static post(u, b) { return this.request(u, { method: 'POST', body: JSON.stringify(b) }); }
    static put(u, b) { return this.request(u, { method: 'PUT', body: JSON.stringify(b) }); }
    static delete(u) { return this.request(u, { method: 'DELETE' }); }
}

class Toast {
    static show(msg, type = 'success', dur = 3000) {
        let c = document.querySelector('.toast-container');
        if (!c) { c = document.createElement('div'); c.className = 'toast-container'; document.body.appendChild(c); }
        const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle' };
        const t = document.createElement('div');
        t.className = `toast ${type}`;
        t.innerHTML = `<i class="fas ${icons[type] || icons.success}"></i><span class="toast-message">${msg}</span>`;
        c.appendChild(t);
        setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(100%)'; setTimeout(() => t.remove(), 300); }, dur);
    }
}

class Modal {
    static open(id) { document.getElementById(id).classList.add('active'); }
    static close(id) { document.getElementById(id).classList.remove('active'); }
    static confirm(msg) {
        return new Promise(resolve => {
            const o = document.createElement('div');
            o.className = 'modal-overlay active';
            o.innerHTML = `<div class="modal" style="max-width:400px"><div class="modal-header"><h3>Confirmar</h3></div><div class="modal-body"><p>${msg}</p></div><div class="modal-footer"><button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()">Cancelar</button><button class="btn btn-danger" id="confirmBtn">Eliminar</button></div></div>`;
            document.body.appendChild(o);
            o.querySelector('#confirmBtn').addEventListener('click', () => { o.remove(); resolve(true); });
            o.addEventListener('click', e => { if (e.target === o) { o.remove(); resolve(false); } });
        });
    }
}

async function logout() {
    try { await Api.post('/api/auth/logout'); } catch (e) {}
    Auth.removeToken();
    window.location.href = '/login';
}

function initLayout() {
    const u = Auth.getUsuario();
    if (!u) return;
    const mt = document.querySelector('.menu-toggle'), sb = document.querySelector('.sidebar'), ov = document.querySelector('.sidebar-overlay');
    if (mt) mt.addEventListener('click', () => { sb.classList.toggle('active'); ov.classList.toggle('active'); });
    if (ov) ov.addEventListener('click', () => { sb.classList.remove('active'); ov.classList.remove('active'); });
    const av = document.querySelector('.user-avatar'), nm = document.querySelector('.user-info .name'), rl = document.querySelector('.user-info .role');
    if (av) av.textContent = u.nombre.charAt(0) + u.apellido.charAt(0);
    if (nm) nm.textContent = `${u.nombre} ${u.apellido}`;
    if (rl) rl.textContent = u.rol_nombre;
    const um = document.querySelector('.user-menu');
    if (um) { um.onclick = function(e) { e.stopPropagation(); this.classList.toggle('active'); }; }
    document.addEventListener('click', () => { const um = document.querySelector('.user-menu'); if (um) um.classList.remove('active'); });
    setupMenuByRole(u.rol_nombre);
    setupNotifications();
}

function setupMenuByRole(rol) {
    const nav = document.querySelector('.sidebar-nav');
    if (!nav) return;
    const adminMenu = `
        <a href="/dashboard" class="nav-link" data-page="dashboard"><i class="fas fa-home"></i> Inicio</a>
        <div class="nav-section">Gestión</div>
        <a href="/instituciones" class="nav-link" data-page="instituciones"><i class="fas fa-building"></i> Instituciones</a>
        <a href="/usuarios" class="nav-link" data-page="usuarios"><i class="fas fa-users"></i> Usuarios</a>
        <a href="/cursos" class="nav-link" data-page="cursos"><i class="fas fa-graduation-cap"></i> Académico</a>
        <div class="nav-section">Bienestar</div>
        <a href="/actividades" class="nav-link" data-page="actividades"><i class="fas fa-running"></i> Actividades</a>
        <a href="/pausas-activas" class="nav-link" data-page="pausas"><i class="fas fa-heart"></i> Pausas Activas</a>
        <a href="/programaciones" class="nav-link" data-page="programaciones"><i class="fas fa-calendar-alt"></i> Programaciones</a>
        <a href="/encuestas" class="nav-link" data-page="encuestas"><i class="fas fa-poll"></i> Encuestas</a>
        <a href="/propuestas" class="nav-link" data-page="propuestas"><i class="fas fa-lightbulb"></i> Propuestas</a>
        <a href="/alertas" class="nav-link" data-page="alertas"><i class="fas fa-bell"></i> Alertas</a>
        <div class="nav-section">Sistema</div>
        <a href="/reportes" class="nav-link" data-page="reportes"><i class="fas fa-chart-bar"></i> Reportes</a>
        <a href="/auditoria" class="nav-link" data-page="auditoria"><i class="fas fa-history"></i> Auditoría</a>
        <a href="/configuracion" class="nav-link" data-page="configuracion"><i class="fas fa-cog"></i> Configuración</a>`;
    const coordinadorMenu = `
        <a href="/dashboard" class="nav-link" data-page="dashboard"><i class="fas fa-home"></i> Inicio</a>
        <a href="/instituciones" class="nav-link" data-page="instituciones"><i class="fas fa-building"></i> Instituciones</a>
        <a href="/usuarios" class="nav-link" data-page="usuarios"><i class="fas fa-users"></i> Usuarios</a>
        <a href="/cursos" class="nav-link" data-page="cursos"><i class="fas fa-graduation-cap"></i> Académico</a>
        <a href="/actividades" class="nav-link" data-page="actividades"><i class="fas fa-running"></i> Actividades</a>
        <a href="/pausas-activas" class="nav-link" data-page="pausas"><i class="fas fa-heart"></i> Pausas Activas</a>
        <a href="/programaciones" class="nav-link" data-page="programaciones"><i class="fas fa-calendar-alt"></i> Programaciones</a>
        <a href="/encuestas" class="nav-link" data-page="encuestas"><i class="fas fa-poll"></i> Encuestas</a>
        <a href="/propuestas" class="nav-link" data-page="propuestas"><i class="fas fa-lightbulb"></i> Propuestas</a>
        <a href="/alertas" class="nav-link" data-page="alertas"><i class="fas fa-bell"></i> Alertas</a>
        <a href="/reportes" class="nav-link" data-page="reportes"><i class="fas fa-chart-bar"></i> Reportes</a>`;
    const docenteMenu = `
        <a href="/dashboard" class="nav-link" data-page="dashboard"><i class="fas fa-home"></i> Inicio</a>
        <a href="/actividades" class="nav-link" data-page="actividades"><i class="fas fa-running"></i> Actividades</a>
        <a href="/pausas-activas" class="nav-link" data-page="pausas"><i class="fas fa-heart"></i> Pausas Activas</a>
        <a href="/programaciones" class="nav-link" data-page="programaciones"><i class="fas fa-calendar-alt"></i> Programaciones</a>
        <a href="/encuestas" class="nav-link" data-page="encuestas"><i class="fas fa-poll"></i> Encuestas</a>
        <a href="/cursos" class="nav-link" data-page="cursos"><i class="fas fa-graduation-cap"></i> Mis Alumnos</a>
        <a href="/reportes" class="nav-link" data-page="reportes"><i class="fas fa-chart-bar"></i> Reportes</a>`;
    const profesorMenu = `
        <a href="/dashboard" class="nav-link" data-page="dashboard"><i class="fas fa-home"></i> Inicio</a>
        <a href="/actividades" class="nav-link" data-page="actividades"><i class="fas fa-running"></i> Actividades</a>
        <a href="/pausas-activas" class="nav-link" data-page="pausas"><i class="fas fa-heart"></i> Pausas Activas</a>
        <a href="/programaciones" class="nav-link" data-page="programaciones"><i class="fas fa-calendar-alt"></i> Programaciones</a>
        <a href="/encuestas" class="nav-link" data-page="encuestas"><i class="fas fa-poll"></i> Encuestas</a>
        <a href="/cursos" class="nav-link" data-page="cursos"><i class="fas fa-graduation-cap"></i> Mis Alumnos</a>
        <a href="/reportes" class="nav-link" data-page="reportes"><i class="fas fa-chart-bar"></i> Reportes</a>`;
    const directorMenu = `
        <a href="/dashboard" class="nav-link" data-page="dashboard"><i class="fas fa-home"></i> Inicio</a>
        <a href="/usuarios" class="nav-link" data-page="usuarios"><i class="fas fa-users"></i> Usuarios</a>
        <a href="/cursos" class="nav-link" data-page="cursos"><i class="fas fa-graduation-cap"></i> Mis Alumnos</a>
        <a href="/actividades" class="nav-link" data-page="actividades"><i class="fas fa-running"></i> Actividades</a>
        <a href="/pausas-activas" class="nav-link" data-page="pausas"><i class="fas fa-heart"></i> Pausas Activas</a>
        <a href="/programaciones" class="nav-link" data-page="programaciones"><i class="fas fa-calendar-alt"></i> Programaciones</a>
        <a href="/encuestas" class="nav-link" data-page="encuestas"><i class="fas fa-poll"></i> Encuestas</a>
        <a href="/propuestas" class="nav-link" data-page="propuestas"><i class="fas fa-lightbulb"></i> Propuestas</a>
        <a href="/alertas" class="nav-link" data-page="alertas"><i class="fas fa-bell"></i> Alertas</a>
        <a href="/reportes" class="nav-link" data-page="reportes"><i class="fas fa-chart-bar"></i> Reportes</a>`;
    const estudianteMenu = `
        <a href="/dashboard" class="nav-link" data-page="dashboard"><i class="fas fa-home"></i> Inicio</a>
        <a href="/actividades" class="nav-link" data-page="actividades"><i class="fas fa-running"></i> Actividades</a>
        <a href="/pausas-activas" class="nav-link" data-page="pausas"><i class="fas fa-heart"></i> Pausas Activas</a>
        <a href="/encuestas" class="nav-link" data-page="encuestas"><i class="fas fa-poll"></i> Encuestas</a>
        <a href="/propuestas" class="nav-link" data-page="propuestas"><i class="fas fa-lightbulb"></i> Propuestas</a>`;
    const menus = {
        'Administrador': adminMenu,
        'Coordinador': coordinadorMenu,
        'Docente': docenteMenu,
        'Profesor': profesorMenu,
        'Director de grupo': directorMenu,
        'Estudiante': estudianteMenu
    };
    nav.innerHTML = menus[rol] || menus['Estudiante'];
    const page = window.location.pathname.split('/')[1] || 'dashboard';
    nav.querySelectorAll('.nav-link').forEach(l => { if (l.dataset.page === page) l.classList.add('active'); });
}

async function setupNotifications() {
    const r = await Api.get('/api/alertas/no-leidas');
    if (r && r.success) {
        const b = document.querySelector('.notification-badge');
        if (b) { b.textContent = r.data.count; b.style.display = r.data.count > 0 ? 'flex' : 'none'; }
    }
}
