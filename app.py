import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import ee

# Inicialização do Google Earth Engine
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# Função para obter dados anuais do CHIRPS
def obter_dados_anuais(lat, lon, ano, inicio, fim):
    ponto = ee.Geometry.Point(lon, lat)
    data_inicio = f"{ano}-{inicio}"
    data_fim = f"{ano}-{fim}"
    
    precipitacao = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')\
        .filterDate(data_inicio, data_fim)\
        .sum()\
        .reduceRegion(reducer=ee.Reducer.mean(), geometry=ponto, scale=5000)
    
    valor_precipitacao = precipitacao.getInfo().get('precipitation', 0)

    return {'Ano': ano, 'CHIRPS': valor_precipitacao}

# Interface Streamlit
st.title('Aplicativo Web - CHIRPS Earth Engine')

lat = st.number_input('Latitude', value=-15.0)
lon = st.number_input('Longitude', value=-47.0)

inicio = st.date_input('Data Inicial', datetime.date(2024, 1, 1)).strftime('%m-%d')
fim = st.date_input('Data Final', datetime.date(2024, 12, 31)).strftime('%m-%d')

if st.button('Gerar Relatório'):
    anos = range(1981, datetime.datetime.now().year + 1)
    resultados = []

    progresso = st.progress(0)

    for i, ano in enumerate(anos):
        resultado = obter_dados_anuais(lat, lon, ano, inicio, fim)
        resultados.append(resultado)
        progresso.progress((i+1)/len(anos))

    df = pd.DataFrame(resultados)
    df_filtrado = df[df['CHIRPS'] > 0]

    st.write('### Dados de Precipitação Anuais')
    st.dataframe(df_filtrado)

    # Gráfico
    fig, ax = plt.subplots()
    ax.bar(df_filtrado['Ano'], df_filtrado['CHIRPS'], color='skyblue')
    ax.set_xlabel('Ano')
    ax.set_ylabel('Precipitação Acumulada (mm)')
    ax.set_title('Precipitação Anual - CHIRPS')

    st.pyplot(fig)
