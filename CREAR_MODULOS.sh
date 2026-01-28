#!/bin/bash

# Script para crear todos los módulos restantes

# ============================================================================
# PROCESADORES
# ============================================================================

cat > src/procesadores/calculador_secciones.py << 'FIN'
"""Módulo Calculador de Secciones"""
import math
from ..utilidades.registro import obtener_registrador

class CalculadorSecciones:
    def __init__(self, gestor_config):
        self.config = gestor_config
        self.registro = obtener_registrador()
        self.capacidades = {
            'aula': self.config.obtener_tamano_seccion('aula'),
            'laboratorio': self.config.obtener_tamano_seccion('laboratorio'),
            'taller': self.config.obtener_tamano_seccion('taller'),
            'virtual': 1
        }
    
    def calcular(self, num_estudiantes: int, tipo_ambiente: str) -> int:
        if num_estudiantes == 0 or tipo_ambiente == 'virtual':
            return 1 if num_estudiantes > 0 else 0
        capacidad = self.capacidades.get(tipo_ambiente, self.capacidades['aula'])
        return math.ceil(num_estudiantes / capacidad)
    
    def calcular_horas_totales(self, horas_curso: float, num_estudiantes: int, tipo_ambiente: str) -> tuple:
        secciones = self.calcular(num_estudiantes, tipo_ambiente)
        horas_totales = horas_curso * secciones
        return secciones, horas_totales
FIN

cat > src/procesadores/procesador_mallas.py << 'FIN'
"""Módulo Procesador de Mallas"""
import pandas as pd
from typing import List, Dict, Tuple
from ..utilidades.registro import obtener_registrador
from ..utilidades.ayudantes import mapear_tipo_ambiente

class ProcesadorMallas:
    def __init__(self):
        self.registro = obtener_registrador()
    
    def mapear_ambientes_curso(self, fila: pd.Series) -> List[Tuple[str, float]]:
        ambientes = []
        if pd.notna(fila.get('HORAS_TEORICAS', 0)) and fila['HORAS_TEORICAS'] > 0:
            tipo_teoria = fila.get('TIPO_AMBIENTE_TEORIA', 'Aula')
            tipo_ambiente = mapear_tipo_ambiente(tipo_teoria)
            ambientes.append((tipo_ambiente, float(fila['HORAS_TEORICAS'])))
        
        if pd.notna(fila.get('HORAS_PRACTICAS', 0)) and fila['HORAS_PRACTICAS'] > 0:
            tipo_practica = fila.get('TIPO_AMBIENTE_PRACTICA', 'Laboratorio')
            tipo_ambiente = mapear_tipo_ambiente(tipo_practica)
            ambientes.append((tipo_ambiente, float(fila['HORAS_PRACTICAS'])))
        
        if not ambientes and pd.notna(fila.get('TOTAL_HORAS_SEMANALES', 0)):
            if fila['TOTAL_HORAS_SEMANALES'] > 0:
                ambientes.append(('aula', float(fila['TOTAL_HORAS_SEMANALES'])))
        
        return ambientes
    
    def expandir_malla(self, df: pd.DataFrame, programa: str) -> pd.DataFrame:
        self.registro.info(f"  Expandiendo malla {programa}...")
        registros = []
        
        for _, fila in df.iterrows():
            ambientes = self.mapear_ambientes_curso(fila)
            for tipo_ambiente, horas in ambientes:
                registros.append({
                    'PROGRAMA': programa,
                    'CODIGO_CURSO': fila['CODIGO_CURSO'],
                    'CURSO': fila['CURSO'],
                    'SEMESTRE': int(fila['SEMESTRE']),
                    'TIPO_AMBIENTE': tipo_ambiente,
                    'HORAS_SEMANALES': horas
                })
        
        df_expandido = pd.DataFrame(registros)
        self.registro.info(f"    ✓ {len(df)} cursos → {len(df_expandido)} registros")
        return df_expandido
    
    def procesar_todas_las_mallas(self, mallas: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        self.registro.info("\n📐 Procesando mallas curriculares...")
        mallas_expandidas = {}
        for programa, df in mallas.items():
            mallas_expandidas[programa] = self.expandir_malla(df, programa)
        self.registro.info("  ✅ Mallas procesadas\n")
        return mallas_expandidas
FIN

cat > src/procesadores/procesador_proyecciones.py << 'FIN'
"""Módulo Procesador de Proyecciones"""
import pandas as pd
from typing import Dict
from ..utilidades.registro import obtener_registrador
from ..utilidades.ayudantes import formatear_periodo, extraer_anio_ciclo
from .calculador_secciones import CalculadorSecciones

class ProcesadorProyecciones:
    def __init__(self, gestor_config):
        self.config = gestor_config
        self.registro = obtener_registrador()
        self.calculador = CalculadorSecciones(gestor_config)
    
    def preparar_proyeccion(self, df: pd.DataFrame, programa: str) -> pd.DataFrame:
        df = df.copy()
        df['PERIODO_STR'] = df['PERIODO'].apply(formatear_periodo)
        df['ANIO'] = df['PERIODO_STR'].apply(lambda x: extraer_anio_ciclo(x)[0])
        df['CICLO'] = df['PERIODO_STR'].apply(lambda x: extraer_anio_ciclo(x)[1])
        df['PROGRAMA'] = programa
        return df
    
    def combinar_con_malla(self, proyeccion: pd.DataFrame, malla_expandida: pd.DataFrame, programa: str) -> pd.DataFrame:
        self.registro.info(f"  Combinando proyección + malla {programa}...")
        combinado = proyeccion.merge(
            malla_expandida[['CODIGO_CURSO', 'SEMESTRE', 'TIPO_AMBIENTE', 'HORAS_SEMANALES', 'CURSO']],
            on=['CODIGO_CURSO', 'SEMESTRE'],
            how='left'
        )
        
        combinado['SECCIONES'] = combinado.apply(
            lambda fila: self.calculador.calcular(
                int(fila['TOTAL_MATRICULADOS']) if pd.notna(fila['TOTAL_MATRICULADOS']) else 0,
                fila['TIPO_AMBIENTE'] if pd.notna(fila['TIPO_AMBIENTE']) else 'aula'
            ),
            axis=1
        )
        
        combinado['HORAS_TOTALES'] = combinado.apply(
            lambda fila: (
                float(fila['HORAS_SEMANALES']) * int(fila['SECCIONES'])
                if pd.notna(fila['HORAS_SEMANALES']) and pd.notna(fila['SECCIONES'])
                else 0.0
            ),
            axis=1
        )
        
        self.registro.info(f"    ✓ {len(combinado)} registros combinados")
        return combinado
    
    def procesar_todas_las_proyecciones(self, proyecciones: Dict[str, pd.DataFrame], mallas_expandidas: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        self.registro.info("\n🔄 Procesando proyecciones...")
        proyecciones_procesadas = {}
        for programa in proyecciones.keys():
            proy_prep = self.preparar_proyeccion(proyecciones[programa], programa)
            proyecciones_procesadas[programa] = self.combinar_con_malla(proy_prep, mallas_expandidas[programa], programa)
        self.registro.info("  ✅ Proyecciones procesadas\n")
        return proyecciones_procesadas
FIN

# ============================================================================
# ANALIZADORES
# ============================================================================

cat > src/analizadores/analizador_periodos.py << 'FIN'
"""Módulo Analizador de Periodos"""
import pandas as pd
from typing import Dict, List
from ..utilidades.registro import obtener_registrador
from ..utilidades.ayudantes import convertir_a_tipos_python

class AnalizadorPeriodos:
    def __init__(self, gestor_config):
        self.config = gestor_config
        self.registro = obtener_registrador()
        self.semanas = gestor_config.obtener_semanas_semestre()
    
    def analizar(self, proyecciones_procesadas: Dict[str, pd.DataFrame]) -> List[Dict]:
        self.registro.info("📊 Analizando consumo por periodo...")
        todos_datos = pd.concat(proyecciones_procesadas.values(), ignore_index=True)
        periodos = sorted(todos_datos['PERIODO_STR'].unique())
        resumen_periodos = []
        
        for periodo in periodos:
            datos_periodo = todos_datos[todos_datos['PERIODO_STR'] == periodo]
            anio, ciclo = int(periodo[:4]), 'I' if periodo.endswith('01') else 'II'
            
            est_por_programa = {}
            total_estudiantes = 0
            
            for programa in self.config.obtener_programas():
                datos_prog = datos_periodo[datos_periodo['PROGRAMA'] == programa]
                if len(datos_prog) > 0:
                    est = int(datos_prog['TOTAL_MATRICULADOS'].iloc[0])
                    est_por_programa[programa.lower()] = est
                    total_estudiantes += est
                else:
                    est_por_programa[programa.lower()] = 0
            
            horas_semanales = {'aula': 0, 'laboratorio': 0, 'taller': 0, 'virtual': 0, 'total': 0}
            secciones = {'aula': 0, 'laboratorio': 0, 'taller': 0, 'virtual': 0, 'total': 0}
            
            for ambiente in ['aula', 'laboratorio', 'taller', 'virtual']:
                datos_amb = datos_periodo[datos_periodo['TIPO_AMBIENTE'] == ambiente]
                horas_semanales[ambiente] = float(datos_amb['HORAS_TOTALES'].sum())
                secciones[ambiente] = int(datos_amb['SECCIONES'].sum())
            
            horas_semanales['total'] = sum([v for k, v in horas_semanales.items() if k != 'total'])
            secciones['total'] = sum([v for k, v in secciones.items() if k != 'total'])
            horas_semestre = {k: v * self.semanas for k, v in horas_semanales.items()}
            
            detalle_programas = {}
            for programa in self.config.obtener_programas():
                datos_prog = datos_periodo[datos_periodo['PROGRAMA'] == programa]
                if len(datos_prog) > 0:
                    est_prog = int(datos_prog['TOTAL_MATRICULADOS'].iloc[0])
                    horas_prog = {}
                    secc_prog = {}
                    for ambiente in ['aula', 'laboratorio', 'taller', 'virtual']:
                        datos_amb = datos_prog[datos_prog['TIPO_AMBIENTE'] == ambiente]
                        horas_prog[ambiente] = float(datos_amb['HORAS_TOTALES'].sum())
                        secc_prog[ambiente] = int(datos_amb['SECCIONES'].sum())
                    detalle_programas[programa] = {
                        'estudiantes': est_prog,
                        'horas_semanales': horas_prog,
                        'secciones': secc_prog
                    }
            
            resumen = {
                'periodo': periodo,
                'anio': anio,
                'ciclo': ciclo,
                'estudiantes': {'total': total_estudiantes, **est_por_programa},
                'horas_semanales': horas_semanales,
                'horas_semestre': horas_semestre,
                'secciones': secciones,
                'detalle_por_programa': detalle_programas
            }
            resumen_periodos.append(convertir_a_tipos_python(resumen))
        
        self.registro.info(f"  ✅ {len(resumen_periodos)} periodos analizados")
        return resumen_periodos
FIN

cat > src/analizadores/analizador_semestres.py << 'FIN'
"""Módulo Analizador de Semestres"""
import pandas as pd
from typing import Dict, List
from ..utilidades.registro import obtener_registrador
from ..utilidades.ayudantes import convertir_a_tipos_python

class AnalizadorSemestres:
    def __init__(self, gestor_config):
        self.config = gestor_config
        self.registro = obtener_registrador()
    
    def analizar(self, proyecciones_procesadas: Dict[str, pd.DataFrame], mallas: Dict[str, pd.DataFrame]) -> List[Dict]:
        self.registro.info("📊 Analizando consumo por semestre académico...")
        todos_datos = pd.concat(proyecciones_procesadas.values(), ignore_index=True)
        todas_mallas = pd.concat(mallas.values(), ignore_index=True)
        resumen_semestres = []
        
        for semestre in range(1, 11):
            datos_sem = todos_datos[todos_datos['SEMESTRE'] == semestre]
            malla_sem = todas_mallas[todas_mallas['SEMESTRE'] == semestre]
            if len(datos_sem) == 0:
                continue
            
            resumen = {
                'semestre': semestre,
                'cursos': len(malla_sem),
                'creditos_totales': int(malla_sem['CREDITOS'].sum()) if 'CREDITOS' in malla_sem.columns else 0,
                'horas_curso_semanales': int(malla_sem['TOTAL_HORAS_SEMANALES'].sum()),
                'estadisticas': {
                    'promedio_estudiantes': float(datos_sem['TOTAL_MATRICULADOS'].mean()),
                    'maximo_estudiantes': int(datos_sem['TOTAL_MATRICULADOS'].max()),
                    'minimo_estudiantes': int(datos_sem['TOTAL_MATRICULADOS'].min()),
                    'promedio_secciones': float(datos_sem['SECCIONES'].mean()),
                    'promedio_horas_semanales': float(datos_sem.groupby('PERIODO_STR')['HORAS_TOTALES'].sum().mean())
                },
                'distribucion_tipo_ambiente': {}
            }
            
            for ambiente in ['aula', 'laboratorio', 'taller', 'virtual']:
                datos_amb = datos_sem[datos_sem['TIPO_AMBIENTE'] == ambiente]
                if len(datos_amb) > 0:
                    horas_prom = datos_amb.groupby('PERIODO_STR')['HORAS_TOTALES'].sum().mean()
                    pct = (horas_prom / resumen['estadisticas']['promedio_horas_semanales'] * 100) if resumen['estadisticas']['promedio_horas_semanales'] > 0 else 0
                    resumen['distribucion_tipo_ambiente'][ambiente] = {
                        'horas_semanales': float(horas_prom),
                        'porcentaje': float(pct)
                    }
                else:
                    resumen['distribucion_tipo_ambiente'][ambiente] = {'horas_semanales': 0.0, 'porcentaje': 0.0}
            
            resumen_semestres.append(convertir_a_tipos_python(resumen))
        
        self.registro.info(f"  ✅ {len(resumen_semestres)} semestres analizados")
        return resumen_semestres
FIN

cat > src/analizadores/analizador_anios.py << 'FIN'
"""Módulo Analizador de Años"""
import pandas as pd
from typing import Dict, List
from ..utilidades.registro import obtener_registrador
from ..utilidades.ayudantes import convertir_a_tipos_python

class AnalizadorAnios:
    def __init__(self, gestor_config):
        self.config = gestor_config
        self.registro = obtener_registrador()
        self.semanas = gestor_config.obtener_semanas_semestre()
    
    def analizar(self, proyecciones_procesadas: Dict[str, pd.DataFrame]) -> List[Dict]:
        self.registro.info("📊 Analizando consumo por año...")
        todos_datos = pd.concat(proyecciones_procesadas.values(), ignore_index=True)
        anios = sorted(todos_datos['ANIO'].unique())
        resumen_anios = []
        
        for anio in anios:
            datos_anio = todos_datos[todos_datos['ANIO'] == anio]
            est_ciclo_i = datos_anio[datos_anio['CICLO'] == 'I']['TOTAL_MATRICULADOS'].max()
            est_ciclo_ii = datos_anio[datos_anio['CICLO'] == 'II']['TOTAL_MATRICULADOS'].max()
            total_est = max(est_ciclo_i if pd.notna(est_ciclo_i) else 0, est_ciclo_ii if pd.notna(est_ciclo_ii) else 0)
            
            horas_anuales = {}
            for ambiente in ['aula', 'laboratorio', 'taller', 'virtual']:
                datos_amb = datos_anio[datos_anio['TIPO_AMBIENTE'] == ambiente]
                horas_totales = datos_amb['HORAS_TOTALES'].sum() * self.semanas
                horas_anuales[ambiente] = float(horas_totales)
            
            horas_anuales['total'] = sum(horas_anuales.values())
            
            ciclo_i = datos_anio[datos_anio['CICLO'] == 'I']
            ciclo_ii = datos_anio[datos_anio['CICLO'] == 'II']
            prom_i = ciclo_i.groupby('PERIODO_STR')['HORAS_TOTALES'].sum().mean() if len(ciclo_i) > 0 else 0
            prom_ii = ciclo_ii.groupby('PERIODO_STR')['HORAS_TOTALES'].sum().mean() if len(ciclo_ii) > 0 else 0
            
            resumen = {
                'anio': int(anio),
                'total_estudiantes_anio': int(total_est),
                'horas_anuales': horas_anuales,
                'promedio_semanal': {
                    'ciclo_i': float(prom_i),
                    'ciclo_ii': float(prom_ii),
                    'promedio': float((prom_i + prom_ii) / 2)
                }
            }
            resumen_anios.append(convertir_a_tipos_python(resumen))
        
        self.registro.info(f"  ✅ {len(resumen_anios)} años analizados")
        return resumen_anios
FIN

# ============================================================================
# EXPORTADORES
# ============================================================================

cat > src/exportadores/exportador_json.py << 'FIN'
"""Módulo Exportador JSON"""
import json
from pathlib import Path
from typing import Dict, List, Any
from ..utilidades.registro import obtener_registrador
from ..utilidades.ayudantes import convertir_a_tipos_python

class ExportadorJSON:
    def __init__(self, gestor_config):
        self.config = gestor_config
        self.registro = obtener_registrador()
    
    def generar(self, resumen_periodos: List[Dict], resumen_semestres: List[Dict], resumen_anios: List[Dict]) -> Dict[str, Any]:
        self.registro.info("\n💾 Generando estructura JSON...")
        periodo_pico = max(resumen_periodos, key=lambda x: x['horas_semanales']['total'])
        
        resultado = {
            'metadatos': {
                **self.config.obtener_metadatos(),
                'periodo_proyeccion': f"{resumen_periodos[0]['periodo']} a {resumen_periodos[-1]['periodo']}",
                'parametros': self.config.obtener_parametros()
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
            'consumo_por_anio': resumen_anios
        }
        
        resultado = convertir_a_tipos_python(resultado)
        self.registro.info("  ✅ Estructura JSON generada")
        return resultado
    
    def guardar(self, datos: Dict[str, Any]) -> str:
        ruta_salida = self.config.obtener_salida_json()
        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        with open(ruta_salida, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=2, ensure_ascii=False)
        self.registro.info(f"  ✅ JSON guardado: {ruta_salida}")
        return ruta_salida
    
    def exportar(self, resumen_periodos: List[Dict], resumen_semestres: List[Dict], resumen_anios: List[Dict]) -> tuple:
        datos = self.generar(resumen_periodos, resumen_semestres, resumen_anios)
        ruta = self.guardar(datos)
        return datos, ruta
FIN

cat > src/exportadores/exportador_excel.py << 'FIN'
"""Módulo Exportador Excel"""
import pandas as pd
from pathlib import Path
from typing import Dict, List
from ..utilidades.registro import obtener_registrador

class ExportadorExcel:
    def __init__(self, gestor_config):
        self.config = gestor_config
        self.registro = obtener_registrador()
    
    def crear_hoja_resumen(self, datos_json: Dict) -> pd.DataFrame:
        resumen_data = [
            ['RESUMEN EJECUTIVO - CONSUMO DE HORAS-AULA', ''],
            ['', ''],
            ['Carrera:', datos_json['metadatos']['carrera']],
            ['Programas:', ', '.join(datos_json['metadatos']['programas'])],
            ['Periodo de Proyección:', datos_json['metadatos']['periodo_proyeccion']],
            ['', ''],
            ['PERIODO PICO', ''],
            ['Periodo:', datos_json['resumen_total']['periodo_pico']['periodo']],
            ['Horas Semanales:', f"{datos_json['resumen_total']['periodo_pico']['horas_semanales_totales']:.2f}"],
            ['Estudiantes:', datos_json['resumen_total']['periodo_pico']['estudiantes']],
        ]
        return pd.DataFrame(resumen_data, columns=['Concepto', 'Valor'])
    
    def crear_hoja_periodos(self, periodos: List[Dict]) -> pd.DataFrame:
        data = []
        for p in periodos:
            data.append({
                'Periodo': p['periodo'],
                'Año': p['anio'],
                'Ciclo': p['ciclo'],
                'Estudiantes': p['estudiantes']['total'],
                'Aula (hrs)': f"{p['horas_semanales']['aula']:.2f}",
                'Lab (hrs)': f"{p['horas_semanales']['laboratorio']:.2f}",
                'Taller (hrs)': f"{p['horas_semanales']['taller']:.2f}",
                'Virtual (hrs)': f"{p['horas_semanales']['virtual']:.2f}",
                'Total (hrs)': f"{p['horas_semanales']['total']:.2f}"
            })
        return pd.DataFrame(data)
    
    def exportar(self, datos_json: Dict) -> str:
        self.registro.info("\n💾 Generando archivo Excel...")
        ruta_salida = self.config.obtener_salida_excel()
        Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            self.crear_hoja_resumen(datos_json).to_excel(writer, sheet_name='Resumen', index=False)
            self.registro.info("  ✓ Hoja 'Resumen' creada")
            self.crear_hoja_periodos(datos_json['consumo_por_periodo']).to_excel(writer, sheet_name='Por Periodo', index=False)
            self.registro.info(f"  ✓ Hoja 'Por Periodo' creada")
        
        self.registro.info(f"  ✅ Excel guardado: {ruta_salida}")
        return ruta_salida
FIN

echo "✅ Todos los módulos creados exitosamente"
