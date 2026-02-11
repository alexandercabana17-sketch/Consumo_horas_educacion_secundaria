# 📦 SISTEMA DE ANÁLISIS DE HORAS-AULA v2.0
## CON OPTIMIZACIÓN DE EQUIVALENCIAS

---

## 🎯 NOVEDADES DE LA VERSIÓN 2.0

### ✨ **NUEVAS CARACTERÍSTICAS:**

1. **Optimización por Equivalencias**
   - Identifica cursos compartidos entre LLYA y MYC
   - Elimina cursos que van a otras carreras
   - Combina estudiantes de cursos equivalentes

2. **Reducción Significativa**
   - 53.4% menos horas necesarias
   - 50% menos aulas requeridas
   - 43% menos laboratorios requeridos

3. **Procesamiento Inteligente**
   - 6 cursos compartidos detectados automáticamente
   - 74 cursos eliminados (van a otras carreras)
   - 45 cursos exclusivos mantenidos

---

## 📊 RESULTADOS COMPARATIVOS

### **ANTES (v1.0 - Sin equivalencias):**
```
Periodo pico 2031-02:
- Horas totales: 592h/semana
- Aulas: ~6 necesarias
- Laboratorios: ~7 necesarios
```

### **AHORA (v2.0 - Con equivalencias):**
```
Periodo pico 2031-02:
- Horas totales: 276h/semana ✅ (53% reducción)
- Aulas: ~3 necesarias ✅ (50% reducción)
- Laboratorios: ~4 necesarios ✅ (43% reducción)
```

---

## 📁 ARCHIVOS INCLUIDOS

```
proyecto_horas_aula_modular/
│
├── config.json                    ← ACTUALIZADO con equivalencias
├── main.py                        ← Script principal
├── requirements.txt               ← Dependencias
│
├── datos/                         ← Datos de entrada
│   ├── Malla_Curricular_LLYA.xlsx
│   ├── Malla_Curricular_MYC.xlsx
│   ├── Proyeccion_LLYA.xlsx
│   ├── Proyeccion_MYC.xlsx
│   ├── Equivalencias_LLYA.xlsx    ← NUEVO
│   └── Equivalencias_MYC.xlsx     ← NUEVO
│
├── scripts/
│   ├── analizador_horas_aula.py   ← MODIFICADO con lógica de equivalencias
│   └── generador_excel.py
│
├── salida/                        ← Resultados generados
│   ├── json/
│   ├── excel/
│   └── logs/
│
└── src/                           ← Módulos adicionales
    ├── configuracion/
    ├── datos/
    ├── procesadores/
    ├── analizadores/
    ├── exportadores/
    └── utilidades/
```

---

## 🚀 INSTALACIÓN Y USO

### **Paso 1: Descomprimir**

**En Windows:**
```
Clic derecho → Extraer todo
```

**En Linux/Mac:**
```bash
unzip proyecto_horas_aula_modular_v2_con_equivalencias.zip
# o
tar -xzf proyecto_horas_aula_modular_v2_con_equivalencias.tar.gz
```

### **Paso 2: Instalar dependencias**

```bash
cd proyecto_horas_aula_modular
pip install -r requirements.txt
```

### **Paso 3: Ejecutar**

```bash
python main.py
```

---

## 🔧 CONFIGURACIÓN

### **Modificar capacidades de ambientes:**

Editar `config.json`:

```json
{
  "parametros": {
    "tamano_seccion_aula": 30,         ← Cambiar aquí
    "tamano_seccion_laboratorio": 20,  ← Cambiar aquí
    "tamano_seccion_taller": 25,       ← Cambiar aquí
    "semanas_por_semestre": 16
  }
}
```

### **Actualizar datos:**

1. Reemplazar archivos en `datos/`
2. Ejecutar `python main.py`
3. Resultados en `salida/`

---

## 📊 ARCHIVOS DE SALIDA

### **1. JSON Completo**
`salida/json/consumo_horas_educacion_secundaria.json`

- Metadata del análisis
- Resumen total con periodo pico
- Consumo por periodo (20 periodos)
- Consumo por semestre académico (10 semestres)
- Consumo por año (10 años)

### **2. Excel de Verificación**
`salida/excel/consumo_horas_educacion_secundaria.xlsx`

**5 hojas:**
1. Resumen Ejecutivo
2. Consumo por Periodo
3. Consumo por Semestre
4. Consumo por Año
5. Tabla Pivote

---

## 🔍 LÓGICA DE EQUIVALENCIAS

### **Cursos Compartidos (LLYA ↔ MYC):**

```
Psicología del Desarrollo
Geometría Euclidiana
Tutoría
Gestión de Instituciones Educativas
Práctica de Ayudantía
Quechua
```

**Procesamiento:**
- Estudiantes de LLYA + MYC combinados
- 1 sola sección calculada
- Contado una sola vez

### **Cursos Eliminados (a otras carreras):**

**74 cursos totales:**
- 36 de LLYA → van a Educación Inicial
- 38 de MYC → van a Educación Inicial

**Procesamiento:**
- No contados en el análisis
- Estudiantes van a otras carreras
- Ya están en otros análisis

### **Cursos Exclusivos:**

**45 cursos totales:**
- 23 de LLYA (solo LLYA)
- 22 de MYC (solo MYC)

**Procesamiento:**
- Contados normalmente
- Sin cambios

---

## 📈 EJEMPLO DE EJECUCIÓN

```bash
$ python main.py

================================================================================
ANÁLISIS DE CONSUMO DE HORAS-AULA
Carrera: Educación Secundaria (LLYA + MYC)
================================================================================

🚀 Iniciando análisis completo con equivalencias...

📂 Cargando datos...
  ✓ Malla LLYA: 65 cursos
  ✓ Equivalencias LLYA: 65 registros
  ✓ Malla MYC: 66 cursos
  ✓ Equivalencias MYC: 66 registros
  ✅ Datos cargados exitosamente

🔍 Identificando cursos compartidos entre LLYA y MYC...
  ✅ 6 cursos compartidos identificados

🗑️ Identificando cursos que van a otras carreras...
  ✅ Total de cursos a eliminar: 74

🔄 Procesando programa: LLYA
  🗑️ Eliminados 36 cursos que van a otras carreras
  ✅ LLYA procesado: 1060 registros

🔄 Procesando programa: MYC
  🗑️ Eliminados 38 cursos que van a otras carreras
  ✅ MYC procesado: 1040 registros

🤝 Procesando cursos compartidos...
  ✅ 6 cursos compartidos procesados

📊 Generando resumen por periodo...
  ✅ 20 periodos procesados

💾 Generando archivo JSON...
  ✅ JSON guardado

================================================================================
✅ ANÁLISIS COMPLETADO EXITOSAMENTE (CON EQUIVALENCIAS)
================================================================================

📊 Optimización aplicada:
  - Cursos compartidos LLYA↔MYC: 6
  - Cursos eliminados (van a otras carreras): 74

Periodo pico: 2031-02
Horas semanales totales (pico): 276.00
```

---

## 🆚 DIFERENCIAS CON VERSIÓN 1.0

| Característica | v1.0 | v2.0 |
|----------------|------|------|
| **Archivos de equivalencias** | ❌ | ✅ |
| **Cursos compartidos** | ❌ | ✅ 6 cursos |
| **Filtro por equivalencias** | ❌ | ✅ 74 cursos |
| **Optimización de secciones** | ❌ | ✅ |
| **Horas periodo pico** | 592h | 276h |
| **Reducción** | - | 53.4% |

---

## 📝 NOTAS IMPORTANTES

### **Equivalencias:**

1. Los archivos `Equivalencias_LLYA.xlsx` y `Equivalencias_MYC.xlsx` son **obligatorios**
2. Si cambias las equivalencias, vuelve a ejecutar el análisis
3. El sistema verifica nombres de cursos para validar equivalencias

### **Archivos de backup:**

- `analizador_horas_aula_backup.py` contiene la versión sin equivalencias
- Útil para comparar resultados o recuperar funcionalidad

### **Actualización de datos:**

Si actualizas proyecciones o mallas:
1. Reemplaza archivos en `datos/`
2. Verifica que equivalencias sigan vigentes
3. Ejecuta `python main.py`

---

## 🐛 RESOLUCIÓN DE PROBLEMAS

### **Error: "Archivo de equivalencias no encontrado"**
```
Solución: Verifica que Equivalencias_LLYA.xlsx y 
         Equivalencias_MYC.xlsx estén en la carpeta datos/
```

### **Error: "No module named pandas"**
```
Solución: pip install -r requirements.txt
```

### **Resultados diferentes a v1.0**
```
Esto es CORRECTO. La v2.0 optimiza con equivalencias.
Para resultados sin optimización, usa v1.0 o el backup.
```

---

## 📞 SOPORTE

### **Documentación adicional:**
- `RESULTADOS_CON_EQUIVALENCIAS.md` - Análisis detallado
- `EXPLICACION_SECCIONES.md` - Concepto de secciones
- `FLUJO_DE_TRABAJO_COMPLETO.md` - Flujo del sistema

### **Archivos útiles:**
- `RESUMEN_OPERACIONES_DATOS.md` - Operaciones realizadas
- `PLAN_MODIFICACIONES_EQUIVALENCIAS.md` - Cambios implementados

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de usar, verifica:

- [ ] Python 3.7+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] 6 archivos Excel en `datos/`:
  - [ ] Malla_Curricular_LLYA.xlsx
  - [ ] Malla_Curricular_MYC.xlsx
  - [ ] Proyeccion_LLYA.xlsx
  - [ ] Proyeccion_MYC.xlsx
  - [ ] Equivalencias_LLYA.xlsx ← NUEVO
  - [ ] Equivalencias_MYC.xlsx ← NUEVO
- [ ] Configuración revisada en `config.json`
- [ ] Carpetas de salida creadas (se crean automáticamente)

---

## 🎯 CASOS DE USO

### **Planificación de infraestructura:**
Usar hoja "Consumo por Periodo" para ver cuándo construir

### **Presupuesto:**
Usar hoja "Consumo por Año" para proyectar gastos anuales

### **Análisis académico:**
Usar hoja "Consumo por Semestre" para ver carga por nivel

### **Vista rápida:**
Usar hoja "Tabla Pivote" para visualizaciones

---

## 📊 ESTADÍSTICAS DEL PROYECTO

- **Archivos de código:** 15+
- **Líneas de código:** ~2000
- **Tiempo de ejecución:** < 5 segundos
- **Periodos analizados:** 20 (2027-2036)
- **Semestres académicos:** 10
- **Años proyectados:** 10
- **Optimización lograda:** 53.4%

---

## 🏆 CARACTERÍSTICAS DESTACADAS

### **Automatización completa:**
- Lectura automática de Excel
- Cálculos automáticos
- Generación automática de reportes

### **Validación robusta:**
- Verifica nombres de cursos equivalentes
- Alerta sobre inconsistencias
- Logs detallados del proceso

### **Escalabilidad:**
- Fácil agregar más programas
- Modificable vía configuración
- Extensible con nuevos módulos

### **Transparencia:**
- Cada cálculo documentado
- Origen de datos trazable
- Proceso auditabl

e

---

## 📅 HISTORIAL DE VERSIONES

### **v2.0 (Actual) - Con Equivalencias**
- ✅ Soporte para equivalencias
- ✅ Optimización de cursos compartidos
- ✅ Filtrado de cursos a otras carreras
- ✅ Reducción de 53.4% en horas

### **v1.0 - Base**
- ✅ Análisis básico sin equivalencias
- ✅ Cálculo de secciones
- ✅ Proyección a 10 años
- ✅ Generación JSON y Excel

---

## 🎉 ¡LISTO PARA USAR!

El sistema está completamente funcional y probado.

**Ejecuta:** `python main.py`

**Resultados en:** `salida/json/` y `salida/excel/`

---

**Desarrollado para:** Análisis de Infraestructura Educativa
**Carrera:** Educación Secundaria (LLYA + MYC)
**Versión:** 2.0 - Con Optimización de Equivalencias
**Fecha:** Febrero 2025
