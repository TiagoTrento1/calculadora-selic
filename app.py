import streamlit as st
import pandas as pd
import requests
from datetime import datetime

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

# --- Botão de Cálculo ---
if st.button("Calcular SELIC"):
    selic_df = buscar_tabela_selic()

    if selic_df is not None:
        mes_procurado = data_selecionada.month
        ano_procurado = data_selecionada.year

        # Padronizar colunas como string para evitar erros
        selic_df.columns = selic_df.columns.astype(str)

        # Converter ano da primeira coluna
        try:
            selic_df.iloc[:,0] = selic_df.iloc[:,0].astype(int)
        except:
            pass

        linha_ano = selic_df[selic_df.iloc[:,0] == ano_procurado]

        if not linha_ano.empty:
            nome_mes = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][mes_procurado-1]

            try:
                taxa_selic_str = linha_ano.iloc[0][nome_mes]
                taxa_selic_encontrada = float(str(taxa_selic_str).replace(',','.'))

                resultado = valor_digitado * (taxa_selic_encontrada / 100)

                st.success(f"**Taxa SELIC Acumulada ({nome_mes}/{ano_procurado}):** {taxa_selic_encontrada:.2f}%")
                st.success(f"**Valor Calculado:** R$ {resultado:.2f}")

            except Exception as e:
                st.warning(f"Não foi possível encontrar ou converter a taxa SELIC para {nome_mes}/{ano_procurado}.")
        else:
            st.warning(f"Não foi possível encontrar o ano {ano_procurado} na tabela SELIC.")
    else:
        st.error("Não foi possível recuperar a tabela SELIC.")
