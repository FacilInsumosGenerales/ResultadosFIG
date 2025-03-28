from conexion import conectarseABaseDeDatos
import pandas as pd

# anadir nombre de empresa y ruc
# añadir saldo
def conseguirDataAdministracion(start_date, end_date):
    query = """
        SELECT 
            mb.Concepto Concepto_pago,
            mb.Fecha Fecha_pago,
            mb.Valor Valor_pago,
            mb.Moneda Moneda_pago,
            mb.No_Operacion_Bancaria,
            mb.Ediciones Ediciones_pago,
            cp.Proveedor,
            cp.OC_cliente,
            cp.OC_proveedor,
            cp.Descripcion Descripcion_factura,
            cp.Numero_de_documento,
            cp.Fecha_Emision,
            cp.Fecha_Vencimiento,
            cp.Fecha_de_Envio,
            cp.Valor_sin_IGV,
            cp.IGV
        FROM movimientos_bancarios mb
        LEFT JOIN pagos_relacionados pr ON mb.TRAZA = pr.Movimiento
        LEFT JOIN comprobantes_de_pago cp ON cp.TRAZA = pr.Comprobante
        WHERE mb.Fecha BETWEEN %s AND %s
        GROUP BY mb.TRAZA;
    """

    connection = conectarseABaseDeDatos()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchall()
    connection.close()
    return pd.DataFrame(result)


###Clientes
# saldo = facturas - abonos
# fecha de vencimiento de facturas
# fecha de emision de factura
# fecha de envio de factura
# nombre del cliente
# numero de oc cliente

###