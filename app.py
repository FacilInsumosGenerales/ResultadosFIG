import streamlit as st
from datetime import datetime, timedelta
from data.general import conseguirDataGeneral


def configurar_fechas():
    """Configura las fechas de inicio y final para la consulta."""
    today = datetime.today().date()
    one_month_ago = today - timedelta(days=30)
    
    start_date = st.date_input("Selecciona la fecha de inicio", value=one_month_ago)
    end_date = st.date_input("Selecciona la fecha final", value=today)
    
    return start_date, end_date


def validar_fechas(start_date, end_date):
    """Valida que la fecha de inicio no sea posterior a la fecha final."""
    if start_date > end_date:
        st.error("La fecha de inicio no puede ser mayor que la fecha final.")
        return False
    return True

  


def mostrar_facturas(data):
    """Muestra las facturas si existen; de lo contrario, muestra una advertencia."""
    if data["Facturas"].empty:
        st.warning("No se encontraron datos en el rango de fechas seleccionado.")
    else:
        st.dataframe(data["Facturas"])


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
start_date, end_date = configurar_fechas()

if st.button("Consultar Datos"):
    if validar_fechas(start_date, end_date):
        st.write(f"Mostrando datos desde {start_date} hasta {end_date}")

        data = conseguirDataGeneral(str(start_date), str(end_date))

        

        st.header('Resultados financieros')
        mostrarMetricasFinancieras(data)

        

        st.header('Facturas')
        mostrar_facturas(data)
