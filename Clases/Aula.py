import json


class Aula:
    def __init__(self, nombre, cantidadMesas, cantidadSillas):
        super().__init__
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
        f = open("aulas,json", "r")
        aulas = json.load(f)
        f.close
        if nombre in aulas:
            print("Aula", nombre)
            for dato in aulas[nombre]:
                print(dato + ":", aulas [nombre][dato])
        else:
            print("El aula que busca no existe")

    @staticmethod
    def asignarAula(gestorHorario, idHorario):
        nombre = input("Ingrese el nombre del aula ")
        f = open("aulas.json", "r")
        aulas = json.load(f)
        f.close
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
        f = open("aulas.json", "r")
        aulas = json.load(f)
        f.close()
        if nombre not in aulas:
            print("El aula que busca no existe ")
            return
        print("Que desea editar")
        print("1.Mesas"
              "2.sillas"
              "3.Equipos")
        opcion = int(input())
        match opcion:
            case 1:
                aulas[nombre]["mesas"] = int(input("Ingrese la nueva cantidad de mesas: "))
            case 2:
                aulas[nombre]["sillas"] = int(input("Ingrese la nueva cantidad de sillas: "))
            case 3:
                if aulas[nombre]["tipo"] == "AulaPractica":
                    aulas[nombre]["equipos"] = int(input("Ingrese la nueva cantidad de equipos: "))
                else:
                    print("Esta aula no es un laboratorio")
                    return
            case _:
                print("No se ingreso una de las 3 respuestas")
                return
        f = open("aulas.json", "w")
        json.dump(aulas, f, indent =4)
        f.close()
        print("Se realizaon los cambios correctamente")

    @staticmethod
    def eliminarAula():
        nombre = input("Ingrese el nombre del aula que quiera eliminar: ")
        f = open("aulas.json", "r")
        aulas = json.load(f)
        f.close()
        if nombre not in aulas:
            print("El aula que se busca no existe en el sistema")
            return
        f = open("horarios.json", "r")
        horarios = json.load(f)
        f.close
        for coord in horarios:
            for dia in horarios[coord]["horarios"]:
                for h in horarios[coord]["horarios"][dia]:
                    if h["aulas"] == nombre:
                        print("No se puede el aula porque esta en un horario")
                        return
        aulas.pop(nombre)
        f = open("aulas.json", "w")
        json.dump(aulas, f, indent=4)
        f.close()
        print("Se a eliminado el aula")