let userRole='', misSolicitudes=[];

document.addEventListener('DOMContentLoaded', async()=>{
    if(!Auth.checkAuth()) return;
    userRole = Auth.getRol();
    initLayout();
    if(userRole!=='Estudiante'){
        document.getElementById('pageActions').style.display='flex';
        if(['Profesor','Director de grupo','Administrador','Coordinador'].includes(userRole)){
            document.getElementById('btnSolicitudes').style.display='inline-flex';
            loadSolicitudesCount();
        }
    } else {
        document.getElementById('thAcciones').style.display='none';
    }
    if(userRole==='Estudiante') document.getElementById('thParticipar').style.display='';
    else document.getElementById('thParticipar').style.display='none';
    await load();
    document.getElementById('searchInput')?.addEventListener('input', debounce(load,300));
    document.getElementById('actividadForm')?.addEventListener('submit', save);
    loadCats();
});

async function loadSolicitudesCount(){
    const endpoint=userRole==='Administrador'||userRole==='Coordinador'?'/api/solicitudes/admin':'/api/solicitudes/profesor';
    const r=await Api.get(endpoint);
    if(!r||!r.success) return;
    const pendientes=r.data.filter(s=>s.estado==='Pendiente');
    const badge=document.getElementById('badgeSol');
    if(pendientes.length>0){badge.textContent=pendientes.length;badge.style.display='inline'}
    else badge.style.display='none';
}

async function verSolicitudes(){
    const endpoint=userRole==='Administrador'||userRole==='Coordinador'?'/api/solicitudes/admin':'/api/solicitudes/profesor';
    const r=await Api.get(endpoint);
    const tb=document.getElementById('solicitudesTable');
    if(!r||!r.success||!r.data.length){
        if(tb) tb.innerHTML='<tr><td colspan="6" class="empty-state"><p>No hay solicitudes</p></td></tr>';
        Modal.open('solicitudesModal');
        return;
    }
    tb.innerHTML=r.data.map(s=>{
        const color=s.state==='Aprobada'?'success':s.estado==='Rechazada'?'danger':'warning';
        const btns=s.estado==='Pendiente'?`<button class="btn btn-sm btn-success" onclick="responderSol(${s.id},'Aprobada')" title="Aprobar"><i class="fas fa-check"></i></button><button class="btn btn-sm btn-danger" onclick="responderSol(${s.id},'Rechazada')" title="Rechazar"><i class="fas fa-times"></i></button>`:`<span class="badge badge-${color}">${s.estado}</span>`;
        return`<tr>
            <td><strong>${s.estudiante_nombre||'-'}</strong><br><small style="color:var(--text-muted)">${s.estudiante_doc||''}</small></td>
            <td>${s.actividad_titulo||'-'}</td>
            <td>${s.curso_nombre||'-'}</td>
            <td>${s.fecha_creacion?new Date(s.fecha_creacion).toLocaleDateString():'-'}</td>
            <td><span class="badge badge-${color}">${s.estado}</span></td>
            <td>${btns}</td>
        </tr>`}).join('');
    Modal.open('solicitudesModal');
}

async function responderSol(id,estado){
    const r=await Api.put(`/api/solicitudes/${id}/responder`,{estado});
    if(r&&r.success){Toast.show('Solicitud '+estado.toLowerCase(),'success');verSolicitudes();loadSolicitudesCount()}
    else Toast.show(r?.message||'Error','error');
}

async function loadCats(){
    const r=await Api.get('/api/actividades/categorias');
    if(!r||!r.success) return;
    const fs=document.getElementById('actCategoria');
    r.data.forEach(c=>{if(fs) fs.innerHTML+=`<option value="${c.id}">${c.nombre}</option>`});
}

async function loadMisSolicitudes(){
    if(userRole!=='Estudiante') return;
    const r=await Api.get('/api/solicitudes/mias');
    if(r&&r.success) misSolicitudes=r.data;
}

async function load(){
    await loadMisSolicitudes();
    const s=document.getElementById('searchInput')?.value||'';
    const r=await Api.get(`/api/actividades?search=${s}`);
    if(!r||!r.success) return;
    const tb=document.getElementById('actividadesTable');
    if(!tb) return;
    if(!r.data.actividades.length){
        tb.innerHTML='<tr><td colspan="8" class="empty-state"><i class="fas fa-running"></i><h3>No hay actividades</h3></td></tr>';
        return;
    }
    const isE=userRole==='Estudiante';
    tb.innerHTML=r.data.actividades.map(a=>{
        const pCount=a.participantes_count||0;
        const pList=a.participantes&&a.participantes.length?a.participantes.slice(0,3).join(', ')+(a.participantes.length>3?' y '+(a.participantes.length-3)+' más':''):'Sin asignar';
        let participarCell='';
        if(isE){
            const sol=misSolicitudes.find(s=>s.actividad_id===a.id);
            if(sol){
                const color=sol.estado==='Aprobada'?'success':sol.estado==='Rechazada'?'danger':'warning';
                participarCell=`<span class="badge badge-${color}">${sol.estado}</span>`;
            }else{
                participarCell=`<button class="btn btn-sm btn-primary" onclick="solicitar(${a.id})"><i class="fas fa-hand-paper"></i> Participar</button>`;
            }
        }
        const adminBtns=isE?'':`<td><div class="table-actions"><button class="btn btn-sm btn-primary" onclick="editItem(${a.id})" title="Editar"><i class="fas fa-edit"></i></button><button class="btn btn-sm btn-danger" onclick="delItem(${a.id})" title="Eliminar"><i class="fas fa-trash"></i></button></div></td>`;
        return`<tr>
            <td>${a.titulo}</td>
            <td><span class="badge badge-purple">${a.categoria_nombre||'-'}</span></td>
            <td>${a.duracion} min</td>
            <td><span title="${a.participantes?a.participantes.join(', '):''}" style="cursor:pointer">${pCount} <i class="fas fa-users" style="color:var(--primary);font-size:12px"></i></span><div style="font-size:11px;color:var(--text-muted);margin-top:2px">${pList}</div></td>
            <td><span class="badge badge-${a.estado==='Activa'?'success':'danger'}">${a.estado}</span></td>
            <td>${a.fecha_creacion?new Date(a.fecha_creacion).toLocaleDateString():'-'}</td>
            <td>${participarCell}</td>
            ${adminBtns}
        </tr>`}).join('');
}

async function solicitar(actId){
    const progs=await Api.get('/api/programaciones');
    if(!progs||!progs.success) return Toast.show('Error al cargar programaciones','error');
    const opciones=progs.data.filter(p=>p.actividad_id===actId);
    if(!opciones.length) return Toast.show('No hay horarios disponibles para esta actividad','error');
    let progId=opciones[0].id;
    if(opciones.length>1){
        const lista=opciones.map(p=>`${p.curso_nombre} - ${p.fecha} ${p.hora_inicio}`).join('\n');
        const idx=prompt(`Selecciona un horario:\n${opciones.map((p,i)=>`${i+1}. ${p.curso_nombre} - ${p.fecha} ${p.hora_inicio}`).join('\n')}\n\nEscribe el número:`);
        if(idx===null) return;
        const i=parseInt(idx)-1;
        if(i<0||i>=opciones.length) return Toast.show('Opción inválida','error');
        progId=opciones[i].id;
    }
    const r=await Api.post('/api/solicitudes',{programacion_id:progId});
    if(r&&r.success){Toast.show(r.message,'success');load()}
    else Toast.show(r?.message||'Error','error');
}

async function save(e){
    e.preventDefault();
    const f=e.target,id=f.dataset.id;
    const d={titulo:f.titulo.value,descripcion:f.descripcion.value,categoria_id:parseInt(f.categoria_id.value),duracion:parseInt(f.duracion.value)||30,instrucciones:f.instrucciones.value,estado:f.estado.value};
    let r=id?await Api.put(`/api/actividades/${id}`,d):await Api.post('/api/actividades',d);
    if(r&&r.success){Toast.show(r.message,'success');Modal.close('actividadModal');f.reset();f.dataset.id='';load()}
    else Toast.show(r?.message||'Error','error');
}

async function editItem(id){
    const r=await Api.get('/api/actividades?per_page=100');
    if(!r||!r.success) return;
    const a=r.data.actividades.find(x=>x.id===id);
    if(!a) return;
    const f=document.getElementById('actividadForm');
    f.dataset.id=id;
    f.titulo.value=a.titulo;
    f.descripcion.value=a.descripcion||'';
    f.categoria_id.value=a.categoria_id;
    f.duracion.value=a.duracion;
    f.instrucciones.value=a.instrucciones||'';
    f.estado.value=a.estado;
    document.getElementById('actividadModalTitle').textContent='Editar Actividad';
    Modal.open('actividadModal');
}

async function delItem(id){
    if(!await Modal.confirm('¿Eliminar esta actividad?')) return;
    const r=await Api.delete(`/api/actividades/${id}`);
    if(r&&r.success){Toast.show('Eliminada','success');load()}
}

function openModal(){
    const f=document.getElementById('actividadForm');
    f.reset();f.dataset.id='';
    document.getElementById('actividadModalTitle').textContent='Nueva Actividad';
    Modal.open('actividadModal');
}

function debounce(fn,d){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),d)}}
