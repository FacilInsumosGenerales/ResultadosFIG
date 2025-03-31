import pandas as pd
import seaborn as sns

from data.informeGeneral.conseguirData import conseguirData
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
    
    data = conseguirData(anio)

    resultados = calcularResultados(data['Facturas'],mes)
    clientes = calcularClientesPrincipales(data['Facturas'],mes)
    proveedores = calcularProveedoresPrincipales(data['Facturas'],mes)


    return {
        "Facturas": data['Facturas'],
        "General":resultados,
        "Clientes principales": clientes,
        "Proveedores principales": proveedores,

        "1": data['OC Clientes'],
        "2":data['Cotizaciones']
    }




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
    MESES_ESPANOL = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
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

## OC por requerimiento (3er diagrama)

