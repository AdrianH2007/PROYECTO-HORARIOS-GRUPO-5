from abc import ABC, abstractmethod
class Usuario(ABC):
    estado = "Activo"
    def __init__(self, nombreUsuario, contrasena):
        self.nombreUsuario = nombreUsuario
        self.contrasena = contrasena

    @abstractmethod
    def iniciarSesion(self):
        pass

    @abstractmethod
    def cerrarSesion(self):
        pass