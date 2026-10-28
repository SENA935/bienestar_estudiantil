import os, sys
from datetime import datetime, date, time, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from app import create_app
from app.extensions import db
from app.models.rol import Rol
from app.models.institucion import Institucion
from app.models.sede import Sede
from app.models.usuario import Usuario
from app.models.curso import Curso
from app.models.estudiante import Estudiante
from app.models.categoria_actividad import CategoriaActividad
from app.models.actividad import Actividad
from app.models.programacion import Programacion
from app.models.actividad_realizada import ActividadRealizada
from app.models.encuesta import Encuesta
from app.models.pregunta_encuesta import PreguntaEncuesta
from app.models.opcion_pregunta import OpcionPregunta
from app.models.propuesta import Propuesta
from app.models.alerta import Alerta


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if Rol.query.count() > 0:
            print("La base de datos ya contiene informacion; se omite el seed")
            return

        roles = [Rol(nombre='Administrador', descripcion='Acceso completo'), Rol(nombre='Coordinador', descripcion='Gestiona actividades y usuarios'), Rol(nombre='Docente', descripcion='Gestiona actividades de sus cursos'), Rol(nombre='Profesor', descripcion='Profesor de asignatura'), Rol(nombre='Director de grupo', descripcion='Director de grupo escolar'), Rol(nombre='Estudiante', descripcion='Participa en actividades')]
        db.session.add_all(roles)
        db.session.flush()

        inst = Institucion(nombre='IED San Martín', nit='890123456-7', telefono='3101234567', email='info@sanmartin.edu.co')
        db.session.add(inst)
        db.session.flush()
        db.session.add(Sede(nombre='Sede Principal', direccion='Calle 50 #15-20', institucion_id=inst.id, telefono='3101234567'))
        db.session.flush()

        admin = Usuario(nombre='Carlos', apellido='Rodríguez', username='admin', email='admin@colegio.com', rol_id=1, institucion_id=inst.id)
        admin.set_password('admin123')
        coord = Usuario(nombre='María', apellido='López', username='coordinador', email='coord@colegio.com', rol_id=2, institucion_id=inst.id)
        coord.set_password('coord123')
        doc1 = Usuario(nombre='Pedro', apellido='García', username='docente1', email='doc1@colegio.com', rol_id=3, institucion_id=inst.id)
        doc1.set_password('doc123')
        doc2 = Usuario(nombre='Ana', apellido='Martínez', username='docente2', email='doc2@colegio.com', rol_id=3, institucion_id=inst.id)
        doc2.set_password('doc123')
        db.session.add_all([admin, coord, doc1, doc2])

        prof = Usuario(nombre='Roberto', apellido='Díaz', username='profesor1', email='prof@colegio.com', rol_id=4, institucion_id=inst.id)
        prof.set_password('prof123')
        director = Usuario(nombre='Lucía', apellido='Fernández', username='director1', email='director@colegio.com', rol_id=5, institucion_id=inst.id)
        director.set_password('dir123')
        db.session.add_all([prof, director])

        est_usuarios = []
        for i, (n, a) in enumerate([('Juan','Pérez'),('Laura','Sánchez'),('Andrés','Ramírez'),('Sofía','Torres'),('Diego','Morales'),('Camila','Vargas'),('Mateo','Herrera'),('Valentina','Castro'),('Santiago','Ruiz'),('Isabella','Mendoza')]):
            u = Usuario(nombre=n, apellido=a, username=f'est{i+1}', email=f'est{i+1}@colegio.com', rol_id=6, institucion_id=inst.id)
            u.set_password('est123')
            db.session.add(u)
            est_usuarios.append(u)
        db.session.flush()

        cursos = []
        for n, g, j in [('9°A','9°','Mañana'),('9°B','9°','Mañana'),('9°C','9°','Tarde'),('10°A','10°','Mañana'),('10°B','10°','Tarde'),('11°A','11°','Mañana'),('11°B','11°','Mañana')]:
            c = Curso(nombre=n, grado=g, jornada=j, director_grupo='Docente Asignado')
            db.session.add(c)
            cursos.append(c)
        db.session.flush()

        for i, eu in enumerate(est_usuarios):
            db.session.add(Estudiante(nombre=eu.nombre, apellido=eu.apellido, documento=f'100{i+1}234', curso_id=cursos[i % len(cursos)].id))

        cats = [CategoriaActividad(nombre='Salud física', descripcion='Actividades físicas', color='#16a34a'),
                CategoriaActividad(nombre='Salud mental', descripcion='Bienestar emocional', color='#087f8c'),
                CategoriaActividad(nombre='Recreación', descripcion='Actividades recreativas', color='#f59e0b'),
                CategoriaActividad(nombre='Cultura', descripcion='Actividades culturales', color='#9333ea'),
                CategoriaActividad(nombre='Pausas activas', descripcion='Pausas saludables', color='#06b6d4')]
        db.session.add_all(cats)
        db.session.flush()

        acts = []
        for t, d, ci, dur in [('Yoga para estudiantes','Sesión de yoga relajante',cats[1].id,30),('Caminata saludable','Caminata por instalaciones',cats[0].id,45),('Juegos recreativos','Juegos en grupo',cats[2].id,40),('Pausa activa de estiramiento','Estiramientos',cats[4].id,15),('Taller de pintura','Actividad artística',cats[3].id,60),('Meditación guiada','Sesión de meditación',cats[1].id,20),('Circuito deportivo','Circuito de ejercicios',cats[0].id,50),('Danza libre','Expresión corporal',cats[2].id,45)]:
            a = Actividad(titulo=t, descripcion=d, categoria_id=ci, duracion=dur, instrucciones='Seguir indicaciones del docente')
            db.session.add(a)
            acts.append(a)
        db.session.flush()

        today = date.today()
        progs = []
        for i in range(7):
            p = Programacion(actividad_id=acts[i % len(acts)].id, curso_id=cursos[i].id, docente_id=doc1.id if i % 2 == 0 else doc2.id, fecha=today + timedelta(days=i), hora_inicio=time(8 + (i % 4), 0), hora_final=time(8 + (i % 4), 45), lugar='Patio principal' if i % 2 == 0 else 'Salón 3')
            db.session.add(p)
            progs.append(p)
        db.session.flush()

        for i in range(3):
            db.session.add(ActividadRealizada(programacion_id=progs[i].id, fecha=today - timedelta(days=i+1), hora_inicio=time(8,0), hora_final=time(8,45), observaciones='Actividad completada exitosamente'))

        enc = Encuesta(titulo='¿Cómo te sientes hoy?', descripcion='Encuesta de bienestar emocional')
        db.session.add(enc)
        db.session.flush()

        preg1 = PreguntaEncuesta(encuesta_id=enc.id, texto='¿Cómo te sientes hoy?', tipo='seleccion_unica', orden=0)
        db.session.add(preg1)
        db.session.flush()
        for i, t in enumerate(['😊 Muy bien','🙂 Bien','😐 Regular','😟 Un poco mal','😞 Mal']):
            db.session.add(OpcionPregunta(pregunta_id=preg1.id, texto=t, valor=i, orden=i))

        preg2 = PreguntaEncuesta(encuesta_id=enc.id, texto='¿Qué nivel de energía tienes hoy?', tipo='escala', orden=1)
        db.session.add(preg2)
        db.session.flush()
        for i in range(1, 6):
            db.session.add(OpcionPregunta(pregunta_id=preg2.id, texto=str(i), valor=i, orden=i))

        db.session.add(PreguntaEncuesta(encuesta_id=enc.id, texto='¿Hay algo que te esté preocupando actualmente?', tipo='texto', orden=2, requerida=False))

        preg4 = PreguntaEncuesta(encuesta_id=enc.id, texto='¿Te gustaría recibir orientación o hablar con alguien?', tipo='seleccion_unica', orden=3)
        db.session.add(preg4)
        db.session.flush()
        for i, t in enumerate(['Sí','No','Tal vez']):
            db.session.add(OpcionPregunta(pregunta_id=preg4.id, texto=t, valor=i, orden=i))

        for t, d, es in [('Taller de muralismo','Propongo un taller de muralismo','Pendiente'),('Club de lectura','Club de lectura semanal','Pendiente'),('Circuito de bienestar','Circuitos de actividades','En evaluación')]:
            db.session.add(Propuesta(titulo=t, descripcion=d, estudiante_id=est_usuarios[0].id, estado=es))

        for t, d, tp, l in [('Nueva actividad','Se programó yoga','nueva_actividad',False),('Encuesta pendiente','Responde la encuesta','encuesta_pendiente',False),('Propuesta recibida','Nuevo estudiante propuso','propuesta_recibida',True),('Actividad próxima','Caminata mañana 8am','actividad_proxima',False)]:
            db.session.add(Alerta(titulo=t, descripcion=d, tipo=tp, usuario_id=admin.id, leida=l))

        db.session.commit()
        print("Base de datos sembrada correctamente")
        print("\nCredenciales:")
        print("  Administrador:  admin@colegio.com / admin123")
        print("  Coordinador:    coord@colegio.com / coord123")
        print("  Docente:        doc1@colegio.com / doc123")
        print("  Profesor:       prof@colegio.com / prof123")
        print("  Director grupo: director@colegio.com / dir123")
        print("  Estudiante:     est1@colegio.com / est123")


if __name__ == '__main__':
    seed()
