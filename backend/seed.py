import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, time, datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.institucion import Institucion
from app.models.sede import Sede
from app.models.curso import Curso
from app.models.estudiante import Estudiante
from app.models.actividad import Actividad
from app.models.programacion import Programacion
from app.models.encuesta import Encuesta, PreguntaEncuesta, OpcionPregunta
from app.models.propuesta import Propuesta
from app.models.alerta import Alerta
from app.models.periodo_academico import PeriodoAcademico
from app.models.categoria_actividad import CategoriaActividad


def seed(app=None):
    if app is None:
        app = create_app()
    with app.app_context():
        db.create_all()

        print("Creando roles...")
        roles = {
            'Administrador': Rol(nombre='Administrador', descripcion='Acceso total al sistema'),
            'Coordinador': Rol(nombre='Coordinador', descripcion='Gestión de actividades y usuarios'),
            'Docente': Rol(nombre='Docente', descripcion='Gestión de actividades asignadas'),
            'Estudiante': Rol(nombre='Estudiante', descripcion='Participación y encuestas'),
        }
        for r in roles.values():
            db.session.add(r)
        db.session.flush()

        print("Creando institución e sede...")
        inst = Institucion(
            nombre='SENA - Servicio Nacional de Aprendizaje',
            nit='899999061-1',
            telefono='(601) 5461500',
            email='info@sena.edu.co',
            estado='Activa'
        )
        db.session.add(inst)
        db.session.flush()

        sede = Sede(
            nombre='Sede Principal',
            direccion='Calle 57 No. 8-69 Bogotá D.C.',
            institucion_id=inst.id,
            telefono='(601) 5461500',
            estado='Activa'
        )
        db.session.add(sede)
        db.session.flush()

        print("Creando usuarios...")
        admin = Usuario(nombre='Carlos', apellido='Rodríguez', username='admin',
                        email='admin@sena.edu.co', rol_id=roles['Administrador'].id,
                        institucion_id=inst.id)
        admin.set_password('admin123')
        db.session.add(admin)

        coord = Usuario(nombre='María', apellido='López', username='coordinador',
                        email='coord@sena.edu.co', rol_id=roles['Coordinador'].id,
                        institucion_id=inst.id)
        coord.set_password('coord123')
        db.session.add(coord)

        doc1 = Usuario(nombre='Andrés', apellido='Martínez', username='docente1',
                       email='doc1@sena.edu.co', rol_id=roles['Docente'].id,
                       institucion_id=inst.id)
        doc1.set_password('doc123')
        db.session.add(doc1)

        doc2 = Usuario(nombre='Laura', apellido='García', username='docente2',
                       email='doc2@sena.edu.co', rol_id=roles['Docente'].id,
                       institucion_id=inst.id)
        doc2.set_password('doc123')
        db.session.add(doc2)

        estudiantes_data = [
            ('Juan', 'Pérez'), ('Ana', 'Gómez'), ('Luis', 'Torres'),
            ('Sofía', 'Ramírez',), ('Diego', 'Hernández'), ('Valentina', 'Díaz'),
            ('Sebastián', 'Moreno'), ('Camila', 'Vargas'), ('Mateo', 'Castro'),
            ('Isabella', 'Morales')
        ]
        estudiantes_usuarios = []
        for i, (nom, ape) in enumerate(estudiantes_data):
            u = Usuario(nombre=nom, apellido=ape, username=f'est{i+1}',
                        email=f'est{i+1}@sena.edu.co', rol_id=roles['Estudiante'].id,
                        institucion_id=inst.id)
            u.set_password('est123')
            db.session.add(u)
            db.session.flush()
            estudiantes_usuarios.append(u)

        db.session.flush()

        print("Creando cursos...")
        cursos_data = [
            ('9°A', '9°', 'Mañana'), ('9°B', '9°', 'Mañana'), ('9°C', '9°', 'Tarde'),
            ('10°A', '10°', 'Mañana'), ('10°B', '10°', 'Tarde'),
            ('11°A', '11°', 'Mañana'), ('11°B', '11°', 'Tarde'),
        ]
        cursos = []
        for nombre, grado, jornada in cursos_data:
            c = Curso(nombre=nombre, grado=grado, jornada=jornada,
                      director_grupo='Por asignar', estado='Activo')
            db.session.add(c)
            cursos.append(c)
        db.session.flush()

        print("Creando estudiantes por curso...")
        for i, est_u in enumerate(estudiantes_usuarios):
            curso_idx = i % len(cursos)
            est = Estudiante(
                nombre=est_u.nombre, apellido=est_u.apellido,
                documento=f'100{i+1:06d}', curso_id=cursos[curso_idx].id,
                estado='Activo'
            )
            db.session.add(est)

        print("Creando categorías de actividades...")
        cats_data = [
            ('Salud física', 'Actividades de ejercicio y bienestar físico', '#10B981'),
            ('Salud mental', 'Actividades de bienestar emocional y psicológico', '#3B82F6'),
            ('Recreación', 'Actividades recreativas y de esparcimiento', '#F59E0B'),
            ('Cultura', 'Actividades artísticas y culturales', '#8B5CF6'),
            ('Pausas activas', 'Pausas activas durante la jornada', '#EF4444'),
        ]
        for nombre, desc, color in cats_data:
            cat = CategoriaActividad(nombre=nombre, descripcion=desc, color=color)
            db.session.add(cat)

        print("Creando actividades...")
        actividades_data = [
            ('Estiramientos matutinos', 'Rutina de estiramientos para iniciar el día', 'Pausas activas', 15,
             'Realizar movimientos de estiramiento suaves por 15 minutos'),
            ('Yoga para principiantes', 'Sesión de yoga básica para reducir el estrés', 'Salud mental', 45,
             'Traer tapete y ropa cómoda'),
            ('Caminata ecológica', 'Caminata por los alrededores de la sede', 'Salud física', 60,
             'Usar calzado cómoda y llevar agua'),
            ('Taller de pintura', 'Actividad artística grupal', 'Cultura', 90,
             'Los materiales serán suministrados'),
            ('Juegos recreativos', 'Juegos en grupo y dinámicas', 'Recreación', 40,
             'Participación activa de todos'),
            ('Meditación guiada', 'Sesión de meditación para reducir ansiedad', 'Salud mental', 30,
             'Ambiente silencioso recomendado'),
            ('Baile al ritmo', 'Sesión de baile para desestresar', 'Salud física', 45,
             'Traer ropa cómoda y botella de agua'),
            ('Lectura al aire libre', 'Espacio de lectura compartida', 'Cultura', 30,
             'Traer un libro de interés'),
            ('Pausa activa visual', 'Ejercicios para descanso visual', 'Pausas activas', 10,
             'Seguir las instrucciones en pantalla'),
            ('Respiración consciente', 'Técnicas de respiración para la calma', 'Salud mental', 15,
             'Buscar un lugar tranquilo'),
        ]
        actividades = []
        for titulo, desc, cat, dur, inst_text in actividades_data:
            a = Actividad(titulo=titulo, descripcion=desc, categoria=cat,
                          duracion=dur, instrucciones=inst_text, estado='Activa')
            db.session.add(a)
            actividades.append(a)
        db.session.flush()

        print("Creando programaciones...")
        today = date.today()
        programaciones_data = [
            (0, 0, 0, today + timedelta(days=1), time(8, 0), time(8, 15), 'Patio principal', 'Programada'),
            (1, 1, 1, today + timedelta(days=1), time(10, 0), time(10, 45), 'Sala de wellness', 'Programada'),
            (2, 3, 0, today + timedelta(days=2), time(7, 30), time(8, 30), 'Exteriores', 'Programada'),
            (4, 2, 1, today + timedelta(days=2), time(14, 0), time(14, 40), 'Auditorio', 'Programada'),
            (5, 4, 0, today + timedelta(days=3), time(9, 0), time(9, 30), 'Sala de wellness', 'Programada'),
            (6, 5, 1, today + timedelta(days=3), time(15, 0), time(15, 45), 'Patio principal', 'Programada'),
            (3, 6, 0, today + timedelta(days=4), time(10, 0), time(11, 30), 'Aula de arte', 'Programada'),
            (8, 0, 0, today + timedelta(days=4), time(11, 0), time(11, 10), 'Aula 101', 'Programada'),
            (7, 3, 1, today + timedelta(days=5), time(14, 0), time(14, 30), 'Biblioteca', 'Programada'),
            (9, 4, 0, today - timedelta(days=5), time(9, 0), time(9, 15), 'Sala de wellness', 'Finalizada'),
            (0, 1, 0, today - timedelta(days=4), time(8, 0), time(8, 15), 'Patio principal', 'Finalizada'),
            (2, 2, 1, today - timedelta(days=3), time(7, 30), time(8, 30), 'Exteriores', 'Finalizada'),
            (4, 5, 0, today - timedelta(days=2), time(14, 0), time(14, 40), 'Auditorio', 'Finalizada'),
            (6, 6, 1, today - timedelta(days=1), time(15, 0), time(15, 45), 'Patio principal', 'Finalizada'),
        ]
        for act_i, curso_i, doc_i, fec, hi, hf, lug, est in programaciones_data:
            p = Programacion(
                actividad_id=actividades[act_i].id,
                curso_id=cursos[curso_i].id,
                docente_id=[doc1.id, doc2.id][doc_i],
                fecha=fec, hora_inicio=hi, hora_final=hf,
                lugar=lug, estado=est
            )
            db.session.add(p)

        print("Creando encuesta...")
        enc = Encuesta(
            titulo='¿Cómo te sientes hoy?',
            descripcion='Encuesta de bienestar emocional para estudiantes',
            estado='Activa'
        )
        db.session.add(enc)
        db.session.flush()

        p1 = PreguntaEncuesta(encuesta_id=enc.id, texto='¿Cómo te sientes hoy?', tipo='seleccion_unica', orden=1)
        db.session.add(p1)
        db.session.flush()
        for i, (txt, val) in enumerate([
            ('Muy bien', 5), ('Bien', 4), ('Regular', 3), ('Un poco mal', 2), ('Mal', 1)
        ]):
            db.session.add(OpcionPregunta(pregunta_id=p1.id, texto=txt, valor=val, orden=i+1))

        p2 = PreguntaEncuesta(encuesta_id=enc.id, texto='¿Qué nivel de energía tienes hoy?', tipo='escala', orden=2)
        db.session.add(p2)
        db.session.flush()
        for i in range(1, 6):
            db.session.add(OpcionPregunta(pregunta_id=p2.id, texto=str(i), valor=i, orden=i))

        p3 = PreguntaEncuesta(encuesta_id=enc.id, texto='¿Hay algo que te esté preocupando actualmente?', tipo='texto', orden=3, requerida=False)
        db.session.add(p3)

        p4 = PreguntaEncuesta(encuesta_id=enc.id, texto='¿Te gustaría recibir apoyo o hablar con alguien?', tipo='seleccion_unica', orden=4)
        db.session.add(p4)
        db.session.flush()
        for i, txt in enumerate(['Sí', 'No', 'Tal vez']):
            db.session.add(OpcionPregunta(pregunta_id=p4.id, texto=txt, valor=i+1, orden=i+1))

        enc2 = Encuesta(
            titulo='Satisfacción con las actividades',
            descripcion='Encuesta para evaluar la calidad de las actividades programadas',
            estado='Activa'
        )
        db.session.add(enc2)
        db.session.flush()

        p5 = PreguntaEncuesta(encuesta_id=enc2.id, texto='¿Qué tan satisfecho estás con las actividades realizadas?', tipo='escala', orden=1)
        db.session.add(p5)
        db.session.flush()
        for i in range(1, 6):
            db.session.add(OpcionPregunta(pregunta_id=p5.id, texto=str(i), valor=i, orden=i))

        p6 = PreguntaEncuesta(encuesta_id=enc2.id, texto='¿Qué actividad disfrutaste más?', tipo='seleccion_unica', orden=2)
        db.session.add(p6)
        db.session.flush()
        for i, txt in enumerate(['Estiramientos', 'Yoga', 'Caminata', 'Pintura', 'Juegos']):
            db.session.add(OpcionPregunta(pregunta_id=p6.id, texto=txt, valor=i+1, orden=i+1))

        print("Creando propuestas...")
        propuestas_data = [
            ('Taller de cocina saludable', 'Propuesta realizar un taller donde los estudiantes aprendan a preparar comidas saludables', estudiantes_usuarios[0].id, 'Pendiente'),
            ('Día del deporte', 'Organizar un día completo de actividades deportivas inter-grados', estudiantes_usuarios[2].id, 'En evaluación'),
            ('Círculo de lectura', 'Crear un espacio quincenal de lectura y discusión de libros', estudiantes_usuarios[4].id, 'Aprobada'),
            ('Huerto escolar', 'Crear un pequeño huerto en la sede para actividades de jardinería terapéutica', estudiantes_usuarios[6].id, 'Pendiente'),
        ]
        for titulo, desc, est_id, estado in propuestas_data:
            p = Propuesta(titulo=titulo, descripcion=desc, estudiante_id=est_id, estado=estado)
            db.session.add(p)

        print("Creando alertas...")
        alertas_data = [
            ('Nueva actividad programada', 'Estiramientos matutinos programado para mañana', 'Nueva actividad', admin.id, False),
            ('Encuesta pendiente', 'Tienes una encuesta por responder: ¿Cómo te sientes hoy?', 'Encuesta pendiente', estudiantes_usuarios[0].id, False),
            ('Propuesta recibida', 'Se ha recibido una nueva propuesta: Taller de cocina', 'Propuesta recibida', coord.id, False),
            ('Actividad próxima', 'Yoga para principiantes comienza en 1 hora', 'Actividad próxima', doc1.id, True),
            ('Aviso institucional', 'Recuerde realizar las pausas activas diarias', 'Aviso institucional', admin.id, True),
        ]
        for titulo, desc, tipo, uid, leida in alertas_data:
            a = Alerta(titulo=titulo, descripcion=desc, tipo=tipo, usuario_id=uid, leida=leida)
            db.session.add(a)

        print("Creando periodos académicos...")
        pa1 = PeriodoAcademico(nombre='2026-I', fecha_inicio=date(2026, 1, 15), fecha_fin=date(2026, 6, 30), estado='Inactivo')
        pa2 = PeriodoAcademico(nombre='2026-II', fecha_inicio=date(2026, 7, 15), fecha_fin=date(2026, 12, 5), estado='Activo')
        db.session.add_all([pa1, pa2])

        db.session.commit()
        print("¡Datos iniciales creados exitosamente!")
        print("\nCredenciales de prueba:")
        print("  Admin:      admin / admin123")
        print("  Coordinador: coordinador / coord123")
        print("  Docente 1:  docente1 / doc123")
        print("  Docente 2:  docente2 / doc123")
        print("  Estudiante: est1 / est123")
        print("  Estudiante: est2 / est123")


if __name__ == '__main__':
    seed()
