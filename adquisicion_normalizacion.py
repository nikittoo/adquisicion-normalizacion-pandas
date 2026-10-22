"""
Pre-entrega: Adquisición y Normalización con Pandas.

Pipeline:
  1. Adquisición: leer transacciones (CSV) y maestro de productos (Excel).
  2. Transformación: corregir tipos, manejar nulos y hacer el merge por id_producto.
  3. Normalización: crear la columna calculada total_venta.
  4. Exportación: guardar el dataset final en formato Parquet.
"""

import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV = os.path.join(BASE_DIR, "data", "transacciones.csv")
RUTA_EXCEL = os.path.join(BASE_DIR, "data", "productos.xlsx")
RUTA_SALIDA = os.path.join(BASE_DIR, "output", "ventas_consolidadas.parquet")

# ---------------------------------------------------------------------------
# 1. Adquisición
# ---------------------------------------------------------------------------
transacciones = pd.read_csv(RUTA_CSV)
productos = pd.read_excel(RUTA_EXCEL, engine="openpyxl")  # requiere openpyxl

print("=== 1. Adquisición ===")
print(f"Transacciones (CSV):  {transacciones.shape[0]} filas, {transacciones.shape[1]} columnas")
print(f"Productos (Excel):    {productos.shape[0]} filas, {productos.shape[1]} columnas")
print("\nNulos en transacciones:")
print(transacciones.isna().sum())

# ---------------------------------------------------------------------------
# 2. Transformación
# ---------------------------------------------------------------------------
# 2.a Tipos de datos
# - fecha: texto -> datetime (los valores inválidos pasan a NaT con errors="coerce")
# - id_producto y cantidad: a numérico, para que ambos archivos tengan el mismo tipo
transacciones["fecha"] = pd.to_datetime(transacciones["fecha"], errors="coerce")
transacciones["id_producto"] = pd.to_numeric(transacciones["id_producto"], errors="coerce")
transacciones["cantidad"] = pd.to_numeric(transacciones["cantidad"], errors="coerce")

# Forzamos el MISMO tipo en la llave del Excel: si un ID llegara como texto en un archivo
# y como número en el otro, el merge falla (ValueError) o no encuentra coincidencias.
productos["id_producto"] = pd.to_numeric(productos["id_producto"], errors="coerce")

# 2.b Valores nulos
# Una venta sin producto, sin cantidad o sin fecha válida no se puede analizar ni
# valorizar (no se puede calcular el total), por lo que se eliminan en lugar de imputarse.
columnas_criticas = ["id_producto", "cantidad", "fecha"]
antes = len(transacciones)
transacciones = transacciones.dropna(subset=columnas_criticas)
print(f"\n=== 2. Transformación ===")
print(f"Filas eliminadas por nulos en {columnas_criticas}: {antes - len(transacciones)}")

# Ya sin nulos, el ID puede pasar a entero (con nulos no se podía)
transacciones["id_producto"] = transacciones["id_producto"].astype(int)
transacciones["cantidad"] = transacciones["cantidad"].astype(int)
productos["id_producto"] = productos["id_producto"].astype(int)

print("\nTipos finales de transacciones:")
print(transacciones.dtypes)

# 2.c Merge por id_producto
# how="inner": se conservan solo las ventas cuyo producto existe en el catálogo.
# validate="m:1": muchas transacciones por producto, un solo producto por ID.
filas_antes_merge = len(transacciones)
ventas = transacciones.merge(productos, on="id_producto", how="inner", validate="m:1")
print(f"\nMerge: {filas_antes_merge} transacciones -> {len(ventas)} con producto en el catálogo "
      f"({filas_antes_merge - len(ventas)} sin coincidencia descartadas)")

# ---------------------------------------------------------------------------
# 3. Normalización: columna calculada
# ---------------------------------------------------------------------------
ventas["total_venta"] = (ventas["cantidad"] * ventas["precio_unitario"]).round(2)

# Control de calidad: ningún nulo en los campos críticos del dataset final
campos_finales = ["id_producto", "nombre_producto", "cantidad", "fecha",
                  "precio_unitario", "total_venta"]
assert ventas[campos_finales].notna().all().all(), "Quedaron nulos en campos críticos"
print("\n=== 3. Normalización ===")
print("Control de calidad OK: sin nulos en campos críticos.")

# ---------------------------------------------------------------------------
# 4. Exportación a Parquet
# ---------------------------------------------------------------------------
ventas = ventas[["id_transaccion", "fecha", "id_producto", "nombre_producto",
                 "cantidad", "precio_unitario", "total_venta"]]
os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
ventas.to_parquet(RUTA_SALIDA, index=False)  # requiere pyarrow

# Verificación: releer el archivo exportado
verificacion = pd.read_parquet(RUTA_SALIDA)
print("\n=== 4. Exportación ===")
print(f"Archivo generado: {RUTA_SALIDA}")
print(f"Filas: {len(verificacion)} | Columnas: {list(verificacion.columns)}")
print("\nPrimeras filas:")
print(verificacion.head())
print(f"\nVenta total acumulada: {verificacion['total_venta'].sum():,.2f}")