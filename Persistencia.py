import json

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
        with open("cuentasUsuario.json", "r") as f:
            return json.load(f)

    @staticmethod
    def guardarCuentasJson(cuentas):
        #   transforma el diccionario de python al json
        with open ("cuentasUsuario.json", "w") as f:
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
            with open("horarios.json", "r", encoding="utf-8") as archivo:
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

    def cargarInstancias():
        from Clases.Aula import Aula
        from Clases.AulaPractica import AulaPractica
        aulas = GestorAula.cargarAulaJson()
        #   limpia los diccionarios por si acaso
        GestorAula.aulas_teoricas.clear()
        GestorAula.aulas_practicas.clear()
        #   va cargando las instancia de administrador creadas desde los json
        for id_str, datos in aulas.get("teorica", {}).items():
            GestorAula.aulas_teoricas[int(id_str)] = Aula(datos["nombre"], datos["mesas"], datos["sillas"])
        #   va cargando las instancias de coordinador creadas desde los json
        for id_str, datos in aulas.get("practica", {}).items():
            GestorAula.aulas_practicas[int(id_str)] = AulaPractica(datos["nombre"], datos["mesas"], datos["sillas"], datos["equipos"])

    def guardarAulaJson(asignaturas):
        with open("aulas.jsom","w") as f:
            json.dump(asignaturas, f, indent = 4)

    def cargarAulaJson():
        with open("aulas.json", "r") as f:
            return json.load(f)

    def asignarID(dato, comparador):
        aulas = GestorAula.cargarAulaJson()
        id_max=0
        aulasT = aulas.get("teorica", {})
        for aula in aulasT:
            if int(aula) > id_max:
                id_max = int(aula)
            if aulasT[aula][comparador] == dato:
                return False, None
        aulasP = aulas.get("practica",{})
        for aula in aulasP:
            if int(aula) > id_max:
                id_max = int(aula)
            if aulasP[aula][comparador] == dato:
                return False, None
        return True, id_max+1