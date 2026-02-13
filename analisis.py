import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)   
pd.set_option('display.width', None)         
pd.set_option('display.max_colwidth', None)

ruta_1 = r"D:\Analsis_coding\estimacion_infraestructura\Consumo_horas_educacion_secundaria\datos\Malla_Curricular_LLYA.xlsx"
ruta_2 = r"D:\Analsis_coding\estimacion_infraestructura\Consumo_horas_educacion_secundaria\datos\Proyeccion_MYC.xlsx"

df_1 = pd.read_excel(ruta_1)
df_2 = pd.read_excel(ruta_2)

dfs = [df_1, df_2]

cursos_lab = (
    pd.concat(dfs)
    .query('TIPO_AMBIENTE_PRACTICA == "Laboratorio de Computadoras"')
    ["CURSO"]
    .drop_duplicates()
    .reset_index(drop=True)
)

print(cursos_lab)