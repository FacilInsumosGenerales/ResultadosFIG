import streamlit as st
import pandas as pd

from data.administracion import conseguirDataAdministracion
from data.data import conseguirData
from datetime import datetime, timedelta 




st.title("Resumen administración")

today = datetime.today().date()
one_month_ago = today - timedelta(days=30)

start_date = st.date_input("Selecciona la fecha de inicio", value=one_month_ago)
end_date = st.date_input("Selecciona la fecha final", value=today)


# Botón para ejecutar la consulta

if st.button("Consultar Datos"):
    if start_date > end_date:
        st.error("La fecha de inicio no puede ser mayor que la fecha final.")
    else:
        st.write(f"Mostrando datos desde {start_date} hasta {end_date}")
        
        # Obtener los datos y mostrarlos en una tabla
        data = conseguirDataAdministracion(str(start_date), str(end_date))
        
        if data["Proveedores"].empty:
            st.warning("No se encontraron datos en el rango de fechas seleccionado.")
        else:
            st.header('Control de pago a proveedores')
            st.dataframe(data["Proveedores"])

            st.header('Control de pago a clientes')
            st.dataframe(data["Clientes"])

            st.header('Control de guias')
            st.dataframe(data["Guias"])
