1. **Adquisición:** lee el CSV con `read_csv` y el Excel con `read_excel` (motor `openpyxl`).
2. **Transformación:**
   - `fecha` pasa a `datetime` (los valores inválidos se convierten en nulos con `errors="coerce"`).
   - `id_producto` y `cantidad` se convierten a numérico, y la llave `id_producto` queda con el mismo tipo en ambos archivos (con tipos distintos el merge falla).
   - Nulos: se eliminan las ventas sin producto, sin cantidad o sin fecha válida. No se imputan porque sin esos datos no se puede valorizar la venta.
   - `merge` de transacciones con productos por `id_producto` (`inner`, validado como muchos a uno). Las ventas de productos que no existen en el catálogo se descartan.
3. **Normalización:** nueva columna `total_venta = cantidad * precio_unitario`, con control de calidad que verifica que no haya nulos en los campos críticos.
4. **Exportación:** guarda `output/ventas_consolidadas.parquet`.

## Resultado esperado con los datos de ejemplo

- 200 transacciones leídas, 7 eliminadas por nulos o fechas inválidas.
- 2 ventas descartadas en el merge (producto 999, inexistente en el catálogo).
- **191 filas** en el dataset final, con 7 columnas: `id_transaccion`, `fecha`, `id_producto`, `nombre_producto`, `cantidad`, `precio_unitario`, `total_venta`.

## Errores comunes que evita

- Leer Excel sin tener `openpyxl` instalado.
- Hacer el `merge` con la llave en tipos distintos (por ejemplo texto y entero).
- Dejar fechas como texto en lugar de `datetime`.