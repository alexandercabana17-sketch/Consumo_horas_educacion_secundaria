"""
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
        self.resultados = {}
        
        print(f"ANALIZADOR DE HORAS-AULA - {self.config['metadata']['carrera']}")
        print(f"Fecha: {self.config['metadata']['fecha_analisis']}")
        print(f"Programas: {', '.join(self.config['metadata']['programas'])}")
        print(f"\nParámetros:")
        print(f"  - Tamaño sección Aula: {self.parametros['tamano_seccion_aula']} estudiantes")
        print(f"  - Tamaño sección Laboratorio: {self.parametros['tamano_seccion_laboratorio']} estudiantes")
        print(f"  - Tamaño sección Taller: {self.parametros['tamano_seccion_taller']} estudiantes")
        print(f"  - Semanas por semestre: {self.parametros['semanas_por_semestre']}")
        
    def cargar_datos(self):
        """Carga las mallas curriculares y proyecciones de matrícula."""
        
        for programa in self.config['metadata']['programas']:
            # Cargar malla curricular
            malla_path = self.archivos[programa]['malla']
            self.mallas[programa] = pd.read_excel(malla_path)
            print(f"  ✓ Malla {programa}: {len(self.mallas[programa])} cursos")
            
            # Cargar proyección
            proy_path = self.archivos[programa]['proyeccion']
            self.proyecciones[programa] = pd.read_excel(proy_path)
            print(f"  ✓ Proyección {programa}: {len(self.proyecciones[programa])} registros")
        
        print(" Datos cargados exitosamente\n")
    
    def mapear_tipo_ambiente(self, row):
        """
        Determina el tipo de ambiente basado en las columnas de la malla.
        Retorna: lista de tuplas (tipo_ambiente, horas)
        """
        ambientes = []
        
        # Horas teóricas
        if pd.notna(row['HORAS_TEORICAS']) and row['HORAS_TEORICAS'] > 0:
            if pd.notna(row['TIPO_AMBIENTE_TEORIA']):
                if str(row['TIPO_AMBIENTE_TEORIA']).lower() == 'virtual':
                    ambientes.append(('virtual', row['HORAS_TEORICAS']))
                else:
                    ambientes.append(('aula', row['HORAS_TEORICAS']))
            else:
                ambientes.append(('aula', row['HORAS_TEORICAS']))
        
        # Horas prácticas
        if pd.notna(row['HORAS_PRACTICAS']) and row['HORAS_PRACTICAS'] > 0:
            if pd.notna(row['TIPO_AMBIENTE_PRACTICA']):
                tipo_prac = str(row['TIPO_AMBIENTE_PRACTICA']).lower()
                if 'laboratorio' in tipo_prac:
                    ambientes.append(('laboratorio', row['HORAS_PRACTICAS']))
                elif 'taller' in tipo_prac:
                    ambientes.append(('taller', row['HORAS_PRACTICAS']))
                elif 'virtual' in tipo_prac:
                    ambientes.append(('virtual', row['HORAS_PRACTICAS']))
                else:
                    ambientes.append(('laboratorio', row['HORAS_PRACTICAS']))
            else:
                ambientes.append(('laboratorio', row['HORAS_PRACTICAS']))
        
        # Si no hay ambientes, retornar lista vacía
        if not ambientes:
            ambientes.append(('aula', 0))
        
        return ambientes
    
    def calcular_secciones(self, num_estudiantes, tipo_ambiente):
        """
        Calcula el número de secciones necesarias según el tipo de ambiente.
        """
        if num_estudiantes == 0:
            return 0
        
        if tipo_ambiente == 'aula':
            max_estudiantes = self.parametros['tamano_seccion_aula']
        elif tipo_ambiente == 'laboratorio':
            max_estudiantes = self.parametros['tamano_seccion_laboratorio']
        elif tipo_ambiente == 'taller':
            max_estudiantes = self.parametros['tamano_seccion_taller']
        else:  # virtual
            return 1  # Virtual no se divide en secciones
        
        return math.ceil(num_estudiantes / max_estudiantes)
    
    def procesar_programa(self, programa):
        """Procesa un programa específico (LLYA o MYC)."""
        
        malla = self.mallas[programa].copy()
        proyeccion = self.proyecciones[programa].copy()
        
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
    
    def generar_resumen_por_periodo(self):
        """Genera el resumen de consumo por periodo."""
        
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
                    
                    for ambiente in ['aula', 'laboratorio', 'taller', 'virtual']:
                        datos_amb = datos_periodo[datos_periodo['TIPO_AMBIENTE'] == ambiente]
                        
                        horas = datos_amb['HORAS_TOTALES'].sum()
                        secciones = datos_amb['SECCIONES'].sum()
                        
                        resumen_periodo['horas_semanales'][ambiente] += horas
                        resumen_periodo['secciones'][ambiente] += secciones
                        
                        detalle_programa['horas_semanales'][ambiente] = float(horas)
                        detalle_programa['secciones'][ambiente] = int(secciones)
                    
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
        print("\n Generando resumen por semestre académico...")
        
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
                datos_amb = datos_semestre[datos_semestre['TIPO_AMBIENTE'] == ambiente]
                
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
        
        print(f" {len(resumen_semestres)} semestres procesados")
        
        return resumen_semestres
    
    def generar_resumen_por_año(self):
        """Genera el resumen de consumo por año."""
        
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
                datos_amb = datos_año[datos_año['TIPO_AMBIENTE'] == ambiente]
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
        
        print(f" {len(resumen_años)} años procesados")
        
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
    
    def generar_json(self, resumen_periodos, resumen_semestres, resumen_años):
        """Genera el archivo JSON con todos los resultados."""
        print("\n Generando archivo JSON...")
        
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
            'consumo_por_año': resumen_años
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
        """Ejecuta el análisis completo."""
        print("\n Iniciando análisis completo...\n")
        
        # 1. Cargar datos
        self.cargar_datos()
        
        # 2. Procesar cada programa
        for programa in self.config['metadata']['programas']:
            self.procesar_programa(programa)
        
        # 3. Generar resúmenes
        resumen_periodos = self.generar_resumen_por_periodo()
        resumen_semestres = self.generar_resumen_por_semestre()
        resumen_años = self.generar_resumen_por_año()
        
        # 4. Generar JSON
        resultado_json = self.generar_json(resumen_periodos, resumen_semestres, resumen_años)
                
        print("ANÁLISIS COMPLETADO EXITOSAMENTE")
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
