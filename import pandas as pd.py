import pandas as pd
import time

print("Leyendo el Excel (esto puede tardar un par de minutos, es normal SOLO esta vez)...")
inicio = time.time()

df = pd.read_excel("Gastos Municipales Definitivo.xlsx")

print(f"Excel leído en {time.time() - inicio:.1f} segundos.")
print(f"Filas: {df.shape[0]:,} | Columnas: {df.shape[1]}")

df.to_parquet("gastos_municipales.parquet", index=False)

print("✅ Listo: se creó 'gastos_municipales.parquet'")
print("Ahora usa ese archivo en tu app de Streamlit (se carga en segundos, no minutos).")