import pandas as pd
from pathlib import Path
from typing import Dict
from ..utilidades.registro import obtener_registrador


class CargadorDatos:
    """Clase para cargar datos desde archivos Excel."""
    
    def __init__(self, gestor_config):
        """
        Inicializa el cargador de datos.
        
        Args:
            gestor_config: Instancia de GestorConfiguracion
        """
        self.config = gestor_config
        self.registro = obtener_registrador()
        self.mallas = {}
        self.proyecciones = {}
    
    def cargar_malla(self, programa: str) -> pd.DataFrame:
        """Carga la malla curricular de un programa."""
        archivo = self.config.obtener_archivo_malla(programa)
        ruta = Path(archivo)
        
        if not ruta.exists():
            raise FileNotFoundError(f"Archivo de malla no encontrado: {ruta}")
        
        self.registro.info(f"  Cargando malla {programa}: {archivo}")
        df = pd.read_excel(archivo)
        self.registro.info(f"    ✓ {len(df)} cursos cargados")
        
        return df
    
    def cargar_proyeccion(self, programa: str) -> pd.DataFrame:
        """Carga la proyección de matrícula de un programa."""
        archivo = self.config.obtener_archivo_proyeccion(programa)
        ruta = Path(archivo)
        
        if not ruta.exists():
            raise FileNotFoundError(f"Archivo de proyección no encontrado: {ruta}")
        
        self.registro.info(f"  Cargando proyección {programa}: {archivo}")
        df = pd.read_excel(archivo)
        self.registro.info(f"    ✓ {len(df)} registros cargados")
        
        return df
    
    def cargar_todos_los_datos(self) -> tuple:
        """Carga todos los datos de todos los programas."""
        self.registro.info("\n📂 Cargando datos...")
        
        programas = self.config.obtener_programas()
        
        for programa in programas:
            self.mallas[programa] = self.cargar_malla(programa)
            self.proyecciones[programa] = self.cargar_proyeccion(programa)
        
        self.registro.info(" Datos cargados exitosamente\n")
        
        return self.mallas, self.proyecciones
