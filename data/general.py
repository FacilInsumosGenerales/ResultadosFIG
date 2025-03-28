from conexion import conectarseABaseDeDatos
import pandas as pd


def conseguirDataGeneral(start_date, end_date):
    connection = conectarseABaseDeDatos()
    cursor = connection.cursor(dictionary=True)


    dataFacturas = conseguirFacturas(start_date, end_date, cursor)
    resultados = calcularResultados(dataFacturas)


    cursor.close()
    connection.close()

    return {
        "Facturas": dataFacturas,
        "General":resultados
    }



# anadir nombre de empresa y ruc
def conseguirFacturas(start_date, end_date,cursor):
    query = """
        SELECT *

        FROM comprobantes_de_pago comp
        WHERE comp.Fecha_Emision BETWEEN %s AND %s
    """

    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchall()
    

    return pd.DataFrame(result)

def calcularResultados(df):
    
    ventas_totales = df[df["Categoria"] == 0]["Valor_sin_IGV"].sum()
    compras_totales = df[df["Categoria"] == 1]["Valor_sin_IGV"].sum()
    resultado_ventas = ventas_totales - compras_totales

    gastos_operacion = df[df["Categoria"].isin([2, 4])]["Valor_sin_IGV"].sum()
    gastos_rrhh = df[df["Categoria"] == 3]["Valor_sin_IGV"].sum()

    resultados_totales = resultado_ventas - gastos_operacion - gastos_rrhh

    gm = resultado_ventas / ventas_totales if ventas_totales != 0 else 0
    gm_total = resultados_totales / ventas_totales if ventas_totales != 0 else 0

    return{
        'Ventas totales':ventas_totales,
        'Compras totales': compras_totales,
        'Resultado ventas': resultado_ventas,
        'Gastos operacion': gastos_operacion,
        'Gastos RRHH': gastos_rrhh,
        'Resultado total': resultados_totales,
        'GM': gm,
        'GM total':gm_total
    }