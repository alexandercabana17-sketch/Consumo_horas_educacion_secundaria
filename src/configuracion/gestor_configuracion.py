"""
Módulo Gestor de Configuración
Gestiona la carga y validación de la configuración
"""

import json
from pathlib import Path
from typing import Dict, List, Any


class GestorConfiguracion:
    """Clase para gestionar la configuración del sistema."""
    
    def __init__(self, ruta_configuracion: str = 'configuracion.json'):
        """
        Inicializa el gestor de configuración.
        
        Args:
            ruta_configuracion: Ruta al archivo de configuración
        """
        self.ruta_configuracion = Path(ruta_configuracion)
        self.configuracion = None
        self._cargar_configuracion()
        self._validar_configuracion()
    
    def _cargar_configuracion(self):
        """Carga el archivo de configuración."""
        if not self.ruta_configuracion.exists():
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {self.ruta_configuracion}"
            )
        
        with open(self.ruta_configuracion, 'r', encoding='utf-8') as archivo:
            self.configuracion = json.load(archivo)
    
    def _validar_configuracion(self):
        """Valida que la configuración tenga todos los campos necesarios."""
        # Validar metadatos
        if 'metadatos' not in self.configuracion:
            raise ValueError("Configuración no tiene sección 'metadatos'")
        
        campos_metadatos = ['carrera', 'programas', 'fecha_analisis']
        for campo in campos_metadatos:
            if campo not in self.configuracion['metadatos']:
                raise ValueError(f"Metadatos no tiene campo '{campo}'")
        
        # Validar parámetros
        if 'parametros' not in self.configuracion:
            raise ValueError("Configuración no tiene sección 'parametros'")
        
        campos_parametros = [
            'tamano_seccion_aula',
            'tamano_seccion_laboratorio',
            'tamano_seccion_taller',
            'semanas_por_semestre'
        ]
        for campo in campos_parametros:
            if campo not in self.configuracion['parametros']:
                raise ValueError(f"Parámetros no tiene campo '{campo}'")
        
        # Validar archivos
        if 'archivos' not in self.configuracion:
            raise ValueError("Configuración no tiene sección 'archivos'")
        
        for programa in self.configuracion['metadatos']['programas']:
            if programa not in self.configuracion['archivos']:
                raise ValueError(f"No hay configuración de archivos para programa '{programa}'")
            
            if 'malla' not in self.configuracion['archivos'][programa]:
                raise ValueError(f"Programa '{programa}' no tiene archivo de malla")
            
            if 'proyeccion' not in self.configuracion['archivos'][programa]:
                raise ValueError(f"Programa '{programa}' no tiene archivo de proyección")
        
        # Validar salida
        if 'salida' not in self.configuracion:
            raise ValueError("Configuración no tiene sección 'salida'")
    
    def obtener_metadatos(self) -> Dict[str, Any]:
        """Obtiene los metadatos de la configuración."""
        return self.configuracion['metadatos']
    
    def obtener_carrera(self) -> str:
        """Obtiene el nombre de la carrera."""
        return self.configuracion['metadatos']['carrera']
    
    def obtener_programas(self) -> List[str]:
        """Obtiene la lista de programas."""
        return self.configuracion['metadatos']['programas']
    
    def obtener_parametros(self) -> Dict[str, Any]:
        """Obtiene los parámetros de configuración."""
        return self.configuracion['parametros']
    
    def obtener_tamano_seccion(self, tipo_ambiente: str) -> int:
        """
        Obtiene el tamaño máximo de sección para un tipo de ambiente.
        
        Args:
            tipo_ambiente: 'aula', 'laboratorio' o 'taller'
            
        Returns:
            Tamaño máximo de sección
        """
        mapa_claves = {
            'aula': 'tamano_seccion_aula',
            'laboratorio': 'tamano_seccion_laboratorio',
            'taller': 'tamano_seccion_taller',
            'virtual': 'tamano_seccion_aula'  # Virtual no se divide
        }
        
        clave = mapa_claves.get(tipo_ambiente, 'tamano_seccion_aula')
        return self.configuracion['parametros'][clave]
    
    def obtener_semanas_semestre(self) -> int:
        """Obtiene el número de semanas por semestre."""
        return self.configuracion['parametros']['semanas_por_semestre']
    
    def obtener_archivo_malla(self, programa: str) -> str:
        """
        Obtiene la ruta del archivo de malla curricular.
        
        Args:
            programa: Nombre del programa
            
        Returns:
            Ruta al archivo de malla
        """
        return self.configuracion['archivos'][programa]['malla']
    
    def obtener_archivo_proyeccion(self, programa: str) -> str:
        """
        Obtiene la ruta del archivo de proyección.
        
        Args:
            programa: Nombre del programa
            
        Returns:
            Ruta al archivo de proyección
        """
        return self.configuracion['archivos'][programa]['proyeccion']
    
    def obtener_salida_json(self) -> str:
        """Obtiene la ruta de salida del archivo JSON."""
        return self.configuracion['salida']['json']
    
    def obtener_salida_excel(self) -> str:
        """Obtiene la ruta de salida del archivo Excel."""
        return self.configuracion['salida']['excel']
    
    def obtener_salida_log(self) -> str:
        """Obtiene la ruta del archivo de log."""
        return self.configuracion['salida']['log']
    
    def __str__(self) -> str:
        """Representación en string de la configuración."""
        return json.dumps(self.configuracion, indent=2, ensure_ascii=False)
