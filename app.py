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
    url = "https://www.sef.sc.gov.br/servicos/juro-selic"
    try:
        tables = pd.read_html(url, thousands='.', decimal=',')
        df = tables[3]  # A quarta tabela da página corresponde à SELIC acumulada
        
        # Substitui vírgulas por ponto e converte para float todas as colunas exceto 'Ano/Mês'
        for col in df.columns[1:]:
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

        return df
    except Exception as e:
        st.error(f"Erro ao buscar ou processar a tabela SELIC: {e}")
        return None

if st.button("Calcular SELIC"):
    selic_df = buscar_tabela_selic()

    if selic_df is not None:
        st.subheader("Pré-visualização da Tabela SELIC carregada:")
        st.dataframe(selic_df)

        ano_procurado = data_selecionada.year
        mes_procurado = data_selecionada.month
        nome_mes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 
                    'Ago', 'Set', 'Out', 'Nov', 'Dez'][mes_procurado - 1]

        linha_ano = selic_df[selic_df['Ano/Mês'] == ano_procurado]

        if not linha_ano.empty:
            taxa = linha_ano.iloc[0][nome_mes]

            if pd.notnull(taxa):
                valor_corrigido = valor_digitado * (1 + (taxa / 100))
                taxa_formatada = f"{taxa:,.2f}".replace('.', ',')
                valor_formatado = f"{valor_corrigido:,.2f}".replace('.', ',')
                st.success(f"Taxa SELIC acumulada em {nome_mes}/{ano_procurado}: {taxa_formatada}%")
                st.success(f"Valor corrigido: R$ {valor_formatado}")
            else:
                st.warning(f"A taxa SELIC para {nome_mes}/{ano_procurado} não está disponível na tabela.")
        else:
            st.warning(f"Não foi possível encontrar o ano {ano_procurado} na tabela SELIC.")
    else:
        st.error("Falha ao recuperar a tabela SELIC.")
