import pandas as pd
from decimal import Decimal
from conexion import conectarseABaseDeDatos


def conseguirData(anio):
    connection = conectarseABaseDeDatos()
    cursor = connection.cursor(dictionary=True)

    dataFacturas = conseguirFacturas(anio, cursor)
    dataOCClientes = conseguirOCClientes(anio, cursor)
    dataCotizaciones = conseguirCotizaciones(anio, cursor)

    cursor.close()
    connection.close()

    return {
        'Facturas': dataFacturas,
        'OC Clientes' : dataOCClientes,
        'Cotizaciones': dataCotizaciones
    }

def conseguirFacturas(anio, cursor):
    query = """
        SELECT cp.*,
        empProv.Nombre AS Nombre_proveedor,
        empCli.Nombre AS Nombre_cliente
        FROM comprobantes_de_pago cp
        LEFT JOIN empresas empProv ON empProv.TRAZA = cp.Proveedor
        LEFT JOIN datos_generales_ocs_clientes oc ON cp.OC_cliente = oc.TRAZA
        LEFT JOIN contactos cont ON oc.Contacto_Cliente = cont.TRAZA
        LEFT JOIN empresas empCli ON empCli.TRAZA = cont.Empresa
        WHERE cp.Fecha_Emision >= %s AND cp.Fecha_Emision < %s
    """

    return ejecutarQuery(anio, cursor, query)

def conseguirOCClientes(anio, cursor):
    query = """
        SELECT oc.Valor_sin_IGV,
        cot.Moneda,
        req.Nombre_del_producto Nombre_Req,
        req.Cod_Req
    
        FROM datos_generales_ocs_clientes oc 
        INNER JOIN datos_generales_de_cotizaciones cot ON cot.TRAZA = oc.Numero_de_Cotizacion
        LEFT JOIN datos_generales_del_proceso req ON cot.Cod_Req = req.TRAZA

        WHERE oc.Fecha_Emision >= %s AND oc.Fecha_Emision < %s;
    """
    return ejecutarQuery(anio, cursor, query)

def conseguirCotizaciones(anio, cursor):
    query = """
        SELECT cot.Valor_de_venta Valor_sin_IGV,
        cot.Moneda,
        req.Nombre_del_producto Nombre_Req,
        req.Cod_Req
    
        FROM datos_generales_de_cotizaciones cot 
        LEFT JOIN datos_generales_del_proceso req ON cot.Cod_Req = req.TRAZA

        WHERE cot.Fecha >= %s AND cot.Fecha < %s; 
    """
    return ejecutarQuery(anio, cursor, query)
    

def ejecutarQuery(anio, cursor, query):
    cursor.execute(query, (f"{anio}-01-01", f"{int(anio)+1}-01-01"))
    result = cursor.fetchall()
    dfResultado = pd.DataFrame(result)
    return  convertirASoles(dfResultado) 

def convertirASoles(df):
    df['Valor_sin_IGV'] = df['Valor_sin_IGV'].fillna(Decimal('0'))

    TIPO_CAMBIO_USD_TO_PEN = Decimal('3.64')
    df['Valor_soles'] = df.apply(lambda row: row['Valor_sin_IGV'] * TIPO_CAMBIO_USD_TO_PEN if row['Moneda'] == 'USD' else row['Valor_sin_IGV'], axis=1)

    return df
