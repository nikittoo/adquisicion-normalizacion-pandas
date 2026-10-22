import os # era la libreria que me permite interactuar entre archivos y directorios de mi pc

import numpy as np
import pandas as pd

np.random.seed(42) # uso la misma semilla para que siempre me de igual, ACORDARSE: sin esta seed daria siempre resultados diferentes

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # BASE_DIR guarda la carpeta donde vive el el proyecto
DATA_DIR = os.path.join(BASE_DIR, "data") # aca me crea en la ruta donde guardamos antes el directorio, creo data y guardo esa ruta en DATA_DIR
#NO USAR DATA_DIR = BASE_DIR + "/data" puede dar errores

os.makedirs(DATA_DIR, exist_ok=True) #crea la carpeta data una vez si es que no existe

#generamos la tabla
productos = pd.DataFrame({
    "id_producto": [101, 102, 103, 104, 105, 106, 107, 108],
    "nombre_producto": [ "Sensor de Humedad IoT", "Placa Arduino Uno", "Cable USB-C", "Teclado Mecánico", "Mouse Inalámbrico", "Monitor 24 pulgadas", "Webcam HD", "Auriculares Bluetooth"],
    "precio_unitario": [25.50, 18.90, 6.75, 54.00, 22.30, 189.99, 35.40, 47.80]})
productos.to_excel(os.path.join(DATA_DIR, "productos.xlsx"), index=False) # aca empieza la magia y me crea la tabla en un archivo y los guarda donde dice

n = 200
ids_validos = [101, 102, 103, 104, 105, 106, 107, 108]

transacciones = pd.DataFrame({
    "id_transaccion": range(1, n + 1),
    "id_producto": np.random.choice(ids_validos, size=n),
    "cantidad": np.random.randint(1, 11, size=n).astype(float),
    "fecha": pd.to_datetime("2026-01-01") + pd.to_timedelta(np.random.randint(0, 270, size=n), unit="D"),
})
transacciones["fecha"] = transacciones["fecha"].dt.strftime("%Y-%m-%d")

transacciones.loc[[5, 40, 120], "cantidad"] = np.nan             # cantidad vacía
transacciones.loc[[15, 77], "fecha"] = np.nan                    # fecha vacía
transacciones.loc[[60], "fecha"] = "fecha-invalida"              # fecha mal escrita
transacciones.loc[[90], "id_producto"] = np.nan                  # producto sin ID
transacciones.loc[[130, 131], "id_producto"] = 999               # producto que no existe en el catálogo

transacciones.to_csv(os.path.join(DATA_DIR, "transacciones.csv"), index=False)

print("Archivos generados en la carpeta data/:")
print(" - transacciones.csv:", len(transacciones), "filas")
print(" - productos.xlsx:", len(productos), "filas")