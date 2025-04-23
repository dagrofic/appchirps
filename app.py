{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "e00b996a-9052-4b3f-9dca-53fb7ae26d45",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2025-04-23 15:51:49.848 \n",
      "  \u001b[33m\u001b[1mWarning:\u001b[0m to view this Streamlit app on a browser, run it with the following\n",
      "  command:\n",
      "\n",
      "    streamlit run C:\\ProgramData\\anaconda3\\Lib\\site-packages\\ipykernel_launcher.py [ARGUMENTS]\n"
     ]
    }
   ],
   "source": [
    "import streamlit as st\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import datetime\n",
    "import ee\n",
    "\n",
    "# Inicialização do Google Earth Engine\n",
    "try:\n",
    "    ee.Initialize()\n",
    "except Exception as e:\n",
    "    ee.Authenticate()\n",
    "    ee.Initialize()\n",
    "\n",
    "# Função para obter dados anuais do CHIRPS\n",
    "def obter_dados_anuais(lat, lon, ano, inicio, fim):\n",
    "    ponto = ee.Geometry.Point(lon, lat)\n",
    "    data_inicio = f\"{ano}-{inicio}\"\n",
    "    data_fim = f\"{ano}-{fim}\"\n",
    "    \n",
    "    precipitacao = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')\\\n",
    "        .filterDate(data_inicio, data_fim)\\\n",
    "        .sum()\\\n",
    "        .reduceRegion(reducer=ee.Reducer.mean(), geometry=ponto, scale=5000)\n",
    "    \n",
    "    valor_precipitacao = precipitacao.getInfo().get('precipitation', 0)\n",
    "\n",
    "    return {'Ano': ano, 'CHIRPS': valor_precipitacao}\n",
    "\n",
    "# Interface Streamlit\n",
    "st.title('Aplicativo Web - CHIRPS Earth Engine')\n",
    "\n",
    "lat = st.number_input('Latitude', value=-15.0)\n",
    "lon = st.number_input('Longitude', value=-47.0)\n",
    "\n",
    "inicio = st.date_input('Data Inicial', datetime.date(2024, 1, 1)).strftime('%m-%d')\n",
    "fim = st.date_input('Data Final', datetime.date(2024, 12, 31)).strftime('%m-%d')\n",
    "\n",
    "if st.button('Gerar Relatório'):\n",
    "    anos = range(1981, datetime.datetime.now().year + 1)\n",
    "    resultados = []\n",
    "\n",
    "    progresso = st.progress(0)\n",
    "\n",
    "    for i, ano in enumerate(anos):\n",
    "        resultado = obter_dados_anuais(lat, lon, ano, inicio, fim)\n",
    "        resultados.append(resultado)\n",
    "        progresso.progress((i+1)/len(anos))\n",
    "\n",
    "    df = pd.DataFrame(resultados)\n",
    "    df_filtrado = df[df['CHIRPS'] > 0]\n",
    "\n",
    "    st.write('### Dados de Precipitação Anuais')\n",
    "    st.dataframe(df_filtrado)\n",
    "\n",
    "    # Gráfico\n",
    "    fig, ax = plt.subplots()\n",
    "    ax.bar(df_filtrado['Ano'], df_filtrado['CHIRPS'], color='skyblue')\n",
    "    ax.set_xlabel('Ano')\n",
    "    ax.set_ylabel('Precipitação Acumulada (mm)')\n",
    "    ax.set_title('Precipitação Anual - CHIRPS')\n",
    "\n",
    "    st.pyplot(fig)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "8aca9041-6a63-4157-8158-b6ac46000e01",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
