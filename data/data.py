from conexion import conectarseABaseDeDatos
import pandas as pd


def conseguirData(start_date, end_date):
    query = """
        SELECT * FROM comprobantes_de_pago
        WHERE Fecha_Emision BETWEEN %s AND %s;
    """
    connection = conectarseABaseDeDatos()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchall()
    connection.close()
    return pd.DataFrame(result)


# ventas totales
# - todo lo facturado sin igv

# total de compras
# - facturas de proveedores sin igv

# resultado de ventas
# - ventas - compras


# gm
# resultados de ventas / ventas

# gastos de operaciones
# - facturas logistica + facturas tipo v

# gastos rrhh
# - gastos de equipo

# resultados totales
# - resultado de ventas - gastos de operacioenes - gastos de rrhh

# gm total
# - resultados totales / ventas totales