import json

class Asignatura:
    def __init__(self, nombre, cantidadHoras, dias, paralelos):
        self.Nombre = nombre
        self.CantidadHoras = cantidadHoras
        self.Dias = dias
        self.Paralelos = paralelos

        #Relaciones pendientes a ingresar
        self.Docentes = []
        self.Horarios = []
        self.Cursos = []

    def RegistrarAsignatura(self):
            nombre = input("Ingrese el nombre de la asignatura a registrar: ")
            try:
                with open("Asignaturas.json", "r", encoding="utf-8") as archivo:
                    asignaturas = json.load(archivo)
            
                for a in asignaturas:
                    if a["Nombre"].lower() == nombre.lower():
                        print(f"La asignatura {nombre} ya existe en el sistema.")
                        return
        
            except FileNotFoundError:
                pass
            
            cantidadHoras = input("Ingrese la cantidad de horas de la asignatura durante el periodo académico: ")
            while True:
                try:
                    cantidadHoras = int(cantidadHoras)
                    break
                except ValueError:
                    print("Tipo de dato no válido, ingrese solo números enteros")
                    cantidadHoras = input("Ingrese la cantidad de horas: ")
            
            
            cantidadDias = input("Ingrese la cantidad de dias a la semana: ")
            while True:
                try:
                    cantidadDias = int(cantidadDias)
                    break
                except ValueError:
                    print("Tipo de dato no válido, ingrese solo números enteros")
                    cantidadDias = input("Ingrese la cantidad de Dias a la semana: ")

            #Se guardan los dias que se impartiran la asignatura a travez de una lista
            dias = []
            for i in range(cantidadDias):
                dato = input(f"Ingrese el dia {i + 1}: ")
                dias.append(dato)
            
            cantParalelos = input("Ingrese cuántos paralelos recibirán la asignatura: ")
            while True:
                try:
                    cantParalelos = int(cantParalelos)
                    break
                except ValueError:
                    print("Tipo de dato no válido, ingrese solo números enteros")
                    cantParalelos = input("Ingrese la cantidad de Paralelos: ")
            #lo mismo que en dias, los paralelos se guardan en lista
            paralelos = []
            for i in range(cantParalelos):
                dato = input(f"Ingrese el paralelo {i + 1}: ")
                paralelos.append(dato)
                
            #Se crea un diccionario para guardra todos los atributos ingresados
            asignatura = {
                "Nombre": nombre, 
                "Cantidad de Horas": cantidadHoras, 
                "Cantidad de dias": cantidadDias, 
                "Dias que se imparte": dias, 
                "Cantidad de paralelos": cantParalelos, 
                "Paralelos": paralelos
            }
            
            try:
                with open("Asignaturas.json", "r", encoding="utf-8") as archivo:
                    asignaturas = json.load(archivo)
            except FileNotFoundError:    
                asignaturas = []

            #Agrega la nueva asignatura a la lista general "Asignaturas"
            asignaturas.append(asignatura)

            with open("Asignaturas.json", "w", encoding="utf-8") as archivo:
                json.dump(asignaturas, archivo, indent=4, ensure_ascii=False)

            print("Asignatura registrada correctamente.")

    def EditarAsignatura(self):
        nombre = input("Ingrese el nombre de la asignatura a editar: ")
        nuevoNombre = input(f"Ingrese un nuevo nombre para {nombre}: ")

        try:
            #abre el json en modo lectura
            with open("Asignaturas.json", "r", encoding="utf-8") as archivo:
                asignaturas = json.load(archivo)

            #inicializa una variable encontrado en falso
            encontrado = False

            for a in asignaturas:
                if a["Nombre"].lower() == nombre.lower():
                    a["Nombre"] = nuevoNombre
                    encontrado = True
                    break

            if encontrado:
                with open("Asignaturas.json", "w", encoding="utf-8") as archivo:
                    json.dump(asignaturas, archivo, indent=4, ensure_ascii=False)
                    print(f"Asignatura {nombre} fué editada a {nuevoNombre} correctamente.")
            else:
                print(f"La asignatura '{nombre}' no se encontró en el sistema.")
        except FileNotFoundError:
            print("No hay asignaturas registradas en el sistema.")    


    def ConsultarAsignatura(self):
        nombre = input("Ingrese el nombre de la asignatura a consultar: ")

        try:
            with open("Asignaturas.json", "r", encoding="utf-8") as archivo:
                asignaturas = json.load(archivo)
            encontrado = False

            #Hace el mismo recorrido, guarda el resultado de la condicion y pasa a imprimir si se cumple en el if
            #else si no lo encuentra
            for a in asignaturas:
                if a["Nombre"].lower() == nombre.lower():        
                    print(a)
                    encontrado = True
                    break

            if not encontrado:        
                print("Asignatura no encontrada en el sistema.")

        except FileNotFoundError:    
            print("No hay asignaturas registradas en el sistema.")    

    def EliminarAsignatura(self):
        nombre = input("Ingrese el nombre de la asignatura a eliminar: ")
        try:
            #abre el json en modo lectura
            with open("Asignaturas.json", "r", encoding="utf-8") as archivo:
                asignaturas = json.load(archivo)
            #una vez abierto json, en la lista asignaturas se recorre cada asignatura, 
            #si el nombre es diferente no hace nada, si encuentra un nombre igual vuelve a abrir el json en modo escritura y lo elimina
            asignaturas = [a for a in asignaturas if a["Nombre"] != nombre]
            with open("Asignaturas.json", "w", encoding="utf-8") as archivo:
                json.dump(asignaturas, archivo, indent=4, ensure_ascii=False)
            print(f"Asignatura '{nombre}' eliminada correctamente.")

        except FileNotFoundError:
            print("No hay asignaturas registradas en el sistema.")    
