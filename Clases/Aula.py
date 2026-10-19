from Persistencia import GestorAula
import json


class Aula:
    def __init__(self, nombre, cantidadMesas, cantidadSillas):
        self.nombre = nombre
        self.cantidadMesas = cantidadMesas
        self.cantidadSillas = cantidadSillas
        self.estado = "Activo"
    @staticmethod
    def ingresarCapacidad():
        mesas = int(input("Ingrese la cantidad de meses: "))
        sillas = int(input("Ingrese la cantidad de sillas"))
        return mesas, sillas

    @staticmethod
    def consultarAula():
        nombre = input("Ingrese el nombre del aula:")
        aulas = Aula.Abrir_JSON_lectura()
        for tipo in ("teorica", "practica"):
            for id_aula, datos in aulas.get(tipo, {}).items():
                if datos.get("nombre") == nombre:
                    print("Aula", nombre)
                    for dato in datos:
                        print(dato + ":", datos[dato])
                    return
        print("El aula que busca no existe")

    @staticmethod
    def asignarAula(gestorHorario, idHorario):
        nombre = input("Ingrese el nombre del aula ")
        aulas = Aula.Abrir_JSON_lectura()
        if nombre not in aulas:
            print("El aula que busca no existe")
            return
        for dia in gestorHorario.horarios:
            for h in gestorHorario.horarios[dia]:
                if str(h["id"]) == str(idHorario):
                    aulaAnterior = h["aula"]
                    h["aula"] = nombre
                    if gestorHorario._verificarCruce(h, dia, idExcluir =idHorario):
                        h["aula"] = aulaAnterior
                        return
                    gestorHorario.guardarHorarios()
                    print("Se agino el aula al horario")
                    return
                print("No se encontro el horario")

    @staticmethod
    def editarAula():
        nombre = input("Ingrese el nombre del aula que desea editar: ")
        aulas = Aula.Abrir_JSON_lectura()
        aula = None
        tipo = None
        for t in ("teorica", "practica"):
            for id_aula, datos in aulas.get(t, {}).items():
                if datos.get("nombre") == nombre:
                    aula = datos
                    tipo = t
        if aula is None:
            print("El aula que busca no existe ")
            return
        print("Que desea editar")
        print("1.Mesas"
              "2.sillas"
              "3.Equipos")
        opcion = int(input())
        match opcion:
            case 1:
                aula["mesas"] = int(input("Ingrese la nueva cantidad de mesas: "))
            case 2:
                aula["sillas"] = int(input("Ingrese la nueva cantidad de sillas: "))
            case 3:
                if tipo == "practica":
                    aula["equipos"] = int(input("Ingrese la nueva cantidad de equipos: "))
                else:
                    print("Esta aula no es un laboratorio")
                    return
            case _:
                print("No se ingreso una de las 3 respuestas")
                return
        Aula.Abrir_JSON_escritura(aulas)
        print("Se realizaon los cambios correctamente")

    @staticmethod
    def eliminarAula():
        nombre = input("Ingrese el nombre del aula que quiera eliminar: ")
        aulas = Aula.Abrir_JSON_lectura()
        tipo = None
        id_eliminar = None
        for t in ("teorica", "practica"):
            for id_aula, datos in aulas.get(t, {}).items():
                if datos.get("nombre") == nombre:
                    tipo = t
                    id_eliminar = id_aula
        if tipo is None:
            print("El aula que se busca no existe en el sistema")
            return
        f = open("Datos/horarios.json", "r")
        horarios = json.load(f)
        f.close
        for coord in horarios:
            for dia in horarios[coord]["horarios"]:
                for h in horarios[coord]["horarios"][dia]:
                    if h["aula"] == nombre:
                        print("No se puede el aula porque esta en un horario")
                        return
        aulas[tipo].pop(id_eliminar)
        Aula.Abrir_JSON_escritura(aulas)
        print("Se a eliminado el aula")

    @staticmethod
    def Abrir_JSON_lectura():
        with open("Datos/aulas.json", "r", encoding="utf-8") as archivo:
            aulas = json.load(archivo)
            return aulas

    @staticmethod
    def Abrir_JSON_escritura(aulas):
        with open("Datos/aulas.json", "w", encoding="utf-8") as archivo:
            json.dump(aulas, archivo, indent=4, ensure_ascii=False)