from Persistencia import GestorHorario, GestorAula
import Usuario

class CoordinadorAcademico(Usuario.Usuario):
    def __init__(self, usuario, contrasena):
        super().__init__(usuario, contrasena)
        self.sesionActiva = False
        self.gestor = GestorHorario(self.usuario)


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
        if dia not in GestorHorario.DIAS:
            print(f"El día '{dia}' no es válido. Debe ser uno de: {GestorHorario.DIAS}")
            return False

        inicio = GestorHorario.convertirHora(datos["horaInicio"])
        fin = GestorHorario.convertirHora(datos["horaFin"])

        if inicio == -1 or fin == -1 or inicio >= fin:
            if inicio >= fin:
                print("La hora de inicio debe ser menor que la hora de fin.")
            return False

        horario = {
            "id": str(self.gestor.contadorID),
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

        if self.gestor._verificarCruce(horario, dia):
            return False

        self.gestor.horarios[dia].append(horario)
        self.gestor.contadorID += 1
        self.gestor.guardarHorarios()

        print(f"Horario registrado correctamente para el día {dia}.")
        return horario

    def generarHorarios(self):
        if not self.sesionActiva:
            print("Debe iniciar sesión para generar horarios.")
            return False

        if not any(self.gestor.horarios.values()):
            print("No hay horarios registrados.")
            return False

        for dia, lista in self.gestor.horarios.items():
            for h in lista:
                if self.gestor._verificarCruce(h, dia, idExcluir=h["id"]):
                    print(f"Error de cruce en el día {dia} (ID {h['id']}).")
                    return False

        for dia, lista in self.gestor.horarios.items():
            for h in lista:
                h["estado"] = "generado"

        self.gestor.guardarHorarios()
        print("Los horarios semanales se generaron correctamente.")
        return True

    def modificarHorario(self, idHorario, cambios):
        if not self.sesionActiva:
            print("Debe iniciar sesión para modificar horarios.")
            return False

        horario_encontrado = None
        dia_actual = None
        for d, lista in self.gestor.horarios.items():
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
        if nuevo_dia not in GestorHorario.DIAS:
            print("Día inválido.")
            return False

        nuevo_horario = horario_encontrado.copy()
        for campo, valor in cambios.items():
            if campo != "dia":
                nuevo_horario[campo] = str(valor).strip()

        inicio = GestorHorario.convertirHora(nuevo_horario["horaInicio"])
        fin = GestorHorario.convertirHora(nuevo_horario["horaFin"])
        if inicio >= fin:
            print("La hora de inicio debe ser menor que la hora de fin.")
            return False

        if self.gestor._verificarCruce(nuevo_horario, nuevo_dia, idExcluir=idHorario):
            return False

        if nuevo_dia != dia_actual:
            self.gestor.horarios[dia_actual].remove(horario_encontrado)
            horario_encontrado.update(nuevo_horario)
            self.gestor.horarios[nuevo_dia].append(horario_encontrado)
        else:
            horario_encontrado.update(nuevo_horario)

        self.gestor.guardarHorarios()
        print("Horario modificado correctamente.")
        return horario_encontrado

    def eliminarHorario(self, idHorario):
        if not self.sesionActiva:
            print("Debe iniciar sesión para eliminar horarios.")
            return False

        for dia, lista in self.gestor.horarios.items():
            for h in lista:
                if str(h["id"]) == str(idHorario):
                    lista.remove(h)
                    h_eliminado = h.copy()
                    h_eliminado["_dia_original"] = dia
                    self.gestor.horariosEliminados.append(h_eliminado)
                    self.gestor.guardarHorarios()
                    print("Horario eliminado correctamente.")
                    return True

        print("No se encontró el horario.")
        return False

    def recuperarHorario(self, idHorario):
        if not self.sesionActiva:
            print("Debe iniciar sesión para recuperar horarios.")
            return False

        horario = next((h for h in self.gestor.horariosEliminados if str(h["id"]) == str(idHorario)), None)
        if not horario:
            print("No se encontró el horario eliminado.")
            return False

        dia = horario.get("_dia_original", "Lunes")
        h_limpio = {k: v for k, v in horario.items() if k != "_dia_original"}

        if self.gestor._verificarCruce(h_limpio, dia):
            print("No se puede recuperar el horario porque genera un cruce actual.")
            return False

        self.gestor.horariosEliminados.remove(horario)
        self.gestor.horarios[dia].append(h_limpio)
        self.gestor.guardarHorarios()
        print("Horario recuperado correctamente.")
        return True

    def visualizarHorario(self):
        if not self.sesionActiva:
            print("Debe iniciar sesión para visualizar horarios.")
            return False

        if not any(self.gestor.horarios.values()):
            print("No hay horarios registrados.")
            return {}

        return self.gestor.horarios.copy()

def registrarAula():
        from Aula import Aula
        from AulaPractica import AulaPractica
        equipos = 0
        opcion = int (input("Ingrese 1 si quiere crear un aula o 2 si quiere crear un laboratorio"))
        nombre = input("Ingrese el nombre del aula: ")
        aulas = GestorAula.cargarAulaJson()
        validacion, id = GestorAula.asignarID(nombre, "nombre")
        if not validacion:
            print("El aula ya existe en el sistema")
            return
        mesas, sillas = Aula.ingresarCapacidad()
        str_id = str(id)
        if opcion == 1:
            opcion = "teorica"
            GestorAula.aulas_teoricas[id] = Aula(nombre, mesas, sillas)
        else:
            opcion = "practica"
            equipos = int(input("Ingrese la cantidad de equipos: "))
            GestorAula.aulas_teoricas[id] = AulaPractica(nombre, mesas, sillas, equipos)
        if str_id not in aulas:
            aulas[opcion][str_id] = {}
        aulas[opcion][str_id]["nombre"] = nombre
        aulas[opcion][str_id]["mesas"] = mesas
        aulas[opcion][str_id]["sillas"] = sillas
        aulas[opcion][str_id]["estado"] = "Valida"
        if opcion == "practica":
            aulas[opcion][str_id]["equipos"] = equipos
        GestorAula.guardarAulaJson(aulas)
        print("Se ha guardado el aula correctamente")