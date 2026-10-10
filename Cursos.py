class Curso:

    def __init__(self, nombre, cantidadEstudiantes, nivel):
        self.nombre = nombre
        self.cantidadEstudiantes = cantidadEstudiantes
        self.nivel = nivel
        
    def ingresarCapacidad(self):
        self.cantidadEstudiantes = int(
            input("Ingrese la cantidad de estudiantes del curso: ")
        )
        print("Capacidad del curso registrada correctamente.")

    def asignarCurso(self):
        print(f"Curso '{self.nombre}' asignado correctamente.")

    def eliminarCurso(self):
        print(f"Curso '{self.nombre}' eliminado correctamente.")

    def editarCurso(self):
        print("¿Qué desea editar?")
        print("1. Nombre")
        print("2. Cantidad de estudiantes")
        print("3. Nivel")

        opcion = int(input("Ingrese una opción: "))

        match opcion:
            case 1:
                self.nombre = input("Ingrese el nuevo nombre del curso: ")

            case 2:
                self.cantidadEstudiantes = int(
                    input("Ingrese la nueva cantidad de estudiantes: ")
                )

            case 3:
                self.nivel = input("Ingrese el nuevo nivel del curso: ")

            case _:
                print("Opción no válida.")
                return

        print("Curso modificado correctamente.")