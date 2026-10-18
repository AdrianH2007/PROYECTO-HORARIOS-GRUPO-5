import json
import os

class GestorUsuario():

    usuario_admin = {}
    usuario_coord = {}

    @staticmethod
    def cargarInstancias():
        from Clases.Administrador import Administrador 
        from Clases.coordinador import CoordinadorAcademico
        cuentas = GestorUsuario.cargarCuentasJson()
        #   limpia los diccionarios por si acaso
        GestorUsuario.usuario_admin.clear()
        GestorUsuario.usuario_coord.clear()
        #   va cargando las instancia de administrador creadas desde los json
        for id_str, datos in cuentas.get("administrador", {}).items():
            GestorUsuario.usuario_admin[int(id_str)] = Administrador(datos["usuario"], datos["contrasena"])
            GestorUsuario.usuario_admin[int(id_str)].estado = datos["estado"]
        #   va cargando las instancias de coordinador creadas desde los json
        for id_str, datos in cuentas.get("coordinador", {}).items():
            GestorUsuario.usuario_coord[int(id_str)] = CoordinadorAcademico(datos["usuario"], datos["contrasena"])
            GestorUsuario.usuario_coord[int(id_str)].estado = datos["estado"]

    @staticmethod
    def cargarCuentasJson():
        #   devuelve el json legible para python
        with open("Datos/cuentasUsuario.json", "r") as f:
            return json.load(f)

    @staticmethod
    def guardarCuentasJson(cuentas):
        #   transforma el diccionario de python al json
        with open ("Datos/cuentasUsuario.json", "w") as f:
            json.dump(cuentas, f)

    @staticmethod
    def verificarExistencia(dato, comparador, opcionEliminar=0):
        cuentas = GestorUsuario.cargarCuentasJson()
        #   se usara cuando se quiera crear una cuenta nueva
        if opcionEliminar == 0:
            #   crea una varibale apra comprobar solo administradores
            cuentas_admin = cuentas.get("administrador",{})
            id_max=0
            #   verificara cual es el id de usuario mas alto para asi no repetir ids
            for usuarios_guardados in cuentas_admin:
                if int(usuarios_guardados) > id_max:
                    id_max = int(usuarios_guardados)
                #   verifica que no haya otra cuenta con el mismo nombre de usaurio
                if cuentas_admin[usuarios_guardados][comparador] == dato:
                    return False, None
            # crea una varibale para comprobar solo coordinadores
            cuentas_coord = cuentas.get("coordinador",{})
            #   verifica el id maximo para no repetirlo
            for usuarios_guardados in cuentas_coord:
                if int(usuarios_guardados) > id_max:
                    id_max = int(usuarios_guardados)
                    #   verifica q no exista una cuenta con el mismo nombre de usuario
                if cuentas_coord[usuarios_guardados][comparador] == dato:
                    return False, None
            return True, id_max+1
        #   se usara cuando se quiera verificar si una cuenta existe para que devuelva true
        else:
            #   crea una varibale apra comprobar solo administradores
            cuentas_admin = cuentas.get("administrador",{})
            for usuarios_guardados in cuentas_admin:
                #   verifica si existe le usuario y devuelve su id
                if cuentas_admin[usuarios_guardados][comparador] == dato:
                    return True, int(usuarios_guardados)
            # crea una varibale para comprobar solo coordinadores
            cuentas_coord = cuentas.get("coordinador",{})
            for usuarios_guardados in cuentas_coord:
                #   verifica si existe le usuario y devuelve su id
                if cuentas_coord[usuarios_guardados][comparador] == dato:
                    return True, int(usuarios_guardados)
            return False, None

class GestorHorario():

    DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    RUTA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Datos")
    RUTA_ARCHIVO = os.path.join(RUTA_DATOS, "horarios.json")

    def __init__(self, usuario):
        self.usuario = usuario
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
            with open(self.RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            usuario_datos = datos.get(self.usuario, {})
            self.horarios = usuario_datos.get("horarios", {
                "Lunes": [], "Martes": [], "Miércoles": [], "Jueves": [], "Viernes": []
            })
            self.horariosEliminados = usuario_datos.get("eliminados", [])

            max_id = 0
            for dia in GestorHorario.DIAS:
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
            self.horarios = {d: [] for d in GestorHorario.DIAS}
            self.horariosEliminados = []

    def guardarHorarios(self):
        try:
            with open(self.RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            datos = {}

        datos[self.usuario] = {
            "horarios": self.horarios,
            "eliminados": self.horariosEliminados
        }

        with open(self.RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

        print("Horarios guardados correctamente.")

    @staticmethod
    def convertirHora(hora):
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

        inicio1 = GestorHorario.convertirHora(horarioEvaluar["horaInicio"])
        fin1 = GestorHorario.convertirHora(horarioEvaluar["horaFin"])
        lista_dia = self.horarios.get(dia, [])

        for otro in lista_dia:
            if idExcluir is not None and str(otro["id"]) == str(idExcluir):
                continue

            inicio2 = GestorHorario.convertirHora(otro["horaInicio"])
            fin2 = GestorHorario.convertirHora(otro["horaFin"])

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

class GestorAula:
    aulas_teoricas = {}
    aulas_practicas = {}

    RUTA_DATOS = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Datos"
    )
    RUTA_ARCHIVO = os.path.join(RUTA_DATOS, "aulas.json")

    @staticmethod
    def cargarInstancias():
        from Clases.Aula import Aula
        from Clases.AulaPractica import AulaPractica

        aulas = GestorAula.cargarAulaJson()

        GestorAula.aulas_teoricas.clear()
        GestorAula.aulas_practicas.clear()

        for id_str, datos in aulas.get("teorica", {}).items():
            GestorAula.aulas_teoricas[int(id_str)] = Aula(
                datos["nombre"],
                datos["mesas"],
                datos["sillas"]
            )

        for id_str, datos in aulas.get("practica", {}).items():
            GestorAula.aulas_practicas[int(id_str)] = AulaPractica(
                datos["nombre"],
                datos["mesas"],
                datos["sillas"],
                datos["equipos"]
            )

    @staticmethod
    def cargarAulaJson():
        try:
            with open(GestorAula.RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            if not isinstance(datos, dict):
                print("La estructura del archivo de aulas no es válida.")
                return {"teorica": {}, "practica": {}}

            datos.setdefault("teorica", {})
            datos.setdefault("practica", {})
            return datos

        except FileNotFoundError:
            return {"teorica": {}, "practica": {}}
        except json.JSONDecodeError:
            print("El archivo de aulas está vacío o contiene JSON inválido.")
            return {"teorica": {}, "practica": {}}

    @staticmethod
    def guardarAulaJson(aulas):
        try:
            os.makedirs(GestorAula.RUTA_DATOS, exist_ok=True)

            with open(GestorAula.RUTA_ARCHIVO, "w", encoding="utf-8") as archivo:
                json.dump(aulas, archivo, indent=4, ensure_ascii=False)

            print("Aulas guardadas correctamente.")
            return True

        except OSError as error:
            print(f"Error al guardar las aulas: {error}")
            return False

    @staticmethod
    def registrarAula(tipo, nombre, mesas, sillas, equipos=None):
        tipo = tipo.strip().lower()
        nombre = nombre.strip()

        if tipo not in ("teorica", "practica"):
            print("El tipo debe ser teórica o práctica.")
            return False

        if not nombre:
            print("El nombre del aula es obligatorio.")
            return False

        if not isinstance(mesas, int) or mesas <= 0:
            print("La cantidad de mesas debe ser un entero positivo.")
            return False

        if not isinstance(sillas, int) or sillas <= 0:
            print("La cantidad de sillas debe ser un entero positivo.")
            return False

        if tipo == "practica":
            if not isinstance(equipos, list) or not equipos:
                print("Debe registrar al menos un equipo para el aula práctica.")
                return False

        aulas = GestorAula.cargarAulaJson()

        for categoria in ("teorica", "practica"):
            for datos in aulas[categoria].values():
                if datos["nombre"].strip().lower() == nombre.lower():
                    print("Ya existe un aula registrada con ese nombre.")
                    return False

        id_maximo = 0

        for categoria in ("teorica", "practica"):
            for id_aula in aulas[categoria]:
                if id_aula.isdigit():
                    id_maximo = max(id_maximo, int(id_aula))

        nueva_aula = {
            "nombre": nombre,
            "mesas": mesas,
            "sillas": sillas
        }

        if tipo == "practica":
            nueva_aula["equipos"] = equipos

        aulas[tipo][str(id_maximo + 1)] = nueva_aula

        if not GestorAula.guardarAulaJson(aulas):
            return False

        GestorAula.cargarInstancias()
        print(f"Aula '{nombre}' registrada correctamente.")
        return True

class GestorEstructuraAcademica:

    RUTA_DATOS = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Datos"
    )

    RUTA_ARCHIVO = os.path.join(
        RUTA_DATOS,
        "estructuraAcademica.json"
    )

    @staticmethod
    def cargarDatos():
        try:
            with open(
                GestorEstructuraAcademica.RUTA_ARCHIVO,
                "r",
                encoding="utf-8"
            ) as archivo:
                datos = json.load(archivo)

            if isinstance(datos, list):
                return datos

            print("La estructura del archivo académico no es válida.")
            return []

        except FileNotFoundError:
            return []

        except json.JSONDecodeError:
            print("El archivo académico contiene JSON inválido.")
            return []

    @staticmethod
    def guardarDatos(datos):
        if not os.path.isdir(
            GestorEstructuraAcademica.RUTA_DATOS
        ):
            print("No existe la carpeta Datos.")
            return False

        try:
            with open(
                GestorEstructuraAcademica.RUTA_ARCHIVO,
                "w",
                encoding="utf-8"
            ) as archivo:
                json.dump(
                    datos,
                    archivo,
                    indent=4,
                    ensure_ascii=False
                )

            print("Datos académicos guardados correctamente.")
            return True

        except OSError as error:
            print(f"Error al guardar los datos: {error}")
            return False