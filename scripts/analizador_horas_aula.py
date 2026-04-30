"""
Analizador de Consumo de Horas-Aula
Carrera: Educación Secundaria (LLYA + MYC)

Este script calcula el consumo de horas por tipo de ambiente
(Aula, Laboratorio, Taller, Virtual) considerando estudiantes
matriculados y secciones necesarias.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import math

class AnalizadorHorasAula:
    """
    Clase para analizar el consumo de horas-aula de una carrera.
    """
    
    def __init__(self, config_path='config.json'):
        """Inicializa el analizador cargando la configuración."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.parametros = self.config['parametros']
        self.archivos = self.config['archivos']
        
        # DataFrames
        self.mallas = {}
        self.proyecciones = {}
        self.equivalencias = {}
        self.resultados = {}
        
        # Información de equivalencias
        self.cursos_compartidos = []  # Cursos compartidos entre LLYA y MYC
        self.cursos_a_eliminar = {'LLYA': [], 'MYC': []}  # Cursos que van a otras carreras
        
        print("=" * 80)
        print(f"ANALIZADOR DE HORAS-AULA - {self.config['metadata']['carrera']}")
        print("=" * 80)
        print(f"Fecha: {self.config['metadata']['fecha_analisis']}")
        print(f"Programas: {', '.join(self.config['metadata']['programas'])}")
        print(f"\nParámetros:")
        print(f"  - Tamaño sección Aula: {self.parametros['tamano_seccion_aula']} estudiantes")
        print(f"  - Tamaño sección Laboratorio: {self.parametros['tamano_seccion_laboratorio']} estudiantes")
        print(f"  - Tamaño sección Taller: {self.parametros['tamano_seccion_taller']} estudiantes")
        print(f"  - Semanas por semestre: {self.parametros['semanas_por_semestre']}")
        print("=" * 80)
    
    def cargar_datos(self):
        """Carga las mallas curriculares, proyecciones de matrícula y equivalencias."""
        print("\nCargando datos...")
        
        for programa in self.config['metadata']['programas']:
            # Cargar malla curricular
            malla_path = self.archivos[programa]['malla']
            self.mallas[programa] = pd.read_excel(malla_path)
            print(f"    Malla {programa}: {len(self.mallas[programa])} cursos")
            
            # Cargar proyección
            proy_path = self.archivos[programa]['proyeccion']
            self.proyecciones[programa] = pd.read_excel(proy_path)
            print(f"    Proyeccion {programa}: {len(self.proyecciones[programa])} registros")
            
            # Cargar equivalencias
            equiv_path = self.archivos[programa]['equivalencias']
            self.equivalencias[programa] = pd.read_excel(equiv_path)
            print(f"    Equivalencias {programa}: {len(self.equivalencias[programa])} registros")
        
        print("  Datos cargados exitosamente\n")
    
    def identificar_cursos_compartidos(self):
        """
        Identifica cursos compartidos entre LLYA y MYC.
        Un curso es compartido si PROGRAMA_EQUIVALENTE indica el otro programa.
        """
        print("\nIdentificando cursos compartidos entre LLYA y MYC...")
        
        equiv_llya = self.equivalencias['LLYA']
        equiv_myc = self.equivalencias['MYC']
        
        # Cursos de LLYA que equivalen con MYC
        llya_to_myc = equiv_llya[equiv_llya['PROGRAMA_EQUIVALENTE'] == 'Educación MYC'].copy()
        
        # Cursos de MYC que equivalen con LLYA
        myc_to_llya = equiv_myc[equiv_myc['PROGRAMA_EQUIVALENTE'] == 'Educación LLYA'].copy()
        
        # Verificar que los nombres coincidan y crear lista de compartidos
        for _, row_llya in llya_to_myc.iterrows():
            codigo_llya = row_llya['CODIGO_CURSO']
            nombre_llya = row_llya['CURSO']
            codigo_equiv_myc = row_llya['CODIGO_CURSO_EQUIVALENTE']
            nombre_equiv = row_llya['CURSO_EQUIVALENTE']
            
            # Buscar el curso correspondiente en MYC
            myc_match = myc_to_llya[myc_to_llya['CODIGO_CURSO'] == codigo_equiv_myc]
            
            if len(myc_match) > 0:
                # Verificar que los nombres coincidan
                if nombre_llya == nombre_equiv:
                    self.cursos_compartidos.append({
                        'nombre': nombre_llya,
                        'codigo_llya': codigo_llya,
                        'codigo_myc': codigo_equiv_myc,
                        'semestre_llya': row_llya['SEMESTRE'],
                        'semestre_myc': myc_match.iloc[0]['SEMESTRE']
                    })
                else:
                    print(f"  ADVERTENCIA: Nombres no coinciden - LLYA: '{nombre_llya}' vs Equiv: '{nombre_equiv}'")
        
        print(f"  {len(self.cursos_compartidos)} cursos compartidos identificados:")
        for curso in self.cursos_compartidos:
            print(f"    - {curso['nombre']}")
        print()
        
        return self.cursos_compartidos
    
    def identificar_cursos_a_eliminar(self):
        """
        Identifica cursos que equivalen SOLO con Educación Inicial.
        Solo estos cursos se eliminan del análisis.
        Cursos equivalentes a otras carreras (Psicología, etc.) se mantienen.
        """
        print("\nIdentificando cursos que van a Educación Inicial...")
        
        for programa in ['LLYA', 'MYC']:
            equiv = self.equivalencias[programa]
            
            # NUEVA LÓGICA: Solo eliminar cursos que van a Educación Inicial
            # Cursos de Psicología u otras carreras SÍ se cuentan
            cursos_a_inicial = equiv[
                (equiv['PROGRAMA_EQUIVALENTE'].notna()) &
                (equiv['PROGRAMA_EQUIVALENTE'] == 'Educación Inicial')
            ]
            
            self.cursos_a_eliminar[programa] = cursos_a_inicial['CODIGO_CURSO'].tolist()
            
            print(f"  {programa}: {len(self.cursos_a_eliminar[programa])} cursos van a Educación Inicial")
            
            # Información adicional: cursos a otras carreras (que SÍ se cuentan)
            cursos_otras_carreras = equiv[
                (equiv['PROGRAMA_EQUIVALENTE'].notna()) &
                (equiv['PROGRAMA_EQUIVALENTE'] != 'Educación Inicial') &
                (equiv['PROGRAMA_EQUIVALENTE'] != 'Educación LLYA') &
                (equiv['PROGRAMA_EQUIVALENTE'] != 'Educación MYC')
            ]
            
            if len(cursos_otras_carreras) > 0:
                print(f"  INFO: {programa}: {len(cursos_otras_carreras)} cursos de otras carreras (se mantienen)")
                print(f"      Carreras: {cursos_otras_carreras['PROGRAMA_EQUIVALENTE'].unique().tolist()}")
        
        print(f"  Total eliminados (solo Educación Inicial): {sum(len(v) for v in self.cursos_a_eliminar.values())}\n")
        
        return self.cursos_a_eliminar
    
    def mapear_tipo_ambiente(self, row):
        """
        Determina el tipo de ambiente basado en las columnas de la malla.
        Lee directamente HORAS_TEORICAS/TIPO_AMBIENTE_TEORIA y
        HORAS_PRACTICAS/TIPO_AMBIENTE_PRACTICA sin sobreescrituras.
        Retorna: lista de tuplas (tipo_ambiente, horas)
        """
        ambientes = []

        # Horas teóricas
        if pd.notna(row['HORAS_TEORICAS']) and row['HORAS_TEORICAS'] > 0:
            if pd.notna(row['TIPO_AMBIENTE_TEORIA']):
                tipo_teoria = str(row['TIPO_AMBIENTE_TEORIA']).strip()
                if tipo_teoria.lower() == 'virtual':
                    ambientes.append(('Virtual', row['HORAS_TEORICAS']))
                else:
                    ambientes.append((tipo_teoria, row['HORAS_TEORICAS']))
            else:
                ambientes.append(('Aula', row['HORAS_TEORICAS']))
        
        # Horas prácticas
        if pd.notna(row['HORAS_PRACTICAS']) and row['HORAS_PRACTICAS'] > 0:
            if pd.notna(row['TIPO_AMBIENTE_PRACTICA']):
                tipo_practica = str(row['TIPO_AMBIENTE_PRACTICA']).strip()
                
                if 'Laboratorio' in tipo_practica:
                    ambientes.append((tipo_practica, row['HORAS_PRACTICAS']))
                elif tipo_practica.lower() == 'taller':
                    ambientes.append(('Taller', row['HORAS_PRACTICAS']))
                elif tipo_practica.lower() == 'virtual':
                    ambientes.append(('Virtual', row['HORAS_PRACTICAS']))
                elif tipo_practica.lower() == 'aula':
                    ambientes.append(('Aula', row['HORAS_PRACTICAS']))
                else:
                    ambientes.append((tipo_practica, row['HORAS_PRACTICAS']))
            else:
                # Por defecto si no se especifica
                ambientes.append(('Aula', row['HORAS_PRACTICAS']))

        
        # Si no hay ambientes, retornar lista vacía
        if not ambientes:
            ambientes.append(('Aula', 0))
        
        return ambientes
    
    def calcular_secciones(self, num_estudiantes, tipo_ambiente):
        """
        Calcula el número de secciones necesarias según el tipo de ambiente.
        Maneja laboratorios específicos (Química, Computadoras, etc.)
        """
        if num_estudiantes == 0:
            return 0
        
        tipo_ambiente_lower = str(tipo_ambiente).lower()
        
        # Aula
        if tipo_ambiente_lower == 'aula':
            max_estudiantes = self.parametros['tamano_seccion_aula']
        # Cualquier tipo de Laboratorio usa la capacidad de laboratorio
        elif 'laboratorio' in tipo_ambiente_lower:
            max_estudiantes = self.parametros['tamano_seccion_laboratorio']
        # Taller
        elif tipo_ambiente_lower == 'taller':
            max_estudiantes = self.parametros['tamano_seccion_taller']
        # Virtual
        elif tipo_ambiente_lower == 'virtual':
            return 1  # Virtual no se divide en secciones
        # Cualquier otro ambiente, usar capacidad de aula por defecto
        else:
            max_estudiantes = self.parametros['tamano_seccion_aula']
        
        return math.ceil(num_estudiantes / max_estudiantes)
    
    def procesar_programa(self, programa):
        """Procesa un programa específico (LLYA o MYC)."""
        print(f"\nProcesando programa: {programa}")
        
        malla = self.mallas[programa].copy()
        proyeccion = self.proyecciones[programa].copy()
        
        # NUEVO: Filtrar cursos a eliminar
        cursos_eliminar = self.cursos_a_eliminar[programa]
        if len(cursos_eliminar) > 0:
            malla = malla[~malla['CODIGO_CURSO'].isin(cursos_eliminar)]
            proyeccion = proyeccion[~proyeccion['CODIGO_CURSO'].isin(cursos_eliminar)]
            print(f"  Eliminados {len(cursos_eliminar)} cursos que van a otras carreras")
        
        # Preparar proyección
        proyeccion['PERIODO_STR'] = pd.to_datetime(proyeccion['PERIODO']).dt.strftime('%Y-%m')
        proyeccion['AÑO'] = pd.to_datetime(proyeccion['PERIODO']).dt.year
        proyeccion['CICLO'] = proyeccion['PERIODO_STR'].str[-2:].apply(lambda x: 'I' if x == '01' else 'II')
        
        # Preparar malla con tipos de ambiente
        malla_detalle = []
        for _, row in malla.iterrows():
            ambientes = self.mapear_tipo_ambiente(row)
            for tipo_amb, horas in ambientes:
                malla_detalle.append({
                    'CODIGO_CURSO': row['CODIGO_CURSO'],
                    'CURSO': row['CURSO'],
                    'SEMESTRE': row['SEMESTRE'],
                    'TIPO_AMBIENTE': tipo_amb,
                    'HORAS_SEMANALES': horas
                })
        
        malla_expandida = pd.DataFrame(malla_detalle)
        
        # Unir proyección con malla
        datos = proyeccion.merge(
            malla_expandida,
            on=['CODIGO_CURSO', 'SEMESTRE'],
            how='left'
        )
        
        # Calcular secciones
        datos['SECCIONES'] = datos.apply(
            lambda row: self.calcular_secciones(
                row['TOTAL_MATRICULADOS'], 
                row['TIPO_AMBIENTE']
            ) if pd.notna(row['TIPO_AMBIENTE']) else 0,
            axis=1
        )
        
        # Calcular horas totales (horas del curso × secciones)
        datos['HORAS_TOTALES'] = datos['HORAS_SEMANALES'] * datos['SECCIONES']
        
        self.resultados[programa] = datos
        
        print(f"  {programa} procesado: {len(datos)} registros")
        
        return datos
    
    def procesar_cursos_compartidos(self):
        """
        Procesa los cursos compartidos entre LLYA y MYC considerando desfases
        de semestre entre programas (cursos en semestres distintos de cada malla).

        Lógica de tres fases por periodo:
        - Fase 1 (prematuro): Solo LLYA tiene alumnos activos → se cuenta
          como curso exclusivo de LLYA sin fusión. El curso ya existe pero MYC
          aún no llega a ese semestre en su malla.
        - Fase 2 (compartido): Ambos programas tienen alumnos activos → se
          fusionan estudiantes y se recalcula una sola sección combinada.
          MYC se elimina para no doble-contar.
        - Fase 3 (solo MYC): Solo MYC tiene alumnos activos → se cuenta como
          curso exclusivo de MYC sin fusión (caso simétrico al prematuro).
        """
        print("\nProcesando cursos compartidos...")

        if len(self.cursos_compartidos) == 0:
            print("  INFO: No hay cursos compartidos para procesar")
            return

        for curso_comp in self.cursos_compartidos:
            codigo_llya = curso_comp['codigo_llya']
            codigo_myc  = curso_comp['codigo_myc']
            nombre      = curso_comp['nombre']

            datos_llya = self.resultados['LLYA'][self.resultados['LLYA']['CODIGO_CURSO'] == codigo_llya].copy()
            datos_myc  = self.resultados['MYC'][self.resultados['MYC']['CODIGO_CURSO']  == codigo_myc].copy()

            if len(datos_llya) == 0 or len(datos_myc) == 0:
                print(f"  ADVERTENCIA: Curso '{nombre}' no tiene datos en ambos programas")
                continue

            periodos_unicos = sorted(
                set(datos_llya['PERIODO_STR'].unique()) | set(datos_myc['PERIODO_STR'].unique())
            )

            periodos_prematuros  = []
            periodos_compartidos = []
            periodos_solo_myc    = []

            for periodo in periodos_unicos:
                llya_p = datos_llya[datos_llya['PERIODO_STR'] == periodo]
                myc_p  = datos_myc[datos_myc['PERIODO_STR']  == periodo]

                # Determinar si cada programa tiene alumnos ACTIVOS en este periodo
                llya_activo = llya_p['TOTAL_MATRICULADOS'].sum() > 0
                myc_activo  = myc_p['TOTAL_MATRICULADOS'].sum() > 0

                if llya_activo and myc_activo:
                    # FASE 2: ambos activos → fusionar
                    periodos_compartidos.append(periodo)

                    est_llya  = llya_p['TOTAL_MATRICULADOS'].iloc[0]
                    est_myc   = myc_p['TOTAL_MATRICULADOS'].iloc[0]
                    est_total = est_llya + est_myc

                    # Iterar por índice de fila para preservar cada fila
                    # aunque varias compartan el mismo TIPO_AMBIENTE.
                    for idx in llya_p.index:
                        tipo_ambiente = self.resultados['LLYA'].loc[idx, 'TIPO_AMBIENTE']
                        horas_curso   = self.resultados['LLYA'].loc[idx, 'HORAS_SEMANALES']
                        secciones     = self.calcular_secciones(est_total, tipo_ambiente)
                        horas_total   = horas_curso * secciones

                        self.resultados['LLYA'].loc[idx, 'TOTAL_MATRICULADOS'] = est_total
                        self.resultados['LLYA'].loc[idx, 'SECCIONES']          = secciones
                        self.resultados['LLYA'].loc[idx, 'HORAS_TOTALES']      = horas_total

                    # Eliminar TODAS las filas de MYC para este curso/periodo de una sola vez
                    mask_myc = (
                        (self.resultados['MYC']['CODIGO_CURSO'] == codigo_myc) &
                        (self.resultados['MYC']['PERIODO_STR']  == periodo)
                    )
                    self.resultados['MYC'] = self.resultados['MYC'][~mask_myc]

                elif llya_activo and not myc_activo:
                    # FASE 1: solo LLYA activo (periodo prematuro)
                    # LLYA se queda con sus propios alumnos sin cambios.
                    # Se eliminan las filas de MYC con 0 alumnos para no ensuciar resultados.
                    periodos_prematuros.append(periodo)

                    mask_myc_cero = (
                        (self.resultados['MYC']['CODIGO_CURSO'] == codigo_myc) &
                        (self.resultados['MYC']['PERIODO_STR']  == periodo) &
                        (self.resultados['MYC']['TOTAL_MATRICULADOS'] == 0)
                    )
                    self.resultados['MYC'] = self.resultados['MYC'][~mask_myc_cero]

                elif myc_activo and not llya_activo:
                    # FASE 3: solo MYC activo (simétrico al prematuro)
                    periodos_solo_myc.append(periodo)

                    mask_llya_cero = (
                        (self.resultados['LLYA']['CODIGO_CURSO'] == codigo_llya) &
                        (self.resultados['LLYA']['PERIODO_STR']  == periodo) &
                        (self.resultados['LLYA']['TOTAL_MATRICULADOS'] == 0)
                    )
                    self.resultados['LLYA'] = self.resultados['LLYA'][~mask_llya_cero]

            # Resumen por curso
            resumen = f"  {nombre}:"
            if periodos_prematuros:
                resumen += f" {len(periodos_prematuros)} periodos prematuros (solo LLYA),"
            if periodos_compartidos:
                resumen += f" {len(periodos_compartidos)} periodos compartidos (fusionados),"
            if periodos_solo_myc:
                resumen += f" {len(periodos_solo_myc)} periodos solo MYC,"
            print(resumen.rstrip(','))

        print(f"  {len(self.cursos_compartidos)} cursos compartidos procesados\n")
    
    def normalizar_tipo_ambiente(self, tipo_ambiente):
        """
        Normaliza el tipo de ambiente para agrupación en resúmenes.
        Mantiene los nombres específicos pero permite agrupar por categoría si es necesario.
        """
        if pd.isna(tipo_ambiente):
            return 'Aula'
        
        tipo_str = str(tipo_ambiente).strip()
        
        # Devolver el nombre exacto
        return tipo_str
    
    def agrupar_por_categoria_ambiente(self, tipo_ambiente):
        """
        Agrupa tipos de ambiente en categorías principales para resúmenes legacy.
        SOLO para compatibilidad con reportes existentes.
        """
        if pd.isna(tipo_ambiente):
            return 'aula'
            
        tipo_lower = str(tipo_ambiente).lower()
        
        if tipo_lower == 'aula':
            return 'aula'
        elif 'laboratorio' in tipo_lower:
            return 'laboratorio'
        elif tipo_lower == 'taller':
            return 'taller'
        elif tipo_lower == 'virtual':
            return 'virtual'
        else:
            return 'aula'  # Por defecto
    
    def generar_resumen_por_periodo(self):
        """Genera el resumen de consumo por periodo."""
        print("\nGenerando resumen por periodo...")
        
        resumen_periodos = []
        
        # Obtener todos los periodos únicos
        todos_periodos = set()
        for programa in self.config['metadata']['programas']:
            periodos = self.resultados[programa]['PERIODO_STR'].unique()
            todos_periodos.update(periodos)
        
        periodos_ordenados = sorted(list(todos_periodos))
        
        for periodo in periodos_ordenados:
            resumen_periodo = {
                'periodo': periodo,
                'año': int(periodo[:4]),
                'ciclo': 'I' if periodo.endswith('01') else 'II',
                'estudiantes': {},
                'horas_semanales': {
                    'aula': 0,
                    'laboratorio': 0,
                    'taller': 0,
                    'virtual': 0,
                    'total': 0
                },
                'horas_semestre': {
                    'aula': 0,
                    'laboratorio': 0,
                    'taller': 0,
                    'virtual': 0,
                    'total': 0
                },
                'secciones': {
                    'aula': 0,
                    'laboratorio': 0,
                    'taller': 0,
                    'virtual': 0,
                    'total': 0
                },
                'detalle_por_programa': {}
            }
            
            # Totales de estudiantes
            total_estudiantes = 0
            total_llya = 0
            total_myc = 0
            
            for programa in self.config['metadata']['programas']:
                datos_periodo = self.resultados[programa][
                    self.resultados[programa]['PERIODO_STR'] == periodo
                ]
                
                if len(datos_periodo) > 0:
                    estudiantes_prog = datos_periodo['TOTAL_MATRICULADOS'].iloc[0]
                    
                    if programa == 'LLYA':
                        total_llya = int(estudiantes_prog)
                    else:
                        total_myc = int(estudiantes_prog)
                    
                    total_estudiantes += estudiantes_prog
                    
                    # Agregar por tipo de ambiente
                    detalle_programa = {
                        'estudiantes': int(estudiantes_prog),
                        'horas_semanales': {},
                        'secciones': {}
                    }
                    
                    # Agrupar por categoría de ambiente
                    for ambiente_categoria in ['aula', 'laboratorio', 'taller', 'virtual']:
                        # Filtrar datos usando la función de agrupación
                        datos_amb = datos_periodo[
                            datos_periodo['TIPO_AMBIENTE'].apply(self.agrupar_por_categoria_ambiente) == ambiente_categoria
                        ]
                        
                        horas = datos_amb['HORAS_TOTALES'].sum()
                        secciones = datos_amb['SECCIONES'].sum()
                        
                        resumen_periodo['horas_semanales'][ambiente_categoria] += horas
                        resumen_periodo['secciones'][ambiente_categoria] += secciones
                        
                        detalle_programa['horas_semanales'][ambiente_categoria] = float(horas)
                        detalle_programa['secciones'][ambiente_categoria] = int(secciones)
                    
                    resumen_periodo['detalle_por_programa'][programa] = detalle_programa
            
            # Calcular totales
            resumen_periodo['estudiantes'] = {
                'total': int(total_estudiantes),
                'llya': total_llya,
                'myc': total_myc
            }
            
            resumen_periodo['horas_semanales']['total'] = sum(resumen_periodo['horas_semanales'].values())
            resumen_periodo['secciones']['total'] = sum(resumen_periodo['secciones'].values())
            
            # Calcular horas por semestre (16 semanas)
            semanas = self.parametros['semanas_por_semestre']
            for ambiente in ['aula', 'laboratorio', 'taller', 'virtual']:
                resumen_periodo['horas_semestre'][ambiente] = (
                    resumen_periodo['horas_semanales'][ambiente] * semanas
                )
            resumen_periodo['horas_semestre']['total'] = (
                resumen_periodo['horas_semanales']['total'] * semanas
            )
            
            resumen_periodos.append(resumen_periodo)
        
        print(f"  {len(resumen_periodos)} periodos procesados")
        
        return resumen_periodos
    
    def generar_resumen_por_semestre(self):
        """Genera el resumen de consumo por semestre académico (1-10)."""
        print("\nGenerando resumen por semestre académico...")
        
        resumen_semestres = []
        
        for semestre in range(1, 11):
            datos_semestre = []
            
            for programa in self.config['metadata']['programas']:
                datos_sem = self.resultados[programa][
                    self.resultados[programa]['SEMESTRE'] == semestre
                ]
                if len(datos_sem) > 0:
                    datos_semestre.append(datos_sem)
            
            if len(datos_semestre) == 0:
                continue
            
            datos_semestre = pd.concat(datos_semestre)
            
            # Obtener información base del semestre
            malla_sem = pd.concat([
                self.mallas[prog][self.mallas[prog]['SEMESTRE'] == semestre]
                for prog in self.config['metadata']['programas']
            ])
            
            resumen_sem = {
                'semestre': semestre,
                'cursos': len(malla_sem),
                'creditos_totales': int(malla_sem['CREDITOS'].sum()),
                'horas_curso_semanales': int(malla_sem['TOTAL_HORAS_SEMANALES'].sum()),
                'estadisticas': {
                    'promedio_estudiantes': float(datos_semestre['TOTAL_MATRICULADOS'].mean()),
                    'maximo_estudiantes': int(datos_semestre['TOTAL_MATRICULADOS'].max()),
                    'minimo_estudiantes': int(datos_semestre['TOTAL_MATRICULADOS'].min()),
                    'promedio_secciones': float(datos_semestre['SECCIONES'].mean()),
                    'promedio_horas_semanales': float(datos_semestre.groupby('PERIODO_STR')['HORAS_TOTALES'].sum().mean())
                },
                'distribucion_tipo_ambiente': {}
            }
            
            # Distribución por tipo de ambiente
            for ambiente in ['aula', 'laboratorio', 'taller', 'virtual']:
                datos_amb = datos_semestre[datos_semestre['TIPO_AMBIENTE'].apply(self.agrupar_por_categoria_ambiente) == ambiente]
                
                if len(datos_amb) > 0:
                    horas_prom = datos_amb.groupby('PERIODO_STR')['HORAS_TOTALES'].sum().mean()
                    
                    resumen_sem['distribucion_tipo_ambiente'][ambiente] = {
                        'horas_semanales': float(horas_prom),
                        'porcentaje': float((horas_prom / resumen_sem['estadisticas']['promedio_horas_semanales']) * 100) if resumen_sem['estadisticas']['promedio_horas_semanales'] > 0 else 0
                    }
                else:
                    resumen_sem['distribucion_tipo_ambiente'][ambiente] = {
                        'horas_semanales': 0,
                        'porcentaje': 0
                    }
            
            resumen_semestres.append(resumen_sem)
        
        print(f"  {len(resumen_semestres)} semestres procesados")
        
        return resumen_semestres
    
    def generar_resumen_por_año(self):
        """Genera el resumen de consumo por año."""
        print("\nGenerando resumen por año...")
        
        resumen_años = []
        
        # Combinar todos los datos
        todos_datos = pd.concat([self.resultados[prog] for prog in self.config['metadata']['programas']])
        
        años_unicos = sorted(todos_datos['AÑO'].unique())
        
        for año in años_unicos:
            datos_año = todos_datos[todos_datos['AÑO'] == año]
            
            # Calcular estudiantes únicos por año (tomar el máximo de cada ciclo)
            est_ciclo_i = datos_año[datos_año['CICLO'] == 'I']['TOTAL_MATRICULADOS'].max()
            est_ciclo_ii = datos_año[datos_año['CICLO'] == 'II']['TOTAL_MATRICULADOS'].max()
            
            total_est = max(est_ciclo_i if pd.notna(est_ciclo_i) else 0,
                           est_ciclo_ii if pd.notna(est_ciclo_ii) else 0)
            
            resumen_año = {
                'año': int(año),
                'total_estudiantes_año': int(total_est),
                'horas_anuales': {},
                'promedio_semanal': {}
            }
            
            # Horas anuales por tipo de ambiente
            for ambiente in ['aula', 'laboratorio', 'taller', 'virtual']:
                datos_amb = datos_año[datos_año['TIPO_AMBIENTE'].apply(self.agrupar_por_categoria_ambiente) == ambiente]
                horas_totales = datos_amb['HORAS_TOTALES'].sum() * self.parametros['semanas_por_semestre']
                resumen_año['horas_anuales'][ambiente] = float(horas_totales)
            
            resumen_año['horas_anuales']['total'] = sum(resumen_año['horas_anuales'].values())
            
            # Promedios semanales por ciclo
            ciclo_i = datos_año[datos_año['CICLO'] == 'I']
            ciclo_ii = datos_año[datos_año['CICLO'] == 'II']
            
            prom_i = ciclo_i.groupby('PERIODO_STR')['HORAS_TOTALES'].sum().mean() if len(ciclo_i) > 0 else 0
            prom_ii = ciclo_ii.groupby('PERIODO_STR')['HORAS_TOTALES'].sum().mean() if len(ciclo_ii) > 0 else 0
            
            resumen_año['promedio_semanal'] = {
                'ciclo_i': float(prom_i),
                'ciclo_ii': float(prom_ii),
                'promedio': float((prom_i + prom_ii) / 2)
            }
            
            resumen_años.append(resumen_año)
        
        print(f"  {len(resumen_años)} años procesados")
        
        return resumen_años
    
    def convertir_tipos_python(self, obj):
        """Convierte tipos numpy a tipos nativos de Python para JSON."""
        if isinstance(obj, dict):
            return {k: self.convertir_tipos_python(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convertir_tipos_python(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    def generar_detalle_ambientes_especificos(self):
        """
        Genera un detalle de horas por tipo de ambiente ESPECÍFICO (sin agrupar).
        Muestra por separado: Laboratorio de Química, Laboratorio de Computadoras, etc.
        """
        print("\nGenerando detalle de ambientes específicos...")
        
        detalle_ambientes = []
        
        # Combinar datos de todos los programas
        todos_datos = pd.concat([self.resultados[prog] for prog in self.config['metadata']['programas']])
        
        # Obtener todos los periodos únicos
        periodos_unicos = sorted(todos_datos['PERIODO_STR'].unique())
        
        for periodo in periodos_unicos:
            datos_periodo = todos_datos[todos_datos['PERIODO_STR'] == periodo]
            
            # Agrupar por tipo de ambiente ESPECÍFICO
            resumen_ambientes = datos_periodo.groupby('TIPO_AMBIENTE').agg({
                'HORAS_TOTALES': 'sum',
                'SECCIONES': 'sum',
                'TOTAL_MATRICULADOS': 'first'  # Solo para referencia
            }).reset_index()
            
            detalle_periodo = {
                'periodo': periodo,
                'ambientes': {}
            }
            
            for _, row in resumen_ambientes.iterrows():
                ambiente = row['TIPO_AMBIENTE']
                detalle_periodo['ambientes'][ambiente] = {
                    'horas_semanales': float(row['HORAS_TOTALES']),
                    'secciones': int(row['SECCIONES']),
                    'horas_semestre': float(row['HORAS_TOTALES'] * self.parametros['semanas_por_semestre'])
                }
            
            detalle_ambientes.append(detalle_periodo)
        
        print(f"  Detalle de ambientes específicos generado para {len(detalle_ambientes)} periodos")
        
        return detalle_ambientes
    
    def generar_detalle_cursos_por_periodo(self):
        """
        Genera el detalle de cada curso activo por periodo, conservando
        programa, semestre, tipo de ambiente, estudiantes, secciones y horas.
        Solo incluye filas con HORAS_TOTALES > 0.
        """
        print("\nGenerando detalle de cursos por periodo...")

        frames = []
        for prog in self.config['metadata']['programas']:
            df = self.resultados[prog].copy()
            df['PROGRAMA'] = prog
            frames.append(df)

        todos = pd.concat(frames, ignore_index=True)
        activos = todos[todos['HORAS_TOTALES'] > 0].copy()

        # Resolver el nombre del curso (merge crea CURSO_x/CURSO_y)
        if 'CURSO_y' in activos.columns:
            activos['NOMBRE_CURSO'] = activos['CURSO_y'].fillna(activos.get('CURSO_x', ''))
        elif 'CURSO_x' in activos.columns:
            activos['NOMBRE_CURSO'] = activos['CURSO_x']
        else:
            activos['NOMBRE_CURSO'] = activos.get('CURSO', '')

        resultado = []
        for periodo in sorted(activos['PERIODO_STR'].unique()):
            filas_p = activos[activos['PERIODO_STR'] == periodo].sort_values(
                ['PROGRAMA', 'SEMESTRE', 'NOMBRE_CURSO', 'TIPO_AMBIENTE']
            )
            cursos = []
            for _, r in filas_p.iterrows():
                cursos.append({
                    'programa'       : str(r['PROGRAMA']),
                    'semestre'       : int(r['SEMESTRE']),
                    'codigo_curso'   : str(r['CODIGO_CURSO']),
                    'curso'          : str(r['NOMBRE_CURSO']),
                    'tipo_ambiente'  : str(r['TIPO_AMBIENTE']),
                    'estudiantes'    : int(r['TOTAL_MATRICULADOS']),
                    'horas_semanales': float(r['HORAS_SEMANALES']),
                    'secciones'      : int(r['SECCIONES']),
                    'horas_totales'  : float(r['HORAS_TOTALES']),
                })
            resultado.append({'periodo': periodo, 'cursos': cursos})

        print(f"  Detalle de cursos generado para {len(resultado)} periodos")
        return resultado

    def generar_json(self, resumen_periodos, resumen_semestres, resumen_años):
        """Genera el archivo JSON con todos los resultados."""
        print("\nGenerando archivo JSON...")

        # Generar detalle de ambientes específicos
        detalle_ambientes = self.generar_detalle_ambientes_especificos()

        # Generar detalle de cursos por periodo (para hojas de verificación Excel)
        detalle_cursos = self.generar_detalle_cursos_por_periodo()

        # Encontrar periodo pico
        periodo_pico = max(resumen_periodos, key=lambda x: x['horas_semanales']['total'])

        resultado_json = {
            'metadata': {
                'carrera': self.config['metadata']['carrera'],
                'programas': self.config['metadata']['programas'],
                'fecha_analisis': self.config['metadata']['fecha_analisis'],
                'periodo_proyeccion': f"{resumen_periodos[0]['periodo']} a {resumen_periodos[-1]['periodo']}",
                'parametros': self.parametros
            },
            'resumen_total': {
                'periodo_pico': {
                    'periodo': periodo_pico['periodo'],
                    'horas_semanales_totales': periodo_pico['horas_semanales']['total'],
                    'estudiantes': periodo_pico['estudiantes']['total']
                },
                'distribucion_pico': periodo_pico['horas_semanales']
            },
            'consumo_por_periodo': resumen_periodos,
            'consumo_por_semestre_academico': resumen_semestres,
            'consumo_por_año': resumen_años,
            'detalle_ambientes_especificos': detalle_ambientes,
            'detalle_cursos_por_periodo': detalle_cursos,
        }
        
        # Convertir todos los tipos numpy a tipos nativos de Python
        resultado_json = self.convertir_tipos_python(resultado_json)
        
        # Guardar JSON
        output_path = self.config['output']['json']
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultado_json, f, indent=2, ensure_ascii=False)
        
        print(f"  JSON guardado en: {output_path}")
        
        return resultado_json
    
    def ejecutar(self):
        """Ejecuta el análisis completo con optimización de equivalencias."""
        print("\nIniciando análisis completo con equivalencias...\n")
        
        # 1. Cargar datos (incluye equivalencias)
        self.cargar_datos()
        
        # 2. Identificar equivalencias
        self.identificar_cursos_compartidos()
        self.identificar_cursos_a_eliminar()
        
        # 3. Procesar cada programa (con filtros)
        for programa in self.config['metadata']['programas']:
            self.procesar_programa(programa)
        
        # 4. Procesar cursos compartidos
        self.procesar_cursos_compartidos()
        
        # 5. Generar resúmenes
        resumen_periodos = self.generar_resumen_por_periodo()
        resumen_semestres = self.generar_resumen_por_semestre()
        resumen_años = self.generar_resumen_por_año()
        
        # 6. Generar JSON
        resultado_json = self.generar_json(resumen_periodos, resumen_semestres, resumen_años)
        
        print("\n" + "=" * 80)
        print("ANÁLISIS COMPLETADO EXITOSAMENTE (CON EQUIVALENCIAS)")
        print("=" * 80)
        print(f"\nOptimizacion aplicada:")
        print(f"  - Cursos compartidos LLYA↔MYC: {len(self.cursos_compartidos)}")
        print(f"  - Cursos eliminados (van a otras carreras): {sum(len(v) for v in self.cursos_a_eliminar.values())}")
        print(f"\nPeriodo pico: {resultado_json['resumen_total']['periodo_pico']['periodo']}")
        print(f"Horas semanales totales (pico): {resultado_json['resumen_total']['periodo_pico']['horas_semanales_totales']:.2f}")
        print(f"Estudiantes (pico): {resultado_json['resumen_total']['periodo_pico']['estudiantes']}")
        print(f"\nDistribución en periodo pico:")
        for ambiente, horas in resultado_json['resumen_total']['distribucion_pico'].items():
            if ambiente != 'total':
                print(f"  - {ambiente.capitalize()}: {horas:.2f} horas/semana")
        
        return resultado_json


if __name__ == "__main__":
    analizador = AnalizadorHorasAula()
    resultado = analizador.ejecutar()
