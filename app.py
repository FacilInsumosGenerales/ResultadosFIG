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


def mostrar_mensaje_rango_fechas(start_date, end_date):
    """Muestra un mensaje indicando el rango de fechas seleccionado."""
    st.write(f"Mostrando datos desde {start_date} hasta {end_date}")


def mostrar_facturas(data):
    """Muestra las facturas si existen; de lo contrario, muestra una advertencia."""
    if data["Facturas"].empty:
        st.warning("No se encontraron datos en el rango de fechas seleccionado.")
    else:
        st.header('Facturas')
        st.dataframe(data["Facturas"])


def mostrar_metricas_resultados(resultadosGenerales):
    """Muestra métricas clave en columnas."""
    st.header('Resultados ')
    cols = st.columns(2)
    
    with cols[0]:
        mostrar_metricas_financieras(resultadosGenerales, 
                                    [
                                        ("Ventas Totales", 'Ventas totales',False),
                                        ("Resultado de Ventas", 'Resultado ventas',False),
                                        ("Gastos de Operación", 'Gastos operacion',False),
                                        ("Resultados Totales", 'Resultado total',False)
                                    ])
    with cols[1]:
        mostrar_metricas_financieras(resultadosGenerales, 
                                    [
                                        ("Compras Totales", 'Compras totales',False),
                                        ("Margen Bruto (GM)", 'GM', True),
                                        ("Gastos de RRHH", 'Gastos RRHH',False),
                                        ("Margen Bruto Total (GM Total)", 'GM total', True)
                                    ])


def mostrar_metricas_financieras(resultados, metricas):
    """Muestra métricas financieras en contenedores con nombres y claves proporcionadas."""
    for nombre, clave, es_porcentaje in metricas:
        valor = resultados[clave]
        valor_formateado = f"{valor:.2%}" if es_porcentaje else f"${valor:,.2f}"
        with st.container(border=True):
            st.metric(nombre, valor_formateado)


# Main code
st.title("Resultados")
start_date, end_date = configurar_fechas()

if st.button("Consultar Datos"):
    if validar_fechas(start_date, end_date):
        mostrar_mensaje_rango_fechas(start_date, end_date)
        data = conseguirDataGeneral(str(start_date), str(end_date))
        mostrar_facturas(data)
        mostrar_metricas_resultados(data['General'])
