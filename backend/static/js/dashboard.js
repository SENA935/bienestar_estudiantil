document.addEventListener('DOMContentLoaded', async () => {
    if (!Auth.checkAuth()) return;
    initLayout();

    const [dashRes, propRes, alertRes] = await Promise.all([
        Api.get('/api/dashboard'),
        Api.get('/api/propuestas'),
        Api.get('/api/alertas')
    ]);

    if (dashRes && dashRes.success) loadStats(dashRes.data);
    if (propRes && propRes.success) loadPropuestas(propRes.data);
    if (alertRes && alertRes.success) loadAlertas(alertRes.data);

    if (dashRes && dashRes.success) {
        const d = dashRes.data;
        loadProximas(d.proximas_programaciones || []);
    }
});

function loadStats(data) {
    const es = data.estadisticas;
    document.getElementById('stat-prog').textContent = es.programaciones_activas;
    document.getElementById('stat-act').textContent = es.actividades_realizadas;
    document.getElementById('stat-enc').textContent = es.encuestas_respondidas;
    document.getElementById('stat-prop').textContent = es.propuestas_pendientes;
    document.getElementById('stat-alert').textContent = es.alertas_sin_leer;

    const ac = data.actividades_por_categoria || [];
    const pc = data.participacion_por_curso || [];

    const catCanvas = document.getElementById('chartCategoria');
    if (catCanvas) {
        const labels = ac.length ? ac.map(d => d.nombre) : ['Sin datos'];
        const values = ac.length ? ac.map(d => d.cantidad) : [1];
        const colors = ['#16a34a', '#087f8c', '#f59e0b', '#9333ea', '#06b6d4', '#e11d48'];
        new Chart(catCanvas, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: ac.length ? colors.slice(0, ac.length) : ['#e5e7eb'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { padding: 15, usePointStyle: true } }
                }
            }
        });
    }

    const cursoCanvas = document.getElementById('chartCurso');
    if (cursoCanvas) {
        new Chart(cursoCanvas, {
            type: 'bar',
            data: {
                labels: pc.length ? pc.map(d => d.nombre) : ['Sin datos'],
                datasets: [{
                    label: 'Participaciones',
                    data: pc.length ? pc.map(d => d.cantidad) : [0],
                    backgroundColor: '#087f8c',
                    borderRadius: 8,
                    barThickness: 32
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#f1f5f9' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }
}

function loadProximas(pp) {
    const tb = document.getElementById('proximas-actividades');
    if (!tb) return;
    if (!pp.length) {
        tb.innerHTML = '<tr><td colspan="6" class="empty-state"><p>No hay programaciones próximas</p></td></tr>';
        return;
    }
    tb.innerHTML = pp.map(p => `<tr>
        <td>${p.actividad_titulo || '-'}</td>
        <td>${p.curso_nombre || '-'}</td>
        <td>${formatDate(p.fecha)}</td>
        <td>${p.hora_inicio || '-'}</td>
        <td>${p.lugar || '-'}</td>
        <td><span class="badge badge-${badgeEstado(p.estado)}">${p.estado}</span></td>
    </tr>`).join('');
}

function loadPropuestas(propuestas) {
    const el = document.getElementById('propuestas-recientes');
    if (!el) return;
    const recent = propuestas.slice(0, 4);
    if (!recent.length) {
        el.innerHTML = '<p class="empty-list">No hay propuestas aún</p>';
        return;
    }
    el.innerHTML = recent.map(p => `<div class="propuesta-item">
        <div class="propuesta-icon" style="background:${p.estado === 'Pendiente' ? '#fef3c7' : p.estado === 'Aprobada' ? '#dcfce7' : '#fee2e2'};color:${p.estado === 'Pendiente' ? '#f59e0b' : p.estado === 'Aprobada' ? '#16a34a' : '#dc2626'}"><i class="fas fa-lightbulb"></i></div>
        <div class="propuesta-content">
            <h4>${p.titulo}</h4>
            <p>${p.descripcion ? p.descripcion.substring(0, 60) + '...' : ''}</p>
        </div>
        <span class="badge badge-${p.estado === 'Pendiente' ? 'warning' : p.estado === 'Aprobada' ? 'success' : 'danger'}">${p.estado}</span>
    </div>`).join('');
}

function loadAlertas(alertas) {
    const el = document.getElementById('alertas-recientes');
    if (!el) return;
    const recent = alertas.slice(0, 4);
    if (!recent.length) {
        el.innerHTML = '<p class="empty-list">No hay alertas</p>';
        return;
    }
    el.innerHTML = recent.map(a => {
        const icons = { Info: 'fa-info-circle', Advertencia: 'fa-exclamation-triangle', Urgente: 'fa-exclamation-circle' };
        const colors = { Info: '#06b6d4', Advertencia: '#f59e0b', Urgente: '#dc2626' };
        const bg = colors[a.tipo] || '#6b7280';
        return `<div class="alerta-item" style="${a.leida ? 'opacity:.6' : ''}">
            <div class="alerta-icon" style="background:${bg}22;color:${bg}"><i class="fas ${icons[a.tipo] || 'fa-bell'}"></i></div>
            <div class="alerta-content">
                <h4>${a.titulo}</h4>
                <p>${a.descripcion ? a.descripcion.substring(0, 60) + '...' : ''}</p>
            </div>
            <span class="badge badge-${a.leida ? 'info' : 'danger'}">${a.leida ? 'Leída' : 'Nueva'}</span>
        </div>`;
    }).join('');
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
}

function badgeEstado(e) {
    return { Programada: 'info', 'En curso': 'warning', Finalizada: 'success', Cancelada: 'danger', Activa: 'success', Pendiente: 'warning', Aprobada: 'success', Rechazada: 'danger' }[e] || 'info';
}
