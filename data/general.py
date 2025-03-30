from decimal import Decimal
from conexion import conectarseABaseDeDatos
import pandas as pd
import seaborn as sns

from data.utils import MESES_ESPANOL
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors




data = {
    "Fecha_Emision": pd.to_datetime([
        "2025-01-10", "2025-01-15", "2025-02-20", "2025-02-25",
        "2025-03-05", "2025-03-15", "2025-04-10", "2025-04-20"
    ]),
    "Nombre_proveedor": [
        "Cliente A", "Cliente B", "Cliente A", "Cliente C",
        "Cliente B", "Cliente C", "Cliente A", "Cliente B"
    ],
    "Valor_soles": [1000, 1500, 1200, 800, 2000, 900, 1700, 1300]
}

df_ejemplo = pd.DataFrame(data)

def conseguirDataGeneral(mes, anio):
    connection = conectarseABaseDeDatos()
    cursor = connection.cursor(dictionary=True)
    dataFacturas = conseguirFacturas(anio, cursor)
    cursor.close()
    connection.close()

    resultados = calcularResultados(dataFacturas,mes)
    clientes = calcularClientesPrincipales(dataFacturas,mes)
    proveedores = calcularProveedoresPrincipales(dataFacturas,mes)


    return {
        "Facturas": dataFacturas,
        "General":resultados,
        "Clientes principales": clientes,
        "Proveedores principales": proveedores
    }



# anadir nombre de empresa y ruc
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

    cursor.execute(query, (f"{anio}-01-01", f"{int(anio)+1}-01-01"))

    result = cursor.fetchall()

    dfResultado = pd.DataFrame(result)
    
    return  convertirASoles(dfResultado) 

def convertirASoles(df):
    df['Valor_sin_IGV'] = df['Valor_sin_IGV'].fillna(Decimal('0'))

    TIPO_CAMBIO_USD_TO_PEN = Decimal('3.64')
    df['Valor_soles'] = df.apply(lambda row: row['Valor_sin_IGV'] * TIPO_CAMBIO_USD_TO_PEN if row['Moneda'] == 'USD' else row['Valor_sin_IGV'], axis=1)

    return df

# Primer diagrama
def calcularResultados(df,mes):

    df["Fecha_Emision"] = pd.to_datetime(df["Fecha_Emision"])
    df_filtrado = df[df["Fecha_Emision"].dt.month == mes]
    

    ventas_totales = df_filtrado[df_filtrado["Categoria"] == 0]["Valor_soles"].sum()
    compras_totales = df_filtrado[df_filtrado["Categoria"] == 1]["Valor_soles"].sum()
    resultado_ventas = ventas_totales - compras_totales

    gastos_operacion = df_filtrado[df_filtrado["Categoria"].isin([2, 4])]["Valor_soles"].sum()
    gastos_rrhh = df_filtrado[df_filtrado["Categoria"] == 3]["Valor_soles"].sum()

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

# Segundo diagrama
def calcularClientesPrincipales(df, mes):
    return calcularEntidadesPrincipales (df, mes, 'Nombre_cliente')

def calcularProveedoresPrincipales(df, mes):
    return calcularEntidadesPrincipales (df, mes, 'Nombre_proveedor')


def calcularEntidadesPrincipales(df, mes, entidad):
    """Genera una tabla de totales mensuales por cliente, ordenada por un mes específico."""
    
    df = df.dropna(subset=[entidad]).copy()
    df["Fecha_Emision"] = pd.to_datetime(df["Fecha_Emision"])
    df["Mes"] = df["Fecha_Emision"].dt.month

    # Definir los 12 meses como columnas fijas
    meses_completos = list(range(1, mes+1))

    # Crear tabla pivote
    tabla = df.pivot_table(index=entidad, columns="Mes", values="Valor_soles", aggfunc="sum", fill_value=0)
    tabla = tabla.reindex(columns=meses_completos, fill_value=0) 

    # Agregar columna total por cliente 
    tabla["Total"] = tabla.sum(axis=1)

    # Ordenar por el mes seleccionado y agregar fila de totales
    tabla = tabla.sort_values(by=mes, ascending=False)
    tabla.loc["TOTAL"] = tabla.sum()

    # Calcular porcentaje de cliente
    tabla["Porcentaje"] = tabla[mes] / tabla.loc["TOTAL", mes] * 100
    tabla["Porcentaje"] = tabla["Porcentaje"].apply(lambda x: f"{x:.2f}%")

    # Diccionario para mapear números de mes a nombres en español
    
    mes_seleccionado = MESES_ESPANOL[mes]

    # Renombrar las columnas numéricas a nombres de meses
    tabla = tabla.rename(columns=MESES_ESPANOL)

    # Cambiar el nombre de la columna 'Porcentaje' para incluir el mes seleccionado
    tabla = tabla.rename(columns={"Porcentaje": f"Porcentaje {mes_seleccionado}"})


    # Estilizar columnas
    mapaColores = sns.light_palette("#79C", as_cmap=True)  
    colorSombra = mapaColores(0.5)

    

    tabla["Porcentaje Acumulado"] = (
        tabla[f"Porcentaje {mes_seleccionado}"]
        .str.rstrip("%") # Quita el símbolo '%'
        .astype(float) # Convierte a número
        .cumsum() # Calcula la suma acumulativa        
    )

    tabla_estilizada = (
        tabla.style
        .background_gradient(
            cmap=mapaColores, subset=pd.IndexSlice[tabla.index[:-1], [mes_seleccionado]]
        )
        .map(
            lambda _: f"background-color: {mcolors.rgb2hex(colorSombra)} ;",
            subset=(tabla.index[tabla["Porcentaje Acumulado"] < 80], f"Porcentaje {mes_seleccionado}")
        )
    )


    return tabla_estilizada
