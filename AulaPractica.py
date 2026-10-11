from Aula import Aula

class AulaPractica(Aula):
    def __init__(self, nombre, cantidadMesas, cantidadSillas):
        super().__init__(nombre, cantidadMesas, cantidadSillas)
        self.cantidadEquipos = self.cantidadEquipos