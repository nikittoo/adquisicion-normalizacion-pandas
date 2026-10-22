import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV = os.path.join(BASE_DIR, "data", "transacciones.csv")
RUTA_EXCEL = os.path.join(BASE_DIR, "data", "productos.xlsx")

RUTA_SALIDA = os.path.join(BASE_DIR, "output", "ventas_consolidadas.parquet") # salida en formato paquet

transacciones = pd.read_csv(RUTA_CSV)
productos = pd.read_excel(RUTA_EXCEL, engine="openpyxl") 

print("=== 1. Adquisición ===")
print(f"Transacciones (CSV):  {transacciones.shape[0]} filas, {transacciones.shape[1]} columnas")
print(f"Productos (Excel):    {productos.shape[0]} filas, {productos.shape[1]} columnas")
print("\nNulos en transacciones:")
print(transacciones.isna().sum())

transacciones["fecha"] = pd.to_datetime(transacciones["fecha"], errors="coerce")
transacciones["id_producto"] = pd.to_numeric(transacciones["id_producto"], errors="coerce")
transacciones["cantidad"] = pd.to_numeric(transacciones["cantidad"], errors="coerce")

productos["id_producto"] = pd.to_numeric(productos["id_producto"], errors="coerce")

columnas_criticas = ["id_producto", "cantidad", "fecha"]
antes = len(transacciones)
transacciones = transacciones.dropna(subset=columnas_criticas)
print(f"\n=== 2. Transformación ===")
print(f"Filas eliminadas por nulos en {columnas_criticas}: {antes - len(transacciones)}")

transacciones["id_producto"] = transacciones["id_producto"].astype(int)
transacciones["cantidad"] = transacciones["cantidad"].astype(int)
productos["id_producto"] = productos["id_producto"].astype(int)

print("\nTipos finales de transacciones:")
print(transacciones.dtypes)

filas_antes_merge = len(transacciones)
ventas = transacciones.merge(productos, on="id_producto", how="inner", validate="m:1")
print(f"\nMerge: {filas_antes_merge} transacciones -> {len(ventas)} con producto en el catálogo {filas_antes_merge - len(ventas)} sin coincidencia descartadas)")

ventas["total_venta"] = (ventas["cantidad"] * ventas["precio_unitario"]).round(2)

campos_finales = ["id_producto", "nombre_producto", "cantidad", "fecha", "precio_unitario", "total_venta"]
assert ventas[campos_finales].notna().all().all(), "Quedaron nulos en campos críticos"
print("\n=== 3. Normalización ===")
print("Control de calidad OK: sin nulos en campos críticos.")

ventas = ventas[["id_transaccion", "fecha", "id_producto", "nombre_producto", "cantidad", "precio_unitario", "total_venta"]]
os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
ventas.to_parquet(RUTA_SALIDA, index=False)  

verificacion = pd.read_parquet(RUTA_SALIDA)
print("\n=== 4. Exportación ===")
print(f"Archivo generado: {RUTA_SALIDA}")
print(f"Filas: {len(verificacion)} | Columnas: {list(verificacion.columns)}")
print("\nPrimeras filas:")
print(verificacion.head())
print(f"\nVenta total acumulada: {verificacion['total_venta'].sum():,.2f}")