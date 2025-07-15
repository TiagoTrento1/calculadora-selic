import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Calculadora SELIC Acumulada", layout="centered")

st.title("💰 Calculadora SELIC Acumulada")
st.markdown("Insira um valor e selecione o mês/ano para calcular o valor com a taxa SELIC acumulada do site da SEF/SC.")

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
        tables = pd.read_html(response.text, header=3)
        df = tables[0]
        df.rename(columns={df.columns[0]: "Ano"}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Erro ao buscar a tabela SELIC: {e}")
        return None

if st.button("Calcular SELIC"):
    selic_df = buscar_tabela_selic()

    if selic_df is not None:
        ano_procurado = data_selecionada.year
        mes_procurado_idx = data_selecionada.month - 1
        meses_portugues = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                           'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        mes_procurado = meses_portugues[mes_procurado_idx]

        linha_ano = selic_df[selic_df["Ano"] == ano_procurado]
        if not linha_ano.empty:
            if mes_procurado in linha_ano.columns:
                taxa_valor = linha_ano[mes_procurado].values[0]
                try:
                    taxa_selic = float(str(taxa_valor).replace(',', '.')) / 100
                    resultado = valor_digitado * (taxa_selic / 100)
                    st.success(f"**Taxa SELIC Acumulada ({mes_procurado}/{ano_procurado}):** {taxa_selic:.4f}%")
                    st.success(f"**Valor Calculado:** R$ {resultado:.2f}")
                except Exception as e:
                    st.error(f"Erro ao converter taxa SELIC: {e}")
            else:
                st.warning(f"O mês '{mes_procurado}' não foi encontrado na tabela SELIC.")
        else:
            st.warning(f"Não foi possível encontrar o ano {ano_procurado} na tabela SELIC.")
    else:
        st.error("Não foi possível recuperar a tabela SELIC.")
