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
                asignaturas = self.Abrir_JSON_lectura()
            
                for a in asignaturas:
                    if a["Nombre"].lower() == nombre.lower():
                        print(f"La asignatura {nombre} ya existe en el sistema.")
                        return
        
            except FileNotFoundError:
                pass
            
            cantidadHoras = input("Ingrese la cantidad de horas de la asignatura durante el periodo académico: ")

            while True:
                try:
                    #intenta convertir el dato string en int, si funciona rompe el ciclo,
                    #si arroja un ValueError, pedira de nuevo la cantidad hasta que el valor se convierta a entero correctamente.
                    cantidadHoras = int(cantidadHoras)
                    break

                except ValueError:
                    print("Tipo de dato no válido, ingrese solo números enteros")
                    cantidadHoras = input("Ingrese la cantidad de horas: ")
            
            
            cantidadDias = input("Ingrese la cantidad de dias a la semana: ")

            while True:
                try:
                    #Aqui pasa lo mismo que la cantidad de horas.
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
                
            #Se crea un diccionario para guarda todos los atributos ingresados anteriormente en 'asignatura'
            asignatura = {
                "Nombre": nombre, 
                "Cantidad de Horas": cantidadHoras, 
                "Cantidad de dias": cantidadDias, 
                "Dias que se imparte": dias, 
                "Cantidad de paralelos": cantParalelos, 
                "Paralelos": paralelos
            }
            
            try: 
                #intentara capturar el error si en este caso el jsn aun no se ha creado,
                # si captura el error, creara una nueva lista 'asignaturas' para luego guardarla en el json.              
                asignaturas = self.Abrir_JSON_lectura()
            except FileNotFoundError:    
                asignaturas = []

            #Agrega la estructura de la lista 'asignatura' a la lista general "Asignaturas"
            asignaturas.append(asignatura)

            #guarda lo que se agrego a la lista asignaturas en el json.
            self.Abrir_JSON_escritura(asignaturas)
            print("Asignatura registrada correctamente.")

    def EditarAsignatura(self):
        nombre = input("Ingrese el nombre de la asignatura a editar: ")

        try:
            #abre el json en modo lectura
            asignaturas = self.Abrir_JSON_lectura()

            #inicializa una variable 'encontrado' que sirve como bandera, en falso
            encontrado = False

            for a in asignaturas:
                if a["Nombre"].lower() == nombre.lower():
                    nuevoNombre = input(f"Ingrese un nuevo nombre para {nombre}: ")
                    a["Nombre"] = nuevoNombre
                    encontrado = True
                    break

            if encontrado:
                self.Abrir_JSON_escritura(asignaturas)
                print(f"Asignatura '{nombre}' fué editada a '{nuevoNombre}' correctamente.")
            else:
                print(f"La asignatura '{nombre}' no se encontró en el sistema.")
        except FileNotFoundError:
            print("No hay asignaturas registradas en el sistema.")    


    def ConsultarAsignatura(self):
        nombre = input("Ingrese el nombre de la asignatura a consultar: ")

        try:
            asignaturas = self.Abrir_JSON_lectura()
            encontrado = False

            #Hace el mismo recorrido que el metodo eliminar, pero esta vez muestra la asignatura encontrada
            #y la bandera pasa a ser true, si se niega la bandera imprime que la asignatura no se encontro.
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
            asignaturas = self.Abrir_JSON_lectura()
            #una vez abierto json, en la lista asignaturas se recorre cada asignatura con ciclo for, 
            #si el nombre es diferente no hace nada, si encuentra un nombre igual vuelve a abrir el json en modo escritura y lo elimina
            encontrado = False

            for a in asignaturas:
                if a["Nombre"].lower() == nombre.lower():
                    asignaturas.remove(a)
                    encontrado = True
                    break             

            if encontrado:
                self.Abrir_JSON_escritura(asignaturas)
                print(f"Asignatura '{nombre}' eliminada correctamente.")
            else:
                print(f"La asignatura '{nombre}' no existe en el sistema.")

        except FileNotFoundError:
            print("No hay asignaturas registradas en el sistema.")    

    def Abrir_JSON_lectura(self):
        with open("Datos/Asignaturas.json", "r", encoding="utf-8") as archivo:
            asignaturas = json.load(archivo)
            return asignaturas
        
    def Abrir_JSON_escritura(self, asignaturas):
        with open("Datos/Asignaturas.json", "w", encoding="utf-8") as archivo:
            json.dump(asignaturas, archivo, indent=4, ensure_ascii=False)