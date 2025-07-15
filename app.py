import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Calculadora SELIC Acumulada", layout="centered")

st.title("💰 Calculadora SELIC Acumulada")
st.markdown("Insira um valor e selecione o mês/ano para calcular o valor com a taxa SELIC acumulada do site da SEF/SC.")

# Entrada de dados
valor_digitado = st.number_input(
    "Digite o valor a ser calculado (Ex: 1000.00)",
    min_value=0.01,
    format="%.2f",
    value=1000.00
)

data_selecionada = st.date_input(
    "Selecione o mês e ano para o cálculo:",
    value=datetime.now().date(),
    min_value=datetime(2000, 1, 1).date(),
    max_value=datetime.now().date()
)

def buscar_tabela_selic():
    url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tables = pd.read_html(response.text)
        selic_df = tables[0]
        return selic_df
    except Exception as e:
        st.error(f"Erro ao buscar a tabela SELIC: {e}")
        return None

if st.button("Calcular SELIC"):
    selic_df = buscar_tabela_selic()
    if selic_df is not None:
        # Primeiro, olhar como está a tabela
        st.write("Tabela bruta:", selic_df)
        
        # A primeira coluna é "Ano/Mês"
        # A primeira linha tem os anos (começando da segunda coluna)
        anos = selic_df.columns[1:].tolist()
        # A primeira coluna a partir da segunda linha tem os meses
        meses = selic_df.iloc[:, 0].tolist()[1:]
        
        # Construir dataframe transposto com meses como linhas e anos como colunas
        dados = selic_df.iloc[1:, 1:]
        dados.index = meses
        dados.columns = anos
        
        # Converter valores para float (trocar ',' por '.' e converter)
        dados = dados.applymap(lambda x: float(str(x).replace(',', '.')))
        
        mes_procurado = data_selecionada.strftime('%b')  # Ex: 'Jun'
        ano_procurado = str(data_selecionada.year)       # Ex: '2025'
        
        # Mapear mês para abreviação usada na tabela (abreviações em português com 3 letras)
        meses_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        mes_abrev = meses_pt[data_selecionada.month -1]
        
        if ano_procurado not in dados.columns:
            st.warning(f"Não foi possível encontrar o ano {ano_procurado} na tabela SELIC.")
        elif mes_abrev not in dados.index:
            st.warning(f"O mês '{mes_abrev}' não foi encontrado na tabela SELIC.")
        else:
            taxa_selic_encontrada = dados.loc[mes_abrev, ano_procurado]
            resultado = valor_digitado * (taxa_selic_encontrada / 100)
            
            st.success(f"**Taxa SELIC Acumulada ({mes_abrev}/{ano_procurado}):** {taxa_selic_encontrada:.2f}%")
            st.success(f"**Valor Calculado:** R$ {resultado:.2f}")
    else:
        st.error("Não foi possível recuperar a tabela SELIC.")
