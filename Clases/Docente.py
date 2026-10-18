from asignaturas import Asignatura

class Docente:
    def __init__(self, nombre, asignaturas : Asignatura):
        self.nombre = nombre
        self.asignaturas = asignaturas