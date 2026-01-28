import sys
from pathlib import Path

# Agregamos directorio de scripts al path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from scripts.analizador_horas_aula import AnalizadorHorasAula
from scripts.generador_excel import GeneradorExcel

def main():
    """Función principal que ejecuta todo el proceso."""
    
    print("ANÁLISIS DE CONSUMO DE HORAS-AULA")
    print("Carrera: Educación Secundaria (LLYA + MYC)")
    
    try:
        # 1. Ejecutar análisis y generar JSON
        print("\n[FASE 1] Análisis de datos y generación de JSON")
        
        analizador = AnalizadorHorasAula('config.json')
        resultado_json = analizador.ejecutar()
        
        # 2. Generar Excel de verificación
        print("\n[FASE 2] Generación de Excel de verificación")
        
        json_path = analizador.config['output']['json']
        excel_path = analizador.config['output']['excel']
        
        generador = GeneradorExcel(json_path, excel_path)
        generador.generar()
        
        # 3. Resumen final        
        print("\n Archivos generados:")
        print(f"  1. JSON: {json_path}")
        print(f"  2. Excel: {excel_path}")
        
        print("\n Resumen de Resultados:")
        print(f"  • Periodo pico: {resultado_json['resumen_total']['periodo_pico']['periodo']}")
        print(f"  • Horas semanales (pico): {resultado_json['resumen_total']['periodo_pico']['horas_semanales_totales']:.2f}")
        print(f"  • Estudiantes (pico): {resultado_json['resumen_total']['periodo_pico']['estudiantes']}")
        
        print("\n  Distribución en periodo pico:")
        dist = resultado_json['resumen_total']['distribucion_pico']
        print(f"    - Aula: {dist['aula']:.2f} hrs/semana ({(dist['aula']/dist['total']*100):.1f}%)")
        print(f"    - Laboratorio: {dist['laboratorio']:.2f} hrs/semana ({(dist['laboratorio']/dist['total']*100):.1f}%)")
        print(f"    - Taller: {dist['taller']:.2f} hrs/semana ({(dist['taller']/dist['total']*100):.1f}%)")
        print(f"    - Virtual: {dist['virtual']:.2f} hrs/semana ({(dist['virtual']/dist['total']*100):.1f}%)")
        
        print(" Los archivos están listos para ser utilizados")
        
        return True
        
    except Exception as e:        
        print(" ERROR EN EL PROCESO")
        print(f"\nError: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
