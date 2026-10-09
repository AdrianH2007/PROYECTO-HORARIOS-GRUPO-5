import json
import Usuario
#from Coordinador import Coordinador

class GestorUsuario():

    usuario_admin = {}
    usuario_coord = {}

    @staticmethod
    def cargarInstancias():
        cuentas = GestorUsuario.cargarCuentasJson()
        GestorUsuario.usuario_admin.clear()
        GestorUsuario.usuario_coord.clear()
        if cuentas["administrador"]:
            for id_str, datos in cuentas.get("administrador", {}).items():
                GestorUsuario.usuario_admin[int(id_str)] = Administrador(datos["usuario"], datos["contrasena"])
                GestorUsuario.usuario_admin[int(id_str)].estado = datos["estado"]
#        if cuentas["coordinador"]:
#            for id_str, datos in cuentas.get("coordinador", {}).items():
#                GestorUsuario.usuario_admin[int(id_str)] = Coordinador(datos["usuario"], datos["contrasena"])
#                GestorUsuario.usuario_admin[int(id_str)].estado = datos["estado"]

    @staticmethod
    def cargarCuentasJson():
        with open("cuentasUsuario.json", "r") as f:
            return json.load(f)

    @staticmethod
    def guardarCuentasJson(cuentas):
        with open ("cuentasUsuario.json", "w") as f:
            json.dump(cuentas, f)

    @staticmethod
    def verificarExistencia(dato, comparador, opcionEliminar=0):
        cuentas = GestorUsuario.cargarCuentasJson()
        if opcionEliminar == 0:
            cuentas_admin = cuentas.get("administrador",{})
            id_max=0
            for usuarios_guardados in cuentas_admin:
                if int(usuarios_guardados) > id_max:
                    id_max = int(usuarios_guardados)
                if cuentas_admin[usuarios_guardados][comparador] == dato:
                    return False, None
            cuentas_coord = cuentas.get("coordinador",{})
            for usuarios_guardados in cuentas_coord:
                if int(usuarios_guardados) > id_max:
                    id_max = int(usuarios_guardados)
                if cuentas_coord[usuarios_guardados][comparador] == dato:
                    return False, None
            return True, id_max+1
        else:
            cuentas_admin = cuentas.get("administrador",{})
            for usuarios_guardados in cuentas_admin:
                if cuentas_admin[usuarios_guardados][comparador] == dato:
                    return True, int(usuarios_guardados)
            cuentas_coord = cuentas.get("coordinador",{})
            for usuarios_guardados in cuentas_coord:
                if cuentas_coord[usuarios_guardados][comparador] == dato:
                    return True, int(usuarios_guardados)
            return False, int(usuarios_guardados)

class Administrador(Usuario.Usuario):

    rol = "Administrador"

    def iniciarSesion(self):
        print("Inicio de sesion para cuando este la interfaz")

    def cerrarSesion(self):
        print("Cerrar Sesion para cuando este la interfaz")

    def registrarCuentas(self):
        opcion = int(input("Ingrese 1 si quiere crear una cuenta de admin o 2 si quiere crear una cuenta coordinador: "))
        nombreU = input("Ingrese el nombre de usuario nuevo: ")
        passwordU = input("Ingrese la contraseña para el usuario nuevo: ")
        validacion, id = GestorUsuario.verificarExistencia(nombreU, "usuario")
        if validacion:
            id_str = str(id)
            if opcion == 1:
                opcion = "administrador"
                GestorUsuario.usuario_admin[id] = Administrador(nombreU, passwordU)
            else:
                opcion = "coordinador"
                #GestorUsuario.usuario_coord[id] = Coordinador(nombreU, passwordU)
            cuentas = GestorUsuario.cargarCuentasJson()
            if id_str not in cuentas[opcion]:
                cuentas[opcion][id_str] = {}
            cuentas[opcion][id_str]["usuario"] = nombreU
            cuentas[opcion][id_str]["contrasena"] = passwordU
            cuentas[opcion][id_str]["estado"] = "Activo"
            GestorUsuario.guardarCuentasJson(cuentas)
            print("Se ha guardado la cuenta correctamente")
        else:
            print("El nombre de usuario ya existe en otra cuenta")

    def modificarCuentas(self):
        opcion = int(input("Ingrese 1 si quiere modificar una cuenta de admin o 2 si quiere modificar una cuenta coordinador: "))
        nombreU = input("Ingrese el nombre de usuario a modificar: ")
        validacion, id = GestorUsuario.verificarExistencia(nombreU, "usuario", opcionEliminar=1)
        if validacion:
            print("¿Que desea modificar?")
            print("1. Nombre de usuario\n"+"2. Contraseña\n"+"3. Desactivar Usuario\n")
            op = input()
            match int(op):
                case 1:
                    print("Ingrese el nuevo nombre de Usuario")
                    op = "usuario"
                case 2:
                    print("Ingrese la nueva contraseña para el usuario")
                    op = "contrasena"
                case 3:
                    id_str = str(id)
                    if opcion == 1:
                        GestorUsuario.usuario_admin[id].estado = "Inactivo"
                    else:
                        GestorUsuario.usuario_coord[id].estado = "Inactivo"
                    print("Se desactivado el usuario")
                    cuentas[opcion][id_str]["estado"] = "Inactivo"
                    GestorUsuario.guardarCuentasJson(cuentas)
                    return
                case _:
                    print("No se ingreso una respuesta esperada")
            if op == "usuario" or op == "contrasena":
                nuevo = input("=> ")
                cuentas = GestorUsuario.cargarCuentasJson()
                validacion, id = GestorUsuario.verificarExistencia(nuevo,op,opcionEliminar=1)
                if not validacion:
                    id_str = str(id)
                    if opcion == 1:
                        opcion = "administrador"
                        setattr(GestorUsuario.usuario_admin[id], op, nuevo)
                    else:
                        opcion = "coordinador"
                        setattr(GestorUsuario.usuario_coord[id], op, nuevo)
                    cuentas[opcion][id_str][op] = nuevo
                    GestorUsuario.guardarCuentasJson(cuentas)
                    print("Se realizaron los cambios correctamente")  
                else:
                    print("No se puede ingresar el mismo usuario o contraseña para su modificacion")
        else:
            print("La cuenta que se busca no existe en el sistema")

    def eliminarCuentas(self):
        opcion = int(input("Ingrese 1 si quiere eliminar una cuenta de admin o 2 si quiere eliminar una cuenta coordinador: "))
        nombreU = input("Ingrese el nombre del usuario que quiera eliminar")
        validacion, id = GestorUsuario.verificarExistencia(nombreU, "usuario", opcionEliminar=1)
        if validacion:
            id_str = str(id)
            if opcion == 1:
                opcion = "administrador"
                GestorUsuario.usuario_admin.pop(id)
            else:
                opcion = "coordinador"
                GestorUsuario.usuario_coord.pop(id)
            cuentas = GestorUsuario.cargarCuentasJson()
            cuentas[opcion].pop(id_str)
            GestorUsuario.guardarCuentasJson(cuentas)
            print("Se ha elimnado la cuenta correctamente")
        else:
            print("La cuenta que se busca no existe en el sistema")


