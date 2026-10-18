from Clases.Aula import Aula

class AulaPractica(Aula):
    def __init__(self, nombre, cantidadMesas, cantidadSillas, cantidadEquipos):
        super().__init__(nombre, cantidadMesas, cantidadSillas)
        self.cantidadEquipos = cantidadEquipos