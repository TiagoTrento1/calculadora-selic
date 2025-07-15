import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Calculadora SELIC Acumulada", layout="centered")

st.title("💰 Calculadora SELIC Acumulada")
st.markdown("Insira um valor e selecione o mês/ano para calcular o valor com a taxa SELIC acumulada do site da SEF/SC.")

# --- Entrada de Dados ---
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
    """Busca a tabela SELIC acumulada do site da SEF/SC"""
    url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tables = pd.read_html(response.text)
        return tables[0]  # Supondo que a tabela desejada é a primeira
    except Exception as e:
        st.error(f"Erro ao buscar a tabela SELIC: {e}")
        return None

def try_float(x):
    try:
        return float(str(x).replace(',', '.'))
    except:
        return np.nan

# --- Botão de Cálculo ---
if st.button("Calcular SELIC"):
    dados = buscar_tabela_selic()

    if dados is not None:
        # Converter todos os valores da tabela (exceto coluna "Ano/Mês") para float, tratando erros
        # A coluna 'Ano/Mês' é a primeira e contém os anos, as outras colunas são meses
        dados.iloc[:, 1:] = dados.iloc[:, 1:].applymap(try_float)

        ano_procurado = data_selecionada.year
        mes_procurado = data_selecionada.strftime('%b')  # Nome abreviado do mês, ex: 'Jun'

        # Ajustar mês para formato com inicial maiúscula, pois a tabela usa Jan, Fev, Mar etc.
        mes_procurado = mes_procurado.capitalize()

        if 'Ano/Mês' not in dados.columns:
            st.error("Coluna 'Ano/Mês' não encontrada na tabela SELIC.")
        elif mes_procurado not in dados.columns:
            st.error(f"O mês '{mes_procurado}' não foi encontrado nas colunas normalizadas da tabela SELIC.")
        else:
            # Filtrar linha com o ano desejado
            linha_ano = dados[dados['Ano/Mês'] == ano_procurado]

            if linha_ano.empty:
                st.warning(f"Não foi possível encontrar o ano {ano_procurado} na tabela SELIC.")
            else:
                taxa_selic_encontrada = linha_ano.iloc[0][mes_procurado]

                if pd.isna(taxa_selic_encontrada):
                    st.warning(f"Não foi encontrada taxa SELIC para {mes_procurado}/{ano_procurado}.")
                else:
                    resultado = valor_digitado * (taxa_selic_encontrada / 100)
                    st.success(f"**Taxa SELIC Acumulada ({mes_procurado}/{ano_procurado}):** {taxa_selic_encontrada:.2f}%")
                    st.success(f"**Valor Calculado:** R$ {resultado:.2f}")
    else:
        st.error("Não foi possível recuperar a tabela SELIC.")
