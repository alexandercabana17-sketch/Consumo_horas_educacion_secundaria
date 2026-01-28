import pandas as pd
import numpy as np
import math
from typing import Any, Dict, List, Union


def convertir_a_tipos_python(objeto: Any) -> Any:
    """
    Convierte tipos numpy y pandas a tipos nativos de Python.
    Necesario para serialización JSON.
    
    Args:
        objeto: Objeto a convertir
        
    Returns:
        Objeto convertido a tipos nativos de Python
    """
    if isinstance(objeto, dict):
        return {clave: convertir_a_tipos_python(valor) for clave, valor in objeto.items()}
    elif isinstance(objeto, list):
        return [convertir_a_tipos_python(item) for item in objeto]
    elif isinstance(objeto, (np.integer, np.int64, np.int32)):
        return int(objeto)
    elif isinstance(objeto, (np.floating, np.float64, np.float32)):
        return float(objeto)
    elif isinstance(objeto, np.ndarray):
        return objeto.tolist()
    elif isinstance(objeto, pd.Timestamp):
        return objeto.strftime('%Y-%m-%d')
    elif pd.isna(objeto):
        return None
    else:
        return objeto


def calcular_numero_secciones(num_estudiantes: int, capacidad_maxima: int) -> int:
    """
    Calcula el número de grupos necesarias.
    
    Args:
        num_estudiantes: Número de estudiantes matriculados
        capacidad_maxima: Capacidad máxima por sección
        
    Returns:
        Número de grupos necesarias
    """
    if num_estudiantes == 0 or capacidad_maxima == 0:
        return 0
    
    return math.ceil(num_estudiantes / capacidad_maxima)


def limpiar_texto(texto: str) -> str:
    """
    Limpia y normaliza un texto.
    
    Args:
        texto: Texto a limpiar
        
    Returns:
        Texto limpio
    """
    if pd.isna(texto):
        return ""
    
    return str(texto).strip().lower()


def formatear_periodo(fecha: pd.Timestamp) -> str:
    """
    Formatea una fecha como periodo (YYYY-MM).
    
    Args:
        fecha: Fecha a formatear
        
    Returns:
        String en formato YYYY-MM
    """
    if pd.isna(fecha):
        return ""
    
    return pd.to_datetime(fecha).strftime('%Y-%m')


def es_virtual(modalidad: str = None, tipo_ambiente: str = None) -> bool:
    """
    Determina si un curso/ambiente es virtual.
    
    Args:
        modalidad: Modalidad del curso
        tipo_ambiente: Tipo de ambiente
        
    Returns:
        True si es virtual, False en caso contrario
    """
    if pd.notna(modalidad) and limpiar_texto(modalidad) == 'virtual':
        return True
    
    if pd.notna(tipo_ambiente) and 'virtual' in limpiar_texto(tipo_ambiente):
        return True
    
    return False


def mapear_tipo_ambiente(tipo_ambiente: str) -> str:
    """
    Mapea el tipo de ambiente a categorías estándar.
    
    Args:
        tipo_ambiente: Tipo de ambiente original
        
    Returns:
        Tipo de ambiente normalizado: 'aula', 'laboratorio', 'taller', 'virtual'
    """
    if pd.isna(tipo_ambiente):
        return 'aula'
    
    tipo_limpio = limpiar_texto(tipo_ambiente)
    
    if 'virtual' in tipo_limpio:
        return 'virtual'
    elif 'laboratorio' in tipo_limpio or 'lab' in tipo_limpio:
        return 'laboratorio'
    elif 'taller' in tipo_limpio:
        return 'taller'
    else:
        return 'aula'


def validar_columnas_requeridas(df: pd.DataFrame, columnas: List[str], nombre_df: str = "DataFrame") -> bool:
    """
    Valida que un DataFrame tenga todas las columnas requeridas.
    
    Args:
        df: DataFrame a validar
        columnas: Lista de columnas requeridas
        nombre_df: Nombre descriptivo del DataFrame
        
    Returns:
        True si tiene todas las columnas, False en caso contrario
        
    Raises:
        ValueError: Si faltan columnas
    """
    columnas_faltantes = set(columnas) - set(df.columns)
    
    if columnas_faltantes:
        raise ValueError(
            f"{nombre_df} no tiene las columnas requeridas: {columnas_faltantes}"
        )
    
    return True


def extraer_anio_ciclo(periodo_str: str) -> tuple:
    """
    Extrae año y ciclo de un string de periodo.
    
    Args:
        periodo_str: String en formato 'YYYY-MM'
        
    Returns:
        Tupla (año, ciclo) donde ciclo es 'I' o 'II'
    """
    if not periodo_str:
        return None, None
    
    anio = int(periodo_str[:4])
    mes = periodo_str[-2:]
    ciclo = 'I' if mes == '01' else 'II'
    
    return anio, ciclo


def crear_diccionario_resumen(
    periodo: str,
    anio: int,
    ciclo: str,
    estudiantes: Dict[str, int],
    horas_semanales: Dict[str, float],
    secciones: Dict[str, int],
    semanas: int = 16
) -> Dict:
    """
    Crea un diccionario de resumen estandarizado.
    
    Args:
        periodo: String del periodo (YYYY-MM)
        anio: Año
        ciclo: Ciclo (I o II)
        estudiantes: Dict con totales de estudiantes
        horas_semanales: Dict con horas semanales por tipo
        secciones: Dict con secciones por tipo
        semanas: Número de semanas del semestre
        
    Returns:
        Diccionario con el resumen completo
    """
    # Calcular horas por semestre
    horas_semestre = {
        tipo: horas * semanas
        for tipo, horas in horas_semanales.items()
    }
    
    return {
        'periodo': periodo,
        'anio': anio,
        'ciclo': ciclo,
        'estudiantes': estudiantes,
        'horas_semanales': horas_semanales,
        'horas_semestre': horas_semestre,
        'secciones': secciones
    }


def redondear_diccionario(diccionario: Dict, decimales: int = 2) -> Dict:
    """
    Redondea todos los valores numéricos de un diccionario.
    
    Args:
        diccionario: Diccionario a redondear
        decimales: Número de decimales
        
    Returns:
        Diccionario con valores redondeados
    """
    resultado = {}
    
    for clave, valor in diccionario.items():
        if isinstance(valor, dict):
            resultado[clave] = redondear_diccionario(valor, decimales)
        elif isinstance(valor, (int, float, np.integer, np.floating)):
            if isinstance(valor, (int, np.integer)):
                resultado[clave] = int(valor)
            else:
                resultado[clave] = round(float(valor), decimales)
        else:
            resultado[clave] = valor
    
    return resultado
