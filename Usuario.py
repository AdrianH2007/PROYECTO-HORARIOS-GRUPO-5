from abc import ABC, abstractmethod
class Usuario(ABC):
    estado = "Activo"
    def __init__(self, usuario, contrasena):
        self.usuario = usuario
        self.contrasena = contrasena

    @abstractmethod
    def iniciarSesion(self):
        pass

    @abstractmethod
    def cerrarSesion(self):
        pass