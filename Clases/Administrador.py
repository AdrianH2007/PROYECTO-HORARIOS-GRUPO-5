from Persistencia import GestorUsuario
from Clases import Usuario
from Clases.coordinador import CoordinadorAcademico

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
                #   agrega una nueva instancia de Administrador
                opcion = "administrador"
                GestorUsuario.usuario_admin[id] = Administrador(nombreU, passwordU)
            else:
                #   agrega una nueva instancia de Coordinador
                opcion = "coordinador"
                GestorUsuario.usuario_coord[id] = CoordinadorAcademico(nombreU, passwordU)
            cuentas = GestorUsuario.cargarCuentasJson()
            #   crea en el json la nueva cuenta
            if id_str not in cuentas[opcion]:
                cuentas[opcion][id_str] = {}
            #   ingresa y guarda los valors al json
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
            cuentas = GestorUsuario.cargarCuentasJson()
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
                        #   modifica el atributo de clase estado de la instancia
                        clave = "administrador"
                        GestorUsuario.usuario_admin[id].estado = "Inactivo"
                    else:
                        #   modifica el atributo de clase estado de la instancia
                        clave = "coordinador"
                        GestorUsuario.usuario_coord[id].estado = "Inactivo"
                    print("Se desactivado el usuario")
                    #   modifica la clave "estado" en el json
                    cuentas[clave][id_str]["estado"] = "Inactivo"
                    GestorUsuario.guardarCuentasJson(cuentas)
                    return
                case _:
                    print("No se ingreso una respuesta esperada")
            if op == "usuario" or op == "contrasena":
                nuevo = input("=> ")
                validacion, _ = GestorUsuario.verificarExistencia(nuevo,op,opcionEliminar=1)
                if not validacion:
                    id_str = str(id)
                    if opcion == 1:
                        #   modifica el nombre de usuario o la contraseña de la instancia
                        opcion = "administrador"
                        setattr(GestorUsuario.usuario_admin[id], op, nuevo)
                    else:
                        #   modifica el nombre de usuario o la contraseña de la instancia
                        opcion = "coordinador"
                        setattr(GestorUsuario.usuario_coord[id], op, nuevo)
                    cuentas[opcion][id_str][op] = nuevo
                    #   modifica el nombre de usuario o la contraseña del json
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
                #   elimina la instancia guardada en usario_admin
                opcion = "administrador"
                GestorUsuario.usuario_admin.pop(id)
            else:
                #   elimina la instancia 
                opcion = "coordinador"
                GestorUsuario.usuario_coord.pop(id)
            cuentas = GestorUsuario.cargarCuentasJson()
            #   elimina la cuenta del json
            cuentas[opcion].pop(id_str)
            GestorUsuario.guardarCuentasJson(cuentas)
            print("Se ha elimnado la cuenta correctamente")
        else:
            print("La cuenta que se busca no existe en el sistema")
