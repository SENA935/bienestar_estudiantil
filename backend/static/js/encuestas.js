let encData = [];
let userRole = '';

document.addEventListener('DOMContentLoaded', async () => {
    if (!Auth.checkAuth()) return;
    initLayout();
    userRole = Auth.getRol();
    document.getElementById('encuestaForm')?.addEventListener('submit', save);
    document.getElementById('respuestaForm')?.addEventListener('submit', saveResp);
    await load();
});

async function load() {
    const r = await Api.get('/api/encuestas');
    if (!r || !r.success) return;
    encData = r.data;

    if (userRole === 'Estudiante') {
        renderEstudiante();
    } else {
        renderAdmin();
    }
}

function renderEstudiante() {
    document.getElementById('cardTabla').style.display = 'none';
    document.getElementById('cardPendientes').style.display = 'block';
    document.getElementById('cardRealizadas').style.display = 'block';

    const activas = encData.filter(e => e.estado === 'Activa');
    const pendientes = activas.filter(e => !e.ya_respondio);
    const realizadas = activas.filter(e => e.ya_respondio);

    const elPend = document.getElementById('encuestasPendientes');
    if (!pendientes.length) {
        elPend.innerHTML = '<div class="empty-list"><i class="fas fa-check-circle" style="font-size:32px;color:var(--success);margin-bottom:8px;display:block"></i>No hay encuestas pendientes. ¡Excelente!</div>';
    } else {
        elPend.innerHTML = pendientes.map(e => `
            <div class="encuesta-card encuesta-pendiente">
                <div class="encuesta-card-info">
                    <h4>${e.titulo}</h4>
                    <p>${e.descripcion || 'Encuesta de bienestar'}</p>
                    <p><i class="fas fa-list"></i> ${e.preguntas_count} preguntas</p>
                </div>
                <div class="encuesta-card-status">
                    <button class="btn btn-success" onclick="responder(${e.id})"><i class="fas fa-pen"></i> Realizar</button>
                </div>
            </div>
        `).join('');
    }

    const elReal = document.getElementById('encuestasRealizadas');
    if (!realizadas.length) {
        elReal.innerHTML = '<div class="empty-list"><i class="fas fa-clipboard" style="font-size:32px;color:var(--text-muted);margin-bottom:8px;display:block"></i>Aún no has respondido ninguna encuesta</div>';
    } else {
        elReal.innerHTML = realizadas.map(e => `
            <div class="encuesta-card encuesta-realizada">
                <div class="encuesta-card-info">
                    <h4>${e.titulo}</h4>
                    <p>${e.descripcion || 'Encuesta de bienestar'}</p>
                </div>
                <div class="encuesta-card-status">
                    <span class="badge badge-success"><i class="fas fa-check"></i> Completada</span>
                </div>
            </div>
        `).join('');
    }
}

function renderAdmin() {
    document.getElementById('cardPendientes').style.display = 'none';
    document.getElementById('cardRealizadas').style.display = 'none';
    document.getElementById('cardTabla').style.display = 'block';
    document.getElementById('pageHeader').innerHTML = '<h1>Encuestas</h1><button class="btn btn-primary" onclick="openModal()"><i class="fas fa-plus"></i> Nueva Encuesta</button>';

    const tb = document.getElementById('encuestasTable');
    if (!encData.length) {
        tb.innerHTML = '<tr><td colspan="5" class="empty-state"><i class="fas fa-poll"></i><h3>No hay encuestas</h3></td></tr>';
        return;
    }
    tb.innerHTML = encData.map(e => `<tr>
        <td>${e.titulo}</td>
        <td>${e.preguntas_count} preguntas</td>
        <td>${e.respuestas_count} respuestas</td>
        <td><span class="badge badge-${e.estado === 'Activa' ? 'success' : 'danger'}">${e.estado}</span></td>
        <td>
            <button class="btn btn-sm btn-info" onclick="resultados(${e.id})" title="Ver resultados"><i class="fas fa-chart-bar"></i></button>
            <button class="btn btn-sm btn-primary" onclick="editItem(${e.id})" title="Editar"><i class="fas fa-edit"></i></button>
        </td>
    </tr>`).join('');
}

async function save(e) {
    e.preventDefault();
    const f = e.target, id = f.dataset.id;
    const d = { titulo: f.titulo.value, descripcion: f.descripcion.value, estado: f.estado.value };
    let r;
    if (id) {
        r = await Api.put(`/api/encuestas/${id}`, d);
    } else {
        d.preguntas = [
            { texto: '¿Cómo te sientes hoy?', tipo: 'seleccion_unica', requerida: true, opciones: [{ texto: 'Muy bien', valor: 0 }, { texto: 'Bien', valor: 1 }, { texto: 'Regular', valor: 2 }, { texto: 'Un poco mal', valor: 3 }, { texto: 'Mal', valor: 4 }] },
            { texto: '¿Qué nivel de energía tienes hoy?', tipo: 'escala', requerida: true, opciones: [{ texto: '1', valor: 1 }, { texto: '2', valor: 2 }, { texto: '3', valor: 3 }, { texto: '4', valor: 4 }, { texto: '5', valor: 5 }] },
            { texto: '¿Hay algo que te preocupe actualmente?', tipo: 'texto', requerida: false },
            { texto: '¿Te gustaría recibir orientación o hablar con alguien?', tipo: 'seleccion_unica', requerida: true, opciones: [{ texto: 'Sí', valor: 0 }, { texto: 'No', valor: 1 }, { texto: 'Tal vez', valor: 2 }] }
        ];
        r = await Api.post('/api/encuestas', d);
    }
    if (r && r.success) {
        Toast.show(r.message, 'success');
        Modal.close('encuestaModal');
        f.reset();
        f.dataset.id = '';
        load();
    } else {
        Toast.show(r?.message || 'Error', 'error');
    }
}

async function responder(id) {
    const r = await Api.get(`/api/encuestas/${id}`);
    if (!r || !r.success) return;
    const c = document.getElementById('preguntasContainer');
    c.innerHTML = '';
    r.data.preguntas.forEach(p => {
        let h = `<div class="form-group"><label style="font-weight:600;margin-bottom:8px;display:block">${p.texto}</label>`;
        if (p.tipo === 'seleccion_unica') {
            p.opciones.forEach(o => {
                h += `<label style="display:block;margin:6px 0;font-weight:400;cursor:pointer;padding:8px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);transition:var(--transition)"><input type="radio" name="pregunta_${p.id}" value="${o.id}" style="margin-right:8px"> ${o.texto}</label>`;
            });
        } else if (p.tipo === 'escala') {
            h += `<div style="display:flex;align-items:center;gap:12px"><input type="range" name="pregunta_${p.id}" min="1" max="5" value="3" class="form-control" style="flex:1" oninput="this.nextElementSibling.textContent=this.value"><span style="font-weight:700;font-size:20px;color:var(--primary)">3</span></div>`;
        } else if (p.tipo === 'texto') {
            h += `<textarea name="pregunta_${p.id}" class="form-control" rows="3" placeholder="Escribe tu respuesta aquí..."></textarea>`;
        }
        h += '</div>';
        c.innerHTML += h;
    });
    document.getElementById('encuestaId').value = id;
    Modal.open('respuestaModal');
}

async function saveResp(e) {
    e.preventDefault();
    const eid = document.getElementById('encuestaId').value;
    const inputs = document.querySelectorAll('#preguntasContainer [name^="pregunta_"]');
    const resp = [];
    inputs.forEach(i => {
        const pid = i.name.replace('pregunta_', '');
        if (i.type === 'radio' && i.checked) resp.push({ pregunta_id: parseInt(pid), opcion_id: parseInt(i.value) });
        else if (i.type === 'range') resp.push({ pregunta_id: parseInt(pid), valor_numero: parseFloat(i.value) });
        else if (i.tagName === 'TEXTAREA' && i.value.trim()) resp.push({ pregunta_id: parseInt(pid), valor_texto: i.value.trim() });
    });
    const r = await Api.post(`/api/encuestas/${eid}/responder`, { respuestas: resp });
    if (r && r.success) {
        Toast.show('Encuesta completada exitosamente', 'success');
        Modal.close('respuestaModal');
        load();
    } else {
        Toast.show(r?.message || 'Error al enviar', 'error');
    }
}

async function editItem(id) {
    const e = encData.find(x => x.id === id);
    if (!e) return;
    const f = document.getElementById('encuestaForm');
    f.dataset.id = id;
    f.titulo.value = e.titulo;
    f.descripcion.value = e.descripcion || '';
    f.estado.value = e.estado;
    Modal.open('encuestaModal');
}

async function resultados(id) {
    const r = await Api.get(`/api/encuestas/${id}/resultados`);
    if (!r || !r.success) return;
    const tb = document.getElementById('resultadosTable');
    if (!tb) return;
    if (!r.data.length) {
        tb.innerHTML = '<tr><td colspan="2" class="empty-state"><p>No hay respuestas aun</p></td></tr>';
    } else {
        tb.innerHTML = r.data.map(x => {
            const respuestas = x.respuestas.map(rs => rs.opcion_texto || rs.valor_texto || rs.valor_numero || '-').join(', ');
            return `<tr><td>${respuestas}</td><td>${new Date(x.fecha_respuesta).toLocaleDateString('es-CO')}</td></tr>`;
        }).join('');
    }
    Modal.open('resultadosModal');
}

function openModal() {
    document.getElementById('encuestaForm').reset();
    document.getElementById('encuestaForm').dataset.id = '';
    Modal.open('encuestaModal');
}
