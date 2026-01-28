"""
Módulo de Registro (Logging)
Gestiona los registros del sistema
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class Registrador:
    """Clase para gestionar el registro del sistema."""
    
    def __init__(self, archivo_log=None, nivel=logging.INFO):
        """
        Inicializa el registrador.
        
        Args:
            archivo_log (str): Ruta del archivo de log
            nivel: Nivel de registro (INFO, DEBUG, WARNING, ERROR)
        """
        self.registrador = logging.getLogger('AnalizadorHorasAula')
        self.registrador.setLevel(nivel)
        
        # Limpiar handlers anteriores
        self.registrador.handlers.clear()
        
        # Formato del log
        formateador = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para consola
        manejador_consola = logging.StreamHandler(sys.stdout)
        manejador_consola.setLevel(nivel)
        manejador_consola.setFormatter(formateador)
        self.registrador.addHandler(manejador_consola)
        
        # Handler para archivo (si se especifica)
        if archivo_log:
            # Crear directorio si no existe
            ruta_log = Path(archivo_log)
            ruta_log.parent.mkdir(parents=True, exist_ok=True)
            
            manejador_archivo = logging.FileHandler(archivo_log, encoding='utf-8')
            manejador_archivo.setLevel(nivel)
            manejador_archivo.setFormatter(formateador)
            self.registrador.addHandler(manejador_archivo)
    
    def info(self, mensaje):
        """Registro de información."""
        self.registrador.info(mensaje)
    
    def debug(self, mensaje):
        """Registro de depuración."""
        self.registrador.debug(mensaje)
    
    def advertencia(self, mensaje):
        """Registro de advertencia."""
        self.registrador.warning(mensaje)
    
    def error(self, mensaje):
        """Registro de error."""
        self.registrador.error(mensaje)
    
    def separador(self, caracter='=', longitud=80):
        """Imprime un separador en el registro."""
        self.registrador.info(caracter * longitud)
    
    def seccion(self, titulo, caracter='=', longitud=80):
        """Imprime una sección con título."""
        self.separador(caracter, longitud)
        titulo_centrado = titulo.center(longitud)
        self.registrador.info(titulo_centrado)
        self.separador(caracter, longitud)


# Instancia global del registrador
_instancia_registrador = None


def obtener_registrador(archivo_log=None, nivel=logging.INFO):
    """
    Obtiene la instancia del registrador (singleton).
    
    Args:
        archivo_log (str): Ruta del archivo de log
        nivel: Nivel de registro
        
    Returns:
        Registrador: Instancia del registrador
    """
    global _instancia_registrador
    
    if _instancia_registrador is None:
        _instancia_registrador = Registrador(archivo_log, nivel)
    
    return _instancia_registrador
