import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Calculadora SELIC Acumulada", layout="centered")

st.title("💰 Calculadora SELIC Acumulada")
st.markdown("Insira um valor e selecione o mês/ano para calcular o valor com a taxa SELIC acumulada da SEF/SC.")

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
    """Busca e retorna a tabela SELIC acumulada"""
    url = 'https://www.sef.sc.gov.br/servicos/juro-selic'
    try:
        tables = pd.read_html(url)
        df = tables[3]  # Tabela acumulada

        df = df.replace(',', '.', regex=True)
        df.iloc[:, 1:] = df.iloc[:, 1:].astype(float)
        return df
    except Exception as e:
        st.error(f"Erro ao buscar ou processar a tabela SELIC: {e}")
        return None

def calcular_valor_corrigido(df, ano, mes, valor_base):
    mes_abrev = mes.capitalize()[:3]
    if mes_abrev not in df.columns:
        st.error("Mês inválido.")
        return None, None

    linha_ano = df[df['Ano/Mês'] == ano]
    if linha_ano.empty:
        st.error(f"Ano {ano} não encontrado na tabela SELIC.")
        return None, None

    taxa = linha_ano[mes_abrev].values[0]
    if pd.isnull(taxa):
        st.warning(f"Taxa SELIC para {mes_abrev}/{ano} não disponível.")
        return None, None

    valor_corrigido = valor_base * (1 + taxa / 100)
    return taxa, valor_corrigido

if st.button("Calcular SELIC"):
    selic_df = buscar_tabela_selic()

    if selic_df is not None:
        st.subheader("Pré-visualização da Tabela SELIC carregada:")
        st.dataframe(selic_df)

        ano_procurado = data_selecionada.year
        mes_procurado = data_selecionada.strftime('%B')

        taxa, valor_corrigido = calcular_valor_corrigido(
            selic_df, ano_procurado, mes_procurado, valor_digitado
        )

        if taxa is not None:
            st.success(f"Taxa SELIC acumulada em {mes_procurado[:3]}/{ano_procurado}: {taxa:.2f}%")
            st.success(f"Valor corrigido: R$ {valor_corrigido:,.2f}".replace('.', ','))
