"""
Generador de Excel para Verificación
Crea un archivo Excel con múltiples hojas para verificar los resultados
"""

import pandas as pd
import json
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

class GeneradorExcel:
    """
    Clase para generar el archivo Excel de verificación.
    """
    
    def __init__(self, json_path, output_path):
        """Inicializa el generador."""
        self.json_path = json_path
        self.output_path = output_path
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.datos = json.load(f)
        
        print("GENERADOR DE EXCEL - VERIFICACIÓN")
        
    def crear_hoja_resumen(self, writer):
        """Crea la hoja de resumen ejecutivo."""
        print("\n Generando hoja: Resumen Ejecutivo...")
        
        resumen_data = []
        
        # Información general
        resumen_data.append(['RESUMEN EJECUTIVO - CONSUMO DE HORAS-AULA', ''])
        resumen_data.append(['', ''])
        resumen_data.append(['Carrera:', self.datos['metadata']['carrera']])
        resumen_data.append(['Programas:', ', '.join(self.datos['metadata']['programas'])])
        resumen_data.append(['Periodo de Proyección:', self.datos['metadata']['periodo_proyeccion']])
        resumen_data.append(['Fecha de Análisis:', self.datos['metadata']['fecha_analisis']])
        resumen_data.append(['', ''])
        
        # Parámetros
        resumen_data.append(['PARÁMETROS UTILIZADOS', ''])
        resumen_data.append(['Tamaño Sección Aula:', self.datos['metadata']['parametros']['tamano_seccion_aula']])
        resumen_data.append(['Tamaño Sección Laboratorio:', self.datos['metadata']['parametros']['tamano_seccion_laboratorio']])
        resumen_data.append(['Tamaño Sección Taller:', self.datos['metadata']['parametros']['tamano_seccion_taller']])
        resumen_data.append(['Semanas por Semestre:', self.datos['metadata']['parametros']['semanas_por_semestre']])
        resumen_data.append(['', ''])
        
        # Periodo pico
        pico = self.datos['resumen_total']['periodo_pico']
        resumen_data.append(['PERIODO PICO', ''])
        resumen_data.append(['Periodo:', pico['periodo']])
        resumen_data.append(['Horas Semanales Totales:', f"{pico['horas_semanales_totales']:.2f}"])
        resumen_data.append(['Estudiantes:', pico['estudiantes']])
        resumen_data.append(['', ''])
        
        # Distribución en periodo pico
        resumen_data.append(['DISTRIBUCIÓN HORAS PERIODO PICO', 'Horas/Semana'])
        dist = self.datos['resumen_total']['distribucion_pico']
        resumen_data.append(['Aula', f"{dist['aula']:.2f}"])
        resumen_data.append(['Laboratorio', f"{dist['laboratorio']:.2f}"])
        resumen_data.append(['Taller', f"{dist['taller']:.2f}"])
        resumen_data.append(['Virtual', f"{dist['virtual']:.2f}"])
        resumen_data.append(['TOTAL', f"{dist['total']:.2f}"])
        
        df_resumen = pd.DataFrame(resumen_data, columns=['Concepto', 'Valor'])
        df_resumen.to_excel(writer, sheet_name='Resumen Ejecutivo', index=False)
        
        print("   Hoja 'Resumen Ejecutivo' creada")
    
    def crear_hoja_por_periodo(self, writer):
        """Crea la hoja con consumo por periodo."""
        print("\n Generando hoja: Consumo por Periodo...")
        
        periodos_data = []
        
        for periodo in self.datos['consumo_por_periodo']:
            periodos_data.append({
                'Periodo': periodo['periodo'],
                'Año': periodo['año'],
                'Ciclo': periodo['ciclo'],
                'Estudiantes Total': periodo['estudiantes']['total'],
                'Estudiantes LLYA': periodo['estudiantes']['llya'],
                'Estudiantes MYC': periodo['estudiantes']['myc'],
                'Aula (hrs/sem)': f"{periodo['horas_semanales']['aula']:.2f}",
                'Laboratorio (hrs/sem)': f"{periodo['horas_semanales']['laboratorio']:.2f}",
                'Taller (hrs/sem)': f"{periodo['horas_semanales']['taller']:.2f}",
                'Virtual (hrs/sem)': f"{periodo['horas_semanales']['virtual']:.2f}",
                'Total (hrs/sem)': f"{periodo['horas_semanales']['total']:.2f}",
                'Aula (hrs/semestre)': f"{periodo['horas_semestre']['aula']:.2f}",
                'Laboratorio (hrs/semestre)': f"{periodo['horas_semestre']['laboratorio']:.2f}",
                'Taller (hrs/semestre)': f"{periodo['horas_semestre']['taller']:.2f}",
                'Virtual (hrs/semestre)': f"{periodo['horas_semestre']['virtual']:.2f}",
                'Total (hrs/semestre)': f"{periodo['horas_semestre']['total']:.2f}",
                'Secciones Aula': periodo['secciones']['aula'],
                'Secciones Laboratorio': periodo['secciones']['laboratorio'],
                'Secciones Taller': periodo['secciones']['taller'],
                'Secciones Virtual': periodo['secciones']['virtual'],
                'Secciones Total': periodo['secciones']['total']
            })
        
        df_periodos = pd.DataFrame(periodos_data)
        df_periodos.to_excel(writer, sheet_name='Consumo por Periodo', index=False)
        
        print(f"  Hoja 'Consumo por Periodo' creada ({len(periodos_data)} periodos)")
    
    def crear_hoja_por_semestre(self, writer):
        """Crea la hoja con consumo por semestre académico."""
        print("\n Generando hoja: Consumo por Semestre...")
        
        semestres_data = []
        
        for sem in self.datos['consumo_por_semestre_academico']:
            semestres_data.append({
                'Semestre': sem['semestre'],
                'Cursos': sem['cursos'],
                'Créditos Totales': sem['creditos_totales'],
                'Horas Curso Semanales': sem['horas_curso_semanales'],
                'Prom Estudiantes': f"{sem['estadisticas']['promedio_estudiantes']:.2f}",
                'Máx Estudiantes': sem['estadisticas']['maximo_estudiantes'],
                'Mín Estudiantes': sem['estadisticas']['minimo_estudiantes'],
                'Prom Secciones': f"{sem['estadisticas']['promedio_secciones']:.2f}",
                'Prom Horas/Semana': f"{sem['estadisticas']['promedio_horas_semanales']:.2f}",
                'Aula (hrs)': f"{sem['distribucion_tipo_ambiente']['aula']['horas_semanales']:.2f}",
                'Aula (%)': f"{sem['distribucion_tipo_ambiente']['aula']['porcentaje']:.1f}%",
                'Laboratorio (hrs)': f"{sem['distribucion_tipo_ambiente']['laboratorio']['horas_semanales']:.2f}",
                'Laboratorio (%)': f"{sem['distribucion_tipo_ambiente']['laboratorio']['porcentaje']:.1f}%",
                'Taller (hrs)': f"{sem['distribucion_tipo_ambiente']['taller']['horas_semanales']:.2f}",
                'Taller (%)': f"{sem['distribucion_tipo_ambiente']['taller']['porcentaje']:.1f}%",
                'Virtual (hrs)': f"{sem['distribucion_tipo_ambiente']['virtual']['horas_semanales']:.2f}",
                'Virtual (%)': f"{sem['distribucion_tipo_ambiente']['virtual']['porcentaje']:.1f}%"
            })
        
        df_semestres = pd.DataFrame(semestres_data)
        df_semestres.to_excel(writer, sheet_name='Consumo por Semestre', index=False)
        
        print(f"  Hoja 'Consumo por Semestre' creada ({len(semestres_data)} semestres)")
    
    def crear_hoja_por_año(self, writer):
        """Crea la hoja con consumo por año."""
        print("\n Generando hoja: Consumo por Año...")
        
        años_data = []
        
        for año in self.datos['consumo_por_año']:
            años_data.append({
                'Año': año['año'],
                'Estudiantes': año['total_estudiantes_año'],
                'Aula (hrs/año)': f"{año['horas_anuales']['aula']:.2f}",
                'Laboratorio (hrs/año)': f"{año['horas_anuales']['laboratorio']:.2f}",
                'Taller (hrs/año)': f"{año['horas_anuales']['taller']:.2f}",
                'Virtual (hrs/año)': f"{año['horas_anuales']['virtual']:.2f}",
                'Total (hrs/año)': f"{año['horas_anuales']['total']:.2f}",
                'Prom Ciclo I (hrs/sem)': f"{año['promedio_semanal']['ciclo_i']:.2f}",
                'Prom Ciclo II (hrs/sem)': f"{año['promedio_semanal']['ciclo_ii']:.2f}",
                'Prom Anual (hrs/sem)': f"{año['promedio_semanal']['promedio']:.2f}"
            })
        
        df_años = pd.DataFrame(años_data)
        df_años.to_excel(writer, sheet_name='Consumo por Año', index=False)
        
        print(f"  Hoja 'Consumo por Año' creada ({len(años_data)} años)")
    
    def crear_hoja_tabla_pivote(self, writer):
        """Crea una tabla pivote simplificada."""
        print("\n Generando hoja: Tabla Pivote...")
        
        # Crear matriz Periodo x Tipo de Ambiente
        periodos = []
        for p in self.datos['consumo_por_periodo']:
            periodos.append({
                'Periodo': p['periodo'],
                'Aula': p['horas_semanales']['aula'],
                'Laboratorio': p['horas_semanales']['laboratorio'],
                'Taller': p['horas_semanales']['taller'],
                'Virtual': p['horas_semanales']['virtual'],
                'Total': p['horas_semanales']['total']
            })
        
        df_pivote = pd.DataFrame(periodos)
        df_pivote.to_excel(writer, sheet_name='Tabla Pivote', index=False)
        
        print("  Hoja 'Tabla Pivote' creada")
    
    def generar(self):
        """Genera el archivo Excel completo."""
        print("\n Generando archivo Excel...")
        
        with pd.ExcelWriter(self.output_path, engine='openpyxl') as writer:
            self.crear_hoja_resumen(writer)
            self.crear_hoja_por_periodo(writer)
            self.crear_hoja_por_semestre(writer)
            self.crear_hoja_por_año(writer)
            self.crear_hoja_tabla_pivote(writer)
        
        print(f"\n Excel guardado en: {self.output_path}")
        
        print(" EXCEL DE VERIFICACIÓN GENERADO EXITOSAMENTE")
        

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python generador_excel.py <json_path> <output_path>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_path = sys.argv[2]
    
    generador = GeneradorExcel(json_path, output_path)
    generador.generar()
