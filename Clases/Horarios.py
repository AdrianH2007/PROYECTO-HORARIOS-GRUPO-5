import json
import os
from datetime import datetime
from Clases import Aula, Docente, JornadaAcademica


class Horario:

    RUTA = os.path.join("Datos", "horarios.json")   # mismo archivo que usa GestorHorario
    DIAS = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")

    def __init__(self, id, coordinador, carrera, asignatura, semestre, paralelo, dia,
                 jornada: JornadaAcademica.JordanaAcademica,
                 docente: Docente.Docente,
                 aula: Aula.Aula = None):
        self.id = str(id)
        self.coordinador = coordinador
        self.carrera = carrera
        self.asignatura = asignatura
        self.semestre = semestre
        self.paralelo = paralelo
        self.dia = dia
        self.jornada = jornada      
        self.docente = docente
        self.aula = aula           
        self.estado = "generado"
        self._origen = {}
    @property
    def horaInicio(self):
        return self.jornada.horaClase.split("-")[0]

    @property
    def horaFin(self):
        return self.jornada.horaClase.split("-")[1]

    @property
    def nombreDocente(self):
        return self.docente.nombre if self.docente else ""

    @property
    def nombreAula(self):
        return self.aula.nombre if self.aula else ""

    def editar(self):
        print("¿Que desea editar?")
        print("1. Docente\n2. Aula\n3. Hora de inicio\n4. Hora de fin\n5. Dia\n6. Paralelo")
        opcion = input("Ingrese una opcion: ").strip()


        copia = self._copiar()
        match opcion:
            case "1":
                nombre = input("Ingrese el nuevo docente: ").strip()
                copia.docente = Docente.Docente(nombre, [self.asignatura])
            case "2":
                nombre = input("Ingrese la nueva aula: ").strip()
                # mesas y sillas no se conocen aqui; el nombre es lo que identifica el aula
                copia.aula = Aula.Aula(nombre, 0, 0)
            case "3":
                inicio = self._pedirHora("Ingrese la nueva hora de inicio (HH:MM): ")
                copia.jornada = JornadaAcademica.JordanaAcademica(f"{inicio}-{self.horaFin}")
            case "4":
                fin = self._pedirHora("Ingrese la nueva hora de fin (HH:MM): ")
                copia.jornada = JornadaAcademica.JordanaAcademica(f"{self.horaInicio}-{fin}")
            case "5":
                dia = input(f"Ingrese el nuevo dia ({', '.join(self.DIAS)}): ").strip()
                dia = self._normalizarDia(dia)
                if dia is None:
                    print("Dia no valido.")
                    return
                copia.dia = dia
            case "6":
                copia.paralelo = input("Ingrese el nuevo paralelo: ").strip()
            case _:
                print("No se ingreso una respuesta esperada.")
                return

        if self._aMinutos(copia.horaFin) <= self._aMinutos(copia.horaInicio):
            print("La hora de fin debe ser posterior a la hora de inicio.")
            return
        if copia.hayCruce():
            return


        diaAnterior = self.dia
        self.__dict__.update(copia.__dict__)
        self.estado = "editado"
        self._guardar(diaAnterior)
        print("Se realizaron los cambios correctamente.")

    def visualizar(self):
        print(f"[{self.id}] {self.dia} {self.horaInicio}-{self.horaFin} | {self.asignatura} "
              f"| Docente: {self.nombreDocente} | Aula: {self.nombreAula or 'sin asignar'} "
              f"| {self.carrera}, {self.semestre} {self.paralelo} | {self.estado}")

    def borrar(self):
        datos = self._leerArchivo()
        info = datos.get(self.coordinador, {"horarios": {}, "eliminados": []})
        lista = info["horarios"].get(self.dia, [])
        info["horarios"][self.dia] = [h for h in lista if str(h["id"]) != self.id]
        info["eliminados"].append({**self.aDiccionario(), "_dia_original": self.dia})
        datos[self.coordinador] = info
        self._escribirArchivo(datos)
        print("Se elimino el horario correctamente.")

    def hayCruce(self):
        inicio = self._aMinutos(self.horaInicio)
        fin = self._aMinutos(self.horaFin)
        datos = self._leerArchivo()

        for coord, info in datos.items():
            for h in info.get("horarios", {}).get(self.dia, []):
                if str(h["id"]) == self.id:
                    continue
                if not (inicio < self._aMinutos(h["horaFin"]) and self._aMinutos(h["horaInicio"]) < fin):
                    continue
                if self.nombreDocente and h["docente"] == self.nombreDocente:
                    print(f"Cruce: el docente {h['docente']} ya tiene clase en ese horario.")
                    return True
                if self.nombreAula and h["aula"] == self.nombreAula:
                    print(f"Cruce: el aula {h['aula']} ya esta ocupada en ese horario.")
                    return True
                if (coord == self.coordinador and h["carrera"] == self.carrera
                        and h["semestre"] == self.semestre and h["paralelo"] == self.paralelo):
                    print("Cruce: ese paralelo ya tiene otra clase en ese horario.")
                    return True
        return False

    def aDiccionario(self):
        datos = dict(self._origen)
        # el coordinador genera horarios con la clave "materia"; se respeta la que ya tenia
        claveAsignatura = "materia" if "materia" in datos else "asignatura"
        datos.update({
            "id": self.id,
            "carrera": self.carrera,
            claveAsignatura: self.asignatura,
            "docente": self.nombreDocente,
            "aula": self.nombreAula,
            "semestre": self.semestre,
            "paralelo": self.paralelo,
            "horaInicio": self.horaInicio,
            "horaFin": self.horaFin,
            "estado": self.estado,
        })
        return datos

    @staticmethod
    def desdeDiccionario(d, coordinador, dia):
        asignatura = d.get("asignatura", d.get("materia", ""))
        semestre = d.get("semestre", d.get("nivel", ""))
        aulaNombre = d.get("aula", "")
        jornada = JornadaAcademica.JordanaAcademica(f"{d['horaInicio']}-{d['horaFin']}")
        docente = Docente.Docente(d["docente"], [asignatura])
        aula = Aula.Aula(aulaNombre, 0, 0) if aulaNombre else None
        h = Horario(d["id"], coordinador, d["carrera"], asignatura, semestre,
                    d["paralelo"], dia, jornada, docente, aula)
        h.estado = d.get("estado", "generado")
        h._origen = dict(d)
        return h

    @staticmethod
    def buscar(coordinador, idHorario):
        """Devuelve el Horario con ese id o None."""
        info = Horario._leerArchivo().get(coordinador, {})
        for dia, lista in info.get("horarios", {}).items():
            for d in lista:
                if str(d["id"]) == str(idHorario):
                    return Horario.desdeDiccionario(d, coordinador, dia)
        return None

    def _guardar(self, diaAnterior=None):
        datos = self._leerArchivo()
        info = datos.setdefault(self.coordinador, {"horarios": {}, "eliminados": []})
        if diaAnterior:
            info["horarios"][diaAnterior] = [
                h for h in info["horarios"].get(diaAnterior, []) if str(h["id"]) != self.id]
        lista = info["horarios"].setdefault(self.dia, [])
        for i, h in enumerate(lista):
            if str(h["id"]) == self.id:
                lista[i] = self.aDiccionario()
                break
        else:
            lista.append(self.aDiccionario())
        self._escribirArchivo(datos)

    @staticmethod
    def _leerArchivo():
        try:
            with open(Horario.RUTA, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _escribirArchivo(datos):
        with open(Horario.RUTA, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)


    def _copiar(self):
        copia = Horario(self.id, self.coordinador, self.carrera, self.asignatura,
                        self.semestre, self.paralelo, self.dia, self.jornada,
                        self.docente, self.aula)
        copia.estado = self.estado
        copia._origen = dict(self._origen)
        return copia

    @staticmethod
    def _normalizarDia(dia):
        quitar = str.maketrans("áéíóú", "aeiou")
        for d in Horario.DIAS:
            if d.lower().translate(quitar) == dia.lower().translate(quitar):
                return d
        return None

    @staticmethod
    def _pedirHora(mensaje):
        while True:
            hora = input(mensaje).strip()
            try:
                datetime.strptime(hora, "%H:%M")
                return hora
            except ValueError:
                print("Hora no valida, use el formato HH:MM")

    @staticmethod
    def _aMinutos(hora):
        h, m = hora.split(":")
        return int(h) * 60 + int(m)