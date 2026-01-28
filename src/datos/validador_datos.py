import pandas as pd
from typing import Dict, List
from ..utilidades.registro import obtener_registrador
from ..utilidades.ayudantes import validar_columnas_requeridas


class ValidadorDatos:
    """Clase para validar los datos cargados."""
    
    COLUMNAS_MALLA = ['CODIGO_CURSO', 'CURSO', 'SEMESTRE', 'HORAS_TEORICAS', 'HORAS_PRACTICAS', 'TOTAL_HORAS_SEMANALES']
    COLUMNAS_PROYECCION = ['PERIODO', 'CODIGO_CURSO', 'SEMESTRE', 'TOTAL_MATRICULADOS']
    
    def __init__(self):
        """Inicializa el validador."""
        self.registro = obtener_registrador()
        self.errores = []
        self.advertencias = []
    
    def validar_malla(self, df: pd.DataFrame, programa: str) -> bool:
        """Valida una malla curricular."""
        self.registro.info(f"  Validando malla {programa}...")
        
        try:
            validar_columnas_requeridas(df, self.COLUMNAS_MALLA, f"Malla {programa}")
            
            campos_criticos = ['CODIGO_CURSO', 'SEMESTRE']
            for campo in campos_criticos:
                if df[campo].isnull().any():
                    self.errores.append(f"Malla {programa} tiene valores nulos en {campo}")
            
            self.registro.info(f"    ✓ Validación exitosa")
            return len(self.errores) == 0
            
        except Exception as e:
            self.errores.append(f"Error validando malla {programa}: {str(e)}")
            return False
    
    def validar_proyeccion(self, df: pd.DataFrame, programa: str) -> bool:
        """Valida una proyección de matrícula."""
        self.registro.info(f"  Validando proyección {programa}...")
        
        try:
            validar_columnas_requeridas(df, self.COLUMNAS_PROYECCION, f"Proyección {programa}")
            
            if (df['TOTAL_MATRICULADOS'] < 0).any():
                self.errores.append(f"Proyección {programa} tiene valores negativos")
            
            self.registro.info(f"    ✓ Validación exitosa")
            return len(self.errores) == 0
            
        except Exception as e:
            self.errores.append(f"Error validando proyección {programa}: {str(e)}")
            return False
    
    def validar_todo(self, mallas: Dict[str, pd.DataFrame], proyecciones: Dict[str, pd.DataFrame]) -> bool:
        """Ejecuta todas las validaciones."""
        self.registro.info("\n🔍 Validando datos...")
        
        self.errores = []
        self.advertencias = []
        
        for programa, df in mallas.items():
            self.validar_malla(df, programa)
        
        for programa, df in proyecciones.items():
            self.validar_proyeccion(df, programa)
        
        if self.errores:
            self.registro.error(f"\n❌ Se encontraron {len(self.errores)} errores:")
            for error in self.errores:
                self.registro.error(f"  - {error}")
        else:
            self.registro.info(" Validación exitosa\n")
        
        return len(self.errores) == 0
