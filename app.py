import streamlit as st
from datetime import datetime, date
from data.general import conseguirDataGeneral
from data.utils import MESES_ESPANOL


def seleccionar_ano_mes():
    
    hoy = datetime.today()
    
    rango_anios = reversed(range(2000, hoy.year + 1))
    
    # Crear 2 columnas para la selección del año y el mes
    col1, col2 = st.columns(2)

    with col1:
        anio_seleccionado = st.selectbox("Selecciona el año", rango_anios)

    with col2:
        mes_seleccionado = st.selectbox(
            "Selecciona el mes",
            list(range(1, 13)),  # Meses en forma de números
            index=hoy.month - 1,  # Seleccionar el mes actual automáticamente (enero = índice 0)
            format_func=lambda x: [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ][x - 1]
        )
    
   
    return anio_seleccionado, mes_seleccionado





def mostrarMetricasFinancieras(data):
    """Muestra métricas clave en columnas."""
    
   
    res = data['General']
    cols = st.columns(2)
    
    with cols[0]:
        llenarTarjeta(res,'Ventas totales', objetivo='S/. 216,666')
        llenarTarjeta(res,'Resultado ventas', objetivo='S/. 47,666')
        llenarTarjeta(res,'Gastos operacion')
        llenarTarjeta(res,'Resultado total')

    with cols[1]:

        llenarTarjeta(res,'Compras totales', objetivo='S/. 264,333')
        llenarTarjeta(res,'GM', objetivo='22%',es_porcentaje=True)
        llenarTarjeta(res,'Gastos RRHH')
        llenarTarjeta(res,'GM total', es_porcentaje=True)

def llenarTarjeta(resultados,clave, objetivo = None, es_porcentaje=False):
    valor = resultados[clave]
    valor_formateado = f"{valor:.2%}" if es_porcentaje else f"S/. {valor:,.2f}"
    with st.container(border=True):
        st.metric(clave, valor_formateado)

        if objetivo is not None:
           st.caption(f"Objetivo: {objetivo}")
       


# Main code
st.title("Resultados")
anio_seleccionado, mes_seleccionado = seleccionar_ano_mes()

if st.button("Consultar Datos"):

    data = conseguirDataGeneral(mes_seleccionado, anio_seleccionado)

    print(data['Clientes principales'])  # Ver el contenido
    print(type(data['Clientes principales']))  # Ver si es DataFrame
    print(data['Clientes principales'].columns)  # Ver qué columnas tiene


    st.header('Resultados financieros')
    mostrarMetricasFinancieras(data)

    st.header('Clientes principales')
    st.dataframe(data['Clientes principales'], column_config= {"Porcentaje Acumulado" : None})

    st.header('Proveedores principales')
    st.dataframe(data['Proveedores principales'], column_config= {"Porcentaje Acumulado" : None})


    st.header('Facturas')
    st.dataframe(data["Facturas"])
