import json
from datetime import datetime

class Periodo:
    def __init__(self, nombre, tiempoInicio, tiempoFin, parciales):
        self.nombre = nombre
        self.TiempoInicio = tiempoInicio
        self.TiempoFin = tiempoFin
        self.Parciales = parciales

        #Relacion con Asignaturas, se llena con las asignaturas que existan en Asignaturas.json
        self.Asignaturas = []

    def AsignarPeriodo(self):
        nombre = input("Ingrese el nombre del periodo a registrar: ")

        try:
            periodos = self.Abrir_JSON_lectura()

            #el periodo se identifica por su nombre, si ya existe no se registra de nuevo
            for p in periodos:
                if p["Nombre"].lower() == nombre.lower():
                    print(f"El periodo {nombre} ya existe en el sistema.")
                    return
                    
        except FileNotFoundError:
            pass

        tiempoInicio = self.PedirFecha("Ingrese la fecha de inicio del periodo (dd/mm/aaaa): ")
        tiempoFin = self.PedirFecha("Ingrese la fecha de fin del periodo (dd/mm/aaaa): ")

        #La fecha de fin debe ser posterior a la de inicio, si no, se vuelve a pedir
        while self.ConvertirFecha(tiempoFin) <= self.ConvertirFecha(tiempoInicio):
            print("La fecha de fin debe ser posterior a la fecha de inicio.")
            tiempoFin = self.PedirFecha("Ingrese la fecha de fin del periodo (dd/mm/aaaa): ")

        parciales = input("Ingrese la cantidad de parciales del periodo: ")

        while True:
            try:
                #intenta convertir el dato string en int, si arroja un ValueError pide el dato de nuevo
                parciales = int(parciales)
                if parciales <= 0:
                    raise ValueError
                break

            except ValueError:
                print("Tipo de dato no válido, ingrese solo números enteros mayores a 0")
                parciales = input("ingrese la cantidad de parciales: ")

        #Se piden las asignaturas que tendrá el periodo, validandolas contra Asignaturas.json
        asignaturas = self.SeleccionarAsignaturas()

        #se crea un diccionario para guardar todos los atributos ingresados anteriormente en 'periodo'
        periodo = {
            "Nombre": nombre,
            "Tiempo de inicio": tiempoInicio,
            "Tiempo de fin": tiempoFin,
            "Parciales": parciales,
            "Asignaturas": asignaturas
        }

        try:
            #si el json aun no se ha creado, captura el error y crea una nueva lista 'periodos'
            periodos = self.Abrir_JSON_lectura()
        except FileNotFoundError:
            periodos = []

        #Agrega el periodo a la lista general "periodos" y la guarda en el json
        periodos.append(periodo)
        self.Abrir_JSON_escritura(periodos)
        print("Periodo registrado correctamente.")

    def SeleccionarAsignaturas(self):
        #Abre el json de asignaturas para comprobar que las que ingrese el usuario existan
        try:
            disponibles = self.Abrir_JSON_asignaturas()
        except FileNotFoundError:
            disponibles = []

        if len(disponibles) == 0:
            print("no hay asignaturas registradas en el sistema, el periodo quedará sin asignaturas.")
            return []

        maximo = input("Ingrese el máximo de asignaturas que tendrá el periodo: ")

        while True:
            try:
                maximo = int(maximo)
                if maximo <= 0:
                    raise ValueError
                break
            except ValueError:
                print("Tipo de dato no válido, ingrese solo números enteros mayores a 0")
                maximo = input("Ingrese el máximo de asignaturas: ")

        seleccionadas = []

        #Se piden asignaturas hasta llegar al máximo, o hasta que el usuario presione Enter sin escribir nada
        while len(seleccionadas) < maximo:
            nombre = input(f"Ingrese el nombre de la asignatura {len(seleccionadas) + 1} de {maximo} (Presione Enter para terminar): ").strip()

            if nombre == "":
                break

            #Evita agregar dos veces la misma asignatura el periodo
            repetida = False
            for s in seleccionadas:
                if s["Nombre"].lower() == nombre.lower():
                    repetida = True
                    break

            if repetida:
                print(f"La asignatura '{nombre}' ya fue agregada a este periodo.")
                continue

            #Se busca la asignatura en el json, si existe se agrega el diccionario completo
            encontrada = False
            for a in disponibles:
                if a["Nombre"].lower() == nombre.lower():
                    seleccionadas.append(a)
                    encontrada = True
                    print(f"Asignatura '{a['Nombre']}' agregada al periodo.")
                    break

            if not encontrada:
                print(f"La asignatura '{nombre}' no existe en el sistema.")

        return seleccionadas

    def EditarPeriodo(self):
        nombre = input("ingrese el nombre del periodo a editar: ")

        try:
            #Abre el json en modo lectura
            periodos = self.Abrir_JSON_lectura()

            #bandera que indica si se encuentra el periodo
            encontrado = False

            for p in periodos:
                if p["Nombre"].lower() == nombre.lower():
                    nuevoNombre = input(f"Ingrese un nuevo nombre para {nombre}: ")

                    #si el nuevo nombre ya lo tiene otro periodo, no se permite el cambio
                    for otro in periodos:
                        if otro is not p and otro["Nombre"].lower() == nuevoNombre.lower():
                            print(f"El periodo {nuevoNombre} ya existe en el sistema.")
                            return
                        
                    nuevoInicio = self.PedirFecha("Ingrese la nueva fecha de inicio (dd/mm/aaaa): ")

                    nuevoFin = self.PedirFecha("Ingrese la nueva fecha de fin (dd/mm/aaaa):")

                    while self.ConvertirFecha(nuevoFin) <= self.ConvertirFecha(nuevoInicio):
                        print("La fecha de fin debe ser posterior a la fecha de inicio")
                        nuevoFin = self.PedirFecha("Ingrese la nueva fecha de fin (dd/mm/aaaa): ")

                    nuevosParciales = input("Ingrese la nueva cantidad de parciales: ")

                    while True:
                        try:
                            nuevosParciales = int(nuevosParciales)
                            if nuevosParciales <= 0:
                                raise ValueError
                            break

                        except ValueError:
                            print("tipó de dato no válido, ingrese solo números enteros mayores a 0")

                            nuevosParciales = input("Ingrese la cantidad de parciales: ")

                    #Opcionalmente se vuelven a elegir las asignaturas del periodo
                    respuesta =  input("¿Desea volver a seleccionar las asignaturas del periodo? (s/n)").lower()

                    while respuesta not in ("s", "n"):
                        respuesta = input("Ingrese 's' para sí o 'n' para no: ").lower()

                    if respuesta == "s":
                        p["Asignaturas"] = self.SeleccionarAsignaturas()

                    p["Nombre"] = nuevoNombre
                    p["Tiempo de inicio"] = nuevoInicio
                    p["Tiempo de fin"] = nuevoFin
                    p["Parciales"] = nuevosParciales
                    encontrado = True
                    break

            if encontrado:
                self.Abrir_JSON_escritura(periodos)
                print(f"Periodo '{nombre}' editado correctamente.")
            else:
                print(f"El periodo '{nombre} no se encontró en el sistema.")

        except FileNotFoundError:
            print("No hay periodos registrados en el sistema.")

    def EliminarPeriodo(self):
        nombre = input("Ingrese el nombre del periodo a eliminar: ")

        try:
            periodos = self.Abrir_JSON_lectura()
            encontrado = False

            #Se recorre cada periodo, si el nombre coincide se elimina de la lista
            for p in periodos:
                if p["Nombre"].lower() == nombre.lower():
                    periodos.remove(p)
                    encontrado = True
                    break

            if encontrado:
                self.Abrir_JSON_escritura(periodos)
                print(f"Periodo '{nombre}' eliminado correctamente.")
            else:
                print(f"El periodo '{nombre}' no existe en el sistema.")
        except FileNotFoundError:
            print("No hay periodo registrados en el sistema.")

    def PedirFecha(self, mensaje):
        #Pide una fecha hasta que tenga el formato dd/mm/aaaa y sea una fecha real
        while True:
            fecha = input(mensaje)
            try:
                datetime.strptime(fecha, "%d/%m/%Y")
                return fecha
            except ValueError:
                print("Fecha no válida, use el formato dd/mm/aaaa")

    def ConvertirFecha(self, fecha):
        return datetime.strptime(fecha, "%d/%m/%Y")

    def Abrir_JSON_lectura(self):
        with open("Datos/Periodos.json", "r", encoding="utf-8") as archivo:
            periodos = json.load(archivo)
            return periodos

    def Abrir_JSON_escritura(self, periodos):
        with open("Datos/Periodos.json", "w", encoding="utf-8") as archivo:
            json.dump(periodos, archivo, indent=4, ensure_ascii=False)

    def Abrir_JSON_asignaturas(self):
        with open("Datos/Asignaturas.json", "r", encoding="utf-8") as archivo:
            asignaturas = json.load(archivo)
            return asignaturas

if __name__ == "__main__":
    p = Periodo(None, None, None, None)
    p.EditarPeriodo()