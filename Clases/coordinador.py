import json
import os
from Persistencia import GestorHorario, GestorAula, GestorEstructuraAcademica
from Clases import Usuario

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

    def registrarDatosAcademicos(self):
        if not self.sesionActiva:
            print("Debe iniciar sesión para registrar datos académicos.")
            return False

        def leer_entero(mensaje):
            while True:
                valor = input(mensaje).strip()

                if valor.isdigit() and int(valor) > 0:
                    return int(valor)
                print("Ingrese un úmero mayor a cero.")

        print("\n===== REGITRO ACADÉMICO =====")

        carrera = input("Nombre de la carrera: ").strip()
        if not carrera:
            print("La carrera es obligatoria.")
            return False

        nivel= input("Nivel de la carrera (ej. 1, 2, 3): ").strip()
        if not nivel:
            print("El nivel es obligatorio.")
            return False

        estudiantes = leer_entero("Cantidad de estudiantes del nivel: ")
        aulas= leer_entero("Cantidad de aulas disponibles para el nivel: ")
        paralelos = leer_entero("Cantidad de paralelos de nivel: ")
        cantidad_materias= leer_entero("Cantidad de materias del nivel: ")

        materias=[]

        for numero in range(1, cantidad_materias + 1):
            print(f"\n----- Materia {numero} -----")

            nombre = input("Nombre de la materia: ").strip()
            while not nombre:
                print("El nombre de la materia es obligatorio.")
                nombre = input("Nombre de la materia: ").strip()

            docente = input(f"Profesor asignado a {nombre}: ").strip()
            while not docente:
                print("Debe ingresar el nombre del profesor.")
                docente = input(f"Profesor asignado a {nombre}: ").strip()

            horas_semanales = leer_entero(f"¿Cúantas horas semanales se imparte {nombre}: ")

            materias.append({
                "nombre": nombre,
                "docente": docente,
                "horasSemanales": horas_semanales
            })
        
        datos_nivel = {
            "carrera": carrera,
            "nivel": nivel,
            "cantidadEstudiantes": estudiantes,
            "cantidadAulas": aulas,
            "cantidadParalelos": paralelos,
            "cantidadMaterias": cantidad_materias,
            "materias": materias
        }

        registros = GestorEstructuraAcademica.cargarDatos()
        registros.append(datos_nivel)

        if not GestorEstructuraAcademica.guardarDatos(registros):
            return False

        print("\nDatos académicos registrados correctamente.")
        print(f"Carrera: {carrera}")
        print(f"Nivel: {nivel}")
        print(f"Estudiantes: {estudiantes}")
        print(f"Aulas disponibles: {aulas}")
        print(f"Paralelos: {paralelos}")
        

        print("\nMaterias y profesores asignados:")
        for materia in materias:
            print(f"- {materia['nombre']}: " f"{materia['docente']}")
        return True
        
    def generarHorarios(self):
            if not self.sesionActiva:
                print("Debe iniciar sesión para generar horarios.")
                return False

            # 1. Cargar la estructura académica registrada
            registros_academicos = GestorEstructuraAcademica.cargarDatos()
            if not registros_academicos:
                print("No hay datos académicos registrados para generar el horario.")
                return False

            # 2. Cargar las aulas registradas
            aulas_disponibles = GestorAula.cargarAulaJson()
            aulas_lista = []
            for tipo in ["teorica", "practica"]:
                if tipo in aulas_disponibles and isinstance(aulas_disponibles[tipo], dict):
                    for aula_id, info in aulas_disponibles[tipo].items():
                        aulas_lista.append(info.get("nombre", f"Aula {aula_id}"))

            if not aulas_lista:
                print("No hay aulas registradas en el sistema.")
                return False

            dias_semana = GestorHorario.DIAS

            # Bloques matutinos y vespertinos estrictos hasta las 7:00 PM (19:00)
            bloques_matutinos = [
                {"inicio": "07:00", "fin": "09:00"},
                {"inicio": "09:00", "fin": "11:00"},
                {"inicio": "11:00", "fin": "13:00"}
            ]

            bloques_vespertinos = [
                {"inicio": "13:00", "fin": "15:00"},
                {"inicio": "15:00", "fin": "17:00"},
                {"inicio": "17:00", "fin": "19:00"}
            ]

            # Reiniciar los horarios actuales del gestor para hacer una generación limpia
            self.gestor.horarios = {dia: [] for dia in dias_semana}

            def obtener_nombre_paralelo(index):
                return chr(65 + index)  # 0 -> 'A', 1 -> 'B', etc.

            def hay_conflicto_silencioso(nuevo_h, dia_actual):
                inicio1 = GestorHorario.convertirHora(nuevo_h["horaInicio"])
                fin1 = GestorHorario.convertirHora(nuevo_h["horaFin"])
                
                for otro in self.gestor.horarios.get(dia_actual, []):
                    inicio2 = GestorHorario.convertirHora(otro["horaInicio"])
                    fin2 = GestorHorario.convertirHora(otro["horaFin"])

                    if inicio1 < fin2 and inicio2 < fin1:
                        if nuevo_h["docente"] == otro["docente"]:
                            return True
                        if nuevo_h["aula"] == otro["aula"]:
                            return True
                        if (str(nuevo_h.get("carrera")) == str(otro.get("carrera")) and 
                            str(nuevo_h.get("nivel")) == str(otro.get("nivel")) and 
                            str(nuevo_h.get("paralelo")) == str(otro.get("paralelo"))):
                            return True
                return False

            # Función para verificar si un paralelo ya tiene esa misma materia o está ocupado ese día
            def paralelo_ya_tiene_materia_en_dia(carrera, nivel, paralelo, materia_nombre, dia):
                for h in self.gestor.horarios.get(dia, []):
                    if (str(h.get("carrera")) == str(carrera) and 
                        str(h.get("nivel")) == str(nivel) and 
                        str(h.get("paralelo")) == str(paralelo) and 
                        h.get("materia") == materia_nombre):
                        return True
                return False

            # 3. Iterar sobre cada nivel y sus paralelos
            for registro in registros_academicos:
                carrera = registro.get("carrera", "N/A")
                nivel = registro.get("nivel", "N/A")
                num_paralelos = int(registro.get("cantidadParalelos", 1))
                materias = registro.get("materias", [])

                for p in range(num_paralelos):
                    paralelo_nombre = obtener_nombre_paralelo(p)

                    # Asignación estricta de Jornada por Paralelo
                    if p % 2 == 0:
                        bloques_horarios = bloques_matutinos
                        jornada_txt = "Matutina"
                    else:
                        bloques_horarios = bloques_vespertinos
                        jornada_txt = "Vespertina"

                    for materia in materias:
                        nombre_materia = materia["nombre"]
                        docente = materia["docente"]
                        horas_totales = materia.get("horasSemanales", 4)
                        num_sesiones = max(1, horas_totales // 2)

                        sesiones_colocadas = 0

                        # REGLA DE ORO: Intentar ubicar cada sesión en un DÍA DIFERENTE
                        # Iteramos primero por los días de la semana de forma rotativa
                        intentos_dia = 0
                        while sesiones_colocadas < num_sesiones and intentos_dia < len(dias_semana) * 2:
                            dia_idx = (hash(nombre_materia) + p + sesiones_colocadas + intentos_dia) % len(dias_semana)
                            dia_actual = dias_semana[dia_idx]
                            intentos_dia += 1

                            # RESTRICCIÓN: Evitar que el paralelo vea la misma materia dos veces el mismo día
                            if paralelo_ya_tiene_materia_en_dia(carrera, nivel, paralelo_nombre, nombre_materia, dia_actual):
                                continue

                            # Buscar un bloque libre en ese día
                            espacio_asignado_en_dia = False
                            for bloque in bloques_horarios:
                                if espacio_asignado_en_dia:
                                    break

                                for intento_aula in range(len(aulas_lista)):
                                    aula_actual = aulas_lista[(self.gestor.contadorID + intento_aula) % len(aulas_lista)]

                                    nuevo_horario = {
                                        "id": str(self.gestor.contadorID),
                                        "carrera": carrera,
                                        "semestre": nivel,
                                        "nivel": nivel,
                                        "paralelo": paralelo_nombre,
                                        "materia": nombre_materia,
                                        "docente": docente,
                                        "aula": aula_actual,
                                        "horaInicio": bloque["inicio"],
                                        "horaFin": bloque["fin"],
                                        "estado": "generado"
                                    }

                                    if not hay_conflicto_silencioso(nuevo_horario, dia_actual):
                                        self.gestor.horarios[dia_actual].append(nuevo_horario)
                                        self.gestor.contadorID += 1
                                        sesiones_colocadas += 1
                                        espacio_asignado_en_dia = True
                                        break
                                
                                if espacio_asignado_en_dia:
                                    break

                        # Si por falta de días libres quedan sesiones pendientes, las ubicamos permitiendo otro bloque
                        if sesiones_colocadas < num_sesiones:
                            for dia_actual in dias_semana:
                                if sesiones_colocadas >= num_sesiones:
                                    break
                                for bloque in bloques_horarios:
                                    if sesiones_colocadas >= num_sesiones:
                                        break
                                    for aula_info in aulas_lista:
                                        nuevo_horario = {
                                            "id": str(self.gestor.contadorID),
                                            "carrera": carrera,
                                            "semestre": nivel,
                                            "nivel": nivel,
                                            "paralelo": paralelo_nombre,
                                            "materia": nombre_materia,
                                            "docente": docente,
                                            "aula": aula_info,
                                            "horaInicio": bloque["inicio"],
                                            "horaFin": bloque["fin"],
                                            "estado": "generado"
                                        }
                                        if not hay_conflicto_silencioso(nuevo_horario, dia_actual):
                                            self.gestor.horarios[dia_actual].append(nuevo_horario)
                                            self.gestor.contadorID += 1
                                            sesiones_colocadas += 1
                                            break
                                    if sesiones_colocadas >= num_sesiones:
                                        break

            # 4. Guardar automáticamente en el JSON
            self.gestor.guardarHorarios()
            print("\n¡Horarios generados distribuyendo las materias en días diferentes sin repetir el mismo día!")
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