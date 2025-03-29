from conexion import conectarseABaseDeDatos
import pandas as pd


def conseguirDataAdministracion(start_date, end_date):
    connection = conectarseABaseDeDatos()
    cursor = connection.cursor(dictionary=True)


    dataProveedores = conseguirControlProveedores(start_date, end_date, cursor)
    dataClientes = conseguirControlClientes(start_date, end_date, cursor)
    dataGuias = conseguirControlGuias(start_date, end_date, cursor)

    cursor.close()
    connection.close()

    return {
        "Proveedores": dataProveedores,
        "Clientes": dataClientes,
        "Guias": dataGuias
    }



# anadir nombre de empresa y ruc
def conseguirControlProveedores(start_date, end_date,cursor):
    query = """
        SELECT 
            mb.Concepto Concepto_pago,
            mb.Fecha Fecha_pago,
            mb.Valor Valor_pago,
            mb.Moneda Moneda_pago,
            mb.No_Operacion_Bancaria,
            mb.Ediciones Ediciones_pago,
            oc.No_Orden_de_Compra OC_proveedor,
            oc.Fecha_actualizacion Fecha_OC_proveedor,
            e.Nombre Nombre_proveedor,
            e.RUC,
            cp.TRAZA TRAZA_factura,
            cp.Numero_de_documento,
            cp.Fecha_Emision,
            cp.Fecha_Vencimiento,
            cp.Fecha_de_Envio,
            cp.Moneda Moneda_factura,
            cp.Valor_sin_IGV,
            cp.IGV

        FROM movimientos_bancarios mb
        LEFT JOIN pagos_relacionados pr ON mb.TRAZA = pr.Movimiento
        LEFT JOIN comprobantes_de_pago cp ON cp.TRAZA = pr.Comprobante
        LEFT JOIN empresas e ON e.TRAZA = cp.Proveedor 
        INNER JOIN datos_generales_orden_compra_a_proveedores oc ON oc.TRAZA = cp.OC_proveedor 
        WHERE mb.Fecha BETWEEN %s AND %s
        GROUP BY mb.TRAZA;
    """

    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchall()
    
    dataCompleta = conseguirSaldo(result)
    return pd.DataFrame(dataCompleta)


def conseguirSaldo(data):
    df = pd.DataFrame(data)

    # Sumar valor_pago agrupado por TRAZA_factura
    pagos_agrupados = df.groupby("TRAZA_factura")["Valor_pago"].sum().reset_index()
    pagos_agrupados.rename(columns={"Valor_pago": "Suma_valor_pago"}, inplace=True)

    # Combinar ambos DataFrames en uno solo
    df_final = pd.merge(df, pagos_agrupados, on="TRAZA_factura", how="left")

    # Calcular la columna "Saldo" como Valor_sin_IGV + IGV - suma de valor_pago
    df_final["Saldo"] = df_final["Valor_sin_IGV"] + df_final["IGV"] - df_final["Suma_valor_pago"]

    # Mostrar el resultado final
    return df_final


###Clientes
def conseguirControlClientes(start_date, end_date,cursor):
    query = """
        SELECT 
            oc.Numero_OC_Cliente OC_cliente,
            req.Cod_Req,
            e.Nombre Nombre_cliente,
            e.RUC,
            oc.Fecha_Emision Fecha_OC_Cliente,
            cot.Moneda Moneda_cotizacion,
            oc.Valor_sin_IGV Valor_sin_IGV_OC,
            oc.IGV IGV_OC,
            cp.TRAZA TRAZA_factura,
            cp.Numero_de_documento,
            cp.Fecha_Emision,
            cp.Fecha_Vencimiento,
            cp.Fecha_de_Envio,
            cp.Moneda Moneda_factura,
            cp.Valor_sin_IGV,
            cp.IGV,
            mb.Concepto Concepto_pago,
            mb.Fecha Fecha_pago,
            mb.Valor Valor_pago,
            mb.Moneda Moneda_pago,
            mb.No_Operacion_Bancaria
            

        FROM datos_generales_ocs_clientes oc
        LEFT JOIN comprobantes_de_pago cp ON oc.TRAZA = cp.OC_cliente
        LEFT JOIN pagos_relacionados pr ON pr.Comprobante = cp.TRAZA
        LEFT JOIN movimientos_bancarios mb ON pr.Movimiento = mb.TRAZA
        INNER JOIN datos_generales_de_cotizaciones cot ON cot.TRAZA = oc.Numero_de_Cotizacion
        LEFT JOIN datos_generales_del_proceso req ON cot.Cod_Req = req.TRAZA
        INNER JOIN contactos cont ON req.Contacto_Cliente = cont.TRAZA
        INNER JOIN empresas e ON e.TRAZA = cont.Empresa

        WHERE oc.Fecha_Emision BETWEEN %s AND %s

    """

    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchall()

    dataCompleta = conseguirSaldo(result)
    return pd.DataFrame(dataCompleta)    

    
### Guias
def conseguirControlGuias(start_date, end_date,cursor):
    query = """
        SELECT 
            oc.TRAZA TRAZA_OC_Cliente,
            oc.Numero_OC_Cliente OC_cliente,
            req.Cod_Req,
            e.Nombre Nombre_cliente,
            oc.Fecha_Emision Fecha_OC_Cliente,
            g.Numero_Guia,
            g.*
            

        FROM datos_generales_ocs_clientes oc
        LEFT JOIN datos_generales_de_cotizaciones cot ON cot.TRAZA = oc.Numero_de_Cotizacion
        LEFT JOIN datos_generales_del_proceso req ON req.TRAZA = cot.Cod_Req
        LEFT JOIN contactos cont ON cont.TRAZA = req.Contacto_Cliente
        LEFT JOIN empresas e ON e.TRAZA = cont.Empresa
        LEFT JOIN guias_emitidas g ON g.OC_de_cliente = oc.TRAZA


        WHERE oc.Fecha_Emision BETWEEN %s AND %s

    """

    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchall()
    print(result)

    return pd.DataFrame(result)
