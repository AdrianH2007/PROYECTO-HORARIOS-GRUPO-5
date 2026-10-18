class JordanaAcademica:
    def __init__(self, horaClase):
        self.horaClase = horaClase

    def editarHoraclase(self):
        self.horaClase = input("Ingrese la nueva hora de clases: ")
        print("Hora de clases modificada correctamente")
