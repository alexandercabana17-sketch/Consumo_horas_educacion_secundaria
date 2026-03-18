"""
Script Principal - Análisis de Consumo de Horas-Aula
Carrera: Educación Secundaria

Menú de opciones:
  1. Análisis completo  →  Reporte de cursos + JSON + Excel de consumo
  2. Reporte de cursos  →  Solo muestra los cursos considerados tras equivalencias
  3. Generar Excel      →  Genera el Excel de consumo desde el JSON existente
  0. Salir
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from scripts.analizador_horas_aula  import AnalizadorHorasAula
from scripts.generador_excel        import GeneradorExcel
from scripts.generador_reporte_cursos import GeneradorReporteCursos


# ---------------------------------------------------------------------------
# Helpers de UI
# ---------------------------------------------------------------------------

def separador(char='=', n=80):
    print(char * n)


def mostrar_menu():
    print()
    separador()
    print("MENU PRINCIPAL - CONSUMO DE HORAS-AULA")
    separador()
    print("  1. Analisis completo   (reporte de cursos + JSON + Excel de consumo)")
    print("  2. Reporte de cursos   (verificar equivalencias y exclusiones)")
    print("  3. Generar Excel       (desde JSON existente, sin recalcular)")
    print("  0. Salir")
    separador('-')
    return input("Seleccione una opcion [0-3]: ").strip()


# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------

def opcion_analisis_completo(config_path='config.json'):
    """
    Opción 1: Análisis completo.
    Flujo: cargar datos → equivalencias → procesar → resúmenes → JSON → Excel cursos → Excel consumo.
    """
    separador()
    print("ANALISIS COMPLETO")
    separador()

    try:
        # Fase 1: análisis y JSON
        print("\n[FASE 1/3] Analisis de datos y generacion de JSON")
        separador('-')
        analizador = AnalizadorHorasAula(config_path)
        resultado_json = analizador.ejecutar()

        # Fase 2: reporte de cursos
        print("\n[FASE 2/3] Generacion del reporte de cursos")
        separador('-')
        reporte_path = analizador.config['output']['reporte_cursos']
        reporte = GeneradorReporteCursos(analizador, reporte_path)
        reporte.generar()

        # Fase 3: Excel de consumo
        print("\n[FASE 3/3] Generacion del Excel de consumo")
        separador('-')
        json_path  = analizador.config['output']['json']
        excel_path = analizador.config['output']['excel']
        generador  = GeneradorExcel(json_path, excel_path)
        generador.generar()

        # Resumen final
        print()
        separador()
        print("PROCESO COMPLETADO EXITOSAMENTE")
        separador()
        print("\nArchivos generados:")
        print(f"  1. JSON de consumo   : {json_path}")
        print(f"  2. Reporte de cursos : {reporte_path}")
        print(f"  3. Excel de consumo  : {excel_path}")

        pico = resultado_json['resumen_total']['periodo_pico']
        dist = resultado_json['resumen_total']['distribucion_pico']
        print(f"\nPeriodo pico: {pico['periodo']}")
        print(f"Horas semanales totales (pico): {pico['horas_semanales_totales']:.2f}")
        print(f"Estudiantes (pico): {pico['estudiantes']}")
        print("\nDistribucion en periodo pico:")
        for ambiente, horas in dist.items():
            if ambiente != 'total':
                print(f"  - {ambiente.capitalize()}: {horas:.2f} hrs/semana")
        separador()
        return True

    except Exception as e:
        separador()
        print("ERROR EN EL PROCESO")
        separador()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


def opcion_reporte_cursos(config_path='config.json'):
    """
    Opción 2: Solo generar el reporte de cursos.
    Flujo: cargar datos → identificar equivalencias → Excel de cursos.
    No procesa periodos ni genera JSON.
    """
    separador()
    print("REPORTE DE CURSOS (EQUIVALENCIAS Y EXCLUSIONES)")
    separador()

    try:
        analizador = AnalizadorHorasAula(config_path)

        print("\nCargando datos e identificando equivalencias...")
        separador('-')
        analizador.cargar_datos()
        analizador.identificar_cursos_compartidos()
        analizador.identificar_cursos_a_eliminar()

        reporte_path = analizador.config['output']['reporte_cursos']
        reporte = GeneradorReporteCursos(analizador, reporte_path)
        reporte.generar()
        return True

    except Exception as e:
        separador()
        print("ERROR GENERANDO REPORTE")
        separador()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


def opcion_generar_excel(config_path='config.json'):
    """
    Opción 3: Generar Excel de consumo desde JSON existente.
    Útil para regenerar el Excel sin volver a calcular todo.
    """
    separador()
    print("GENERAR EXCEL DE CONSUMO (DESDE JSON EXISTENTE)")
    separador()

    try:
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        json_path  = config['output']['json']
        excel_path = config['output']['excel']

        json_file = Path(json_path)
        if not json_file.exists():
            print(f"\nERROR: No se encontro el JSON en '{json_path}'.")
            print("Ejecute primero el analisis completo (opcion 1).")
            return False

        generador = GeneradorExcel(json_path, excel_path)
        generador.generar()

        print(f"\nExcel generado: {excel_path}")
        return True

    except Exception as e:
        separador()
        print("ERROR GENERANDO EXCEL")
        separador()
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main():
    CONFIG = 'config.json'

    while True:
        opcion = mostrar_menu()

        if opcion == '1':
            opcion_analisis_completo(CONFIG)
        elif opcion == '2':
            opcion_reporte_cursos(CONFIG)
        elif opcion == '3':
            opcion_generar_excel(CONFIG)
        elif opcion == '0':
            print("\nSaliendo...\n")
            break
        else:
            print("\nOpcion no valida. Ingrese 0, 1, 2 o 3.")

        input("\nPresione Enter para volver al menu...")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success is not False else 1)
