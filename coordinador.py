import json
import Usuario

class CoordinadorAcademico(Usuario.Usuario):
    DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    def __init__(self, usuario, contrasena):
        super().__init__(usuario, contrasena)

        self.sesionActiva = False
        self.horarios = {
            "Lunes": [],
            "Martes": [],
            "Miércoles": [],
            "Jueves": [],
            "Viernes": []
        }
        self.horariosEliminados = []
        self.contadorID = 1
        self.cargarHorarios()
    
    def cargarHorarios(self):
        try:
            with open("horarios.json", "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            usuario_datos = datos.get(self.usuario, {})
            self.horarios = usuario_datos.get("horarios", {
                "Lunes": [], "Martes": [], "Miércoles": [], "Jueves": [], "Viernes": []
            })
            self.horariosEliminados = usuario_datos.get("eliminados", [])

            max_id = 0
            for dia in self.DIAS:
                for h in self.horarios.get(dia, []):
                    if int(h["id"]) > max_id:
                        max_id = int(h["id"])
            for h in self.horariosEliminados:
                if int(h["id"]) > max_id:
                    max_id = int(h["id"])

            self.contadorID = max_id + 1

            if any(self.horarios.values()) or self.horariosEliminados:
                print("Horarios cargados correctamente.")

        except FileNotFoundError:
            self.horarios = {d: [] for d in self.DIAS}
            self.horariosEliminados = []

    def guardarHorarios(self):
        try:
            with open("horarios.json", "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            datos = {}

        datos[self.usuario] = {
            "horarios": self.horarios,
            "eliminados": self.horariosEliminados
        }

        with open("horarios.json", "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

        print("Horarios guardados correctamente.")

    def convertirHora(self, hora):
        partes = hora.split(":")
        if len(partes) != 2:
            return -1
        try:
            h = int(partes[0])
            m = int(partes[1])
        except ValueError:
            return -1

        if h < 0 or h > 23 or m < 0 or m > 59:
            return -1

        return h * 60 + m

    def _verificarCruce(self, horarioEvaluar, dia, idExcluir=None):

        inicio1 = self.convertirHora(horarioEvaluar["horaInicio"])
        fin1 = self.convertirHora(horarioEvaluar["horaFin"])
        lista_dia = self.horarios.get(dia, [])

        for otro in lista_dia:
            if idExcluir is not None and str(otro["id"]) == str(idExcluir):
                continue

            inicio2 = self.convertirHora(otro["horaInicio"])
            fin2 = self.convertirHora(otro["horaFin"])

            hayCruce = inicio1 < fin2 and inicio2 < fin1

            if hayCruce:
                if horarioEvaluar["docente"] == otro["docente"]:
                    print(f"Conflicto el día {dia}: El docente '{horarioEvaluar['docente']}' ya tiene clase a esa hora.")
                    return True
                if horarioEvaluar["aula"] == otro["aula"]:
                    print(f"Conflicto el día {dia}: El aula '{horarioEvaluar['aula']}' está ocupada a esa hora.")
                    return True
                if (horarioEvaluar["carrera"] == otro["carrera"] and 
                    horarioEvaluar["semestre"] == otro["semestre"] and 
                    horarioEvaluar["paralelo"] == otro["paralelo"]):
                    print(f"Conflicto el día {dia}: El grupo (Carrera, Semestre, Paralelo) ya tiene otra clase asignada a esa hora.")
                    return True
        return False

    def iniciarSesion(self, contrasena=None):
        if hasattr(self, 'estado') and self.estado != "Activo":
            print("El usuario está inactivo.")
            return False
        if contrasena is not None and contrasena != self.contrasena:
            print("Contraseña incorrecta.")
            return False

        self.sesionActiva = True
        print("Sesión iniciada correctamente.")
        return True

    def cerrarSesion(self):
        self.sesionActiva = False
        print("Sesión cerrada correctamente.")
        return True

    def ingresarDatos(self, datos):
        if not self.sesionActiva:
            print("Debe iniciar sesión para ingresar datos.")
            return False

        CAMPOS = ["carrera", "asignatura", "docente", "aula", "semestre", "paralelo", "dia", "horaInicio", "horaFin"]
        for campo in CAMPOS:
            if campo not in datos or not str(datos[campo]).strip():
                print(f"El campo '{campo}' es obligatorio.")
                return False

        dia = datos["dia"].strip()
        if dia not in self.DIAS:
            print(f"El día '{dia}' no es válido. Debe ser uno de: {self.DIAS}")
            return False

        inicio = self.convertirHora(datos["horaInicio"])
        fin = self.convertirHora(datos["horaFin"])

        if inicio == -1 or fin == -1 or inicio >= fin:
            if inicio >= fin:
                print("La hora de inicio debe ser menor que la hora de fin.")
            return False

        horario = {
            "id": str(self.contadorID),
            "carrera": datos["carrera"].strip(),
            "asignatura": datos["asignatura"].strip(),
            "docente": datos["docente"].strip(),
            "aula": datos["aula"].strip(),
            "semestre": datos["semestre"].strip(),
            "paralelo": datos["paralelo"].strip(),
            "horaInicio": datos["horaInicio"],
            "horaFin": datos["horaFin"],
            "estado": "pendiente"
        }

        if self._verificarCruce(horario, dia):
            return False

        self.horarios[dia].append(horario)
        self.contadorID += 1
        self.guardarHorarios()

        print(f"Horario registrado correctamente para el día {dia}.")
        return horario

    def generarHorarios(self):
        if not self.sesionActiva:
            print("Debe iniciar sesión para generar horarios.")
            return False

        if not any(self.horarios.values()):
            print("No hay horarios registrados.")
            return False

        for dia, lista in self.horarios.items():
            for h in lista:
                if self._verificarCruce(h, dia, idExcluir=h["id"]):
                    print(f"Error de cruce en el día {dia} (ID {h['id']}).")
                    return False

        for dia, lista in self.horarios.items():
            for h in lista:
                h["estado"] = "generado"

        self.guardarHorarios()
        print("Los horarios semanales se generaron correctamente.")
        return True

    def modificarHorario(self, idHorario, cambios):
        if not self.sesionActiva:
            print("Debe iniciar sesión para modificar horarios.")
            return False

        horario_encontrado = None
        dia_actual = None
        for d, lista in self.horarios.items():
            for h in lista:
                if str(h["id"]) == str(idHorario):
                    horario_encontrado = h
                    dia_actual = d
                    break
            if horario_encontrado:
                break

        if not horario_encontrado:
            print("No se encontró el horario.")
            return False

        nuevo_dia = cambios.get("dia", dia_actual).strip()
        if nuevo_dia not in self.DIAS:
            print("Día inválido.")
            return False

        nuevo_horario = horario_encontrado.copy()
        for campo, valor in cambios.items():
            if campo != "dia":
                nuevo_horario[campo] = str(valor).strip()

        inicio = self.convertirHora(nuevo_horario["horaInicio"])
        fin = self.convertirHora(nuevo_horario["horaFin"])
        if inicio >= fin:
            print("La hora de inicio debe ser menor que la hora de fin.")
            return False

        if self._verificarCruce(nuevo_horario, nuevo_dia, idExcluir=idHorario):
            return False

        if nuevo_dia != dia_actual:
            self.horarios[dia_actual].remove(horario_encontrado)
            horario_encontrado.update(nuevo_horario)
            self.horarios[nuevo_dia].append(horario_encontrado)
        else:
            horario_encontrado.update(nuevo_horario)

        self.guardarHorarios()
        print("Horario modificado correctamente.")
        return horario_encontrado

    def eliminarHorario(self, idHorario):
        if not self.sesionActiva:
            print("Debe iniciar sesión para eliminar horarios.")
            return False

        for dia, lista in self.horarios.items():
            for h in lista:
                if str(h["id"]) == str(idHorario):
                    lista.remove(h)
                    h_eliminado = h.copy()
                    h_eliminado["_dia_original"] = dia
                    self.horariosEliminados.append(h_eliminado)
                    self.guardarHorarios()
                    print("Horario eliminado correctamente.")
                    return True

        print("No se encontró el horario.")
        return False

    def recuperarHorario(self, idHorario):
        if not self.sesionActiva:
            print("Debe iniciar sesión para recuperar horarios.")
            return False

        horario = next((h for h in self.horariosEliminados if str(h["id"]) == str(idHorario)), None)
        if not horario:
            print("No se encontró el horario eliminado.")
            return False

        dia = horario.get("_dia_original", "Lunes")
        h_limpio = {k: v for k, v in horario.items() if k != "_dia_original"}

        if self._verificarCruce(h_limpio, dia):
            print("No se puede recuperar el horario porque genera un cruce actual.")
            return False

        self.horariosEliminados.remove(horario)
        self.horarios[dia].append(h_limpio)
        self.guardarHorarios()
        print("Horario recuperado correctamente.")
        return True

    def visualizarHorario(self):
        if not self.sesionActiva:
            print("Debe iniciar sesión para visualizar horarios.")
            return False

        if not any(self.horarios.values()):
            print("No hay horarios registrados.")
            return {}

        return self.horarios.copy()