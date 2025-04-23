import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import ee
import os

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

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input('Latitude', value=-15.0)
    inicio = st.date_input('Data Inicial', datetime.date(2024, 1, 1)).strftime('%m-%d')
    strike = st.number_input('Strike (mm)', value=230.0)
with col2:
    lon = st.number_input('Longitude', value=-47.0)
    fim = st.date_input('Data Final', datetime.date(2024, 12, 31)).strftime('%m-%d')
    exit = st.number_input('Exit (mm)', value=1000.0)

output_dir = st.text_input('Diretório de saída', value=os.path.expanduser('~/Downloads'))

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

    # Exportar para Excel
    excel_path = os.path.join(output_dir, f"CHIRPS_{lat}_{lon}.xlsx")
    try:
        df_filtrado.to_excel(excel_path, index=False)
        st.success(f'Dados salvos em: {excel_path}')
    except Exception as e:
        st.error(f'Erro ao salvar o arquivo: {e}')

    # Gráfico avançado
    fig, ax = plt.subplots(figsize=(12, 6))
    cores = ['orange' if val < strike else 'green' for val in df_filtrado['CHIRPS']]

    # Faixas de fundo
    ax.axhspan(0, strike, facecolor='#fde0dd', alpha=0.4)
    ax.axhspan(strike, exit, facecolor='#e5f5e0', alpha=0.4)
    ax.axhspan(exit, df_filtrado['CHIRPS'].max()*1.05, facecolor='#deebf7', alpha=0.3)

    ax.bar(df_filtrado['Ano'], df_filtrado['CHIRPS'], color=cores)

    media = df_filtrado['CHIRPS'].mean()
    ax.axhline(y=strike, color='red', linestyle='-', linewidth=2, label=f'Strike: {strike} mm')
    ax.axhline(y=exit, color='blue', linestyle='-', linewidth=2, label=f'Exit: {exit} mm')
    ax.axhline(y=media, color='green', linestyle='--', linewidth=1.5, label=f'Média: {media:.1f} mm')

    max_valor = df_filtrado['CHIRPS'].max()
    max_ano = df_filtrado.loc[df_filtrado['CHIRPS'].idxmax(), 'Ano']
    min_valor = df_filtrado['CHIRPS'].min()
    min_ano = df_filtrado.loc[df_filtrado['CHIRPS'].idxmin(), 'Ano']

    ax.annotate(f'Máximo: {max_valor:.1f} mm', xy=(max_ano, max_valor), xytext=(max_ano, max_valor+40),
                arrowprops=dict(facecolor='black', arrowstyle='->'), bbox=dict(boxstyle="round", fc="yellow", ec="black"))
    ax.annotate(f'Mínimo: {min_valor:.1f} mm', xy=(min_ano, min_valor), xytext=(min_ano, min_valor-100),
                arrowprops=dict(facecolor='black', arrowstyle='->'), bbox=dict(boxstyle="round", fc="yellow", ec="black"))

    ax.set_xlabel('Ano')
    ax.set_ylabel('Precipitação (mm)')
    ax.set_title('Precipitação Anual (CHIRPS)')
    ax.legend()
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    st.pyplot(fig)
