import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import subprocess
import sys

# --- Garantir que o html5lib esteja instalado ---
try:
    import html5lib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "html5lib"])
    import html5lib

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
    url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tables = pd.read_html(response.text, header=3)

        df = tables[0]
        df.columns = ['Ano/Mês', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        df['Ano/Mês'] = pd.to_numeric(df['Ano/Mês'], errors='coerce')
        df = df.dropna(subset=['Ano/Mês'])
        df['Ano/Mês'] = df['Ano/Mês'].astype(int)

        for mes in df.columns[1:]:
            df[mes] = df[mes].astype(str).str.replace(',', '.')
            df[mes] = pd.to_numeric(df[mes], errors='coerce') / 100

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
                valor_corrigido = valor_digitado * (1 + taxa)
                taxa_formatada = f"{taxa * 100:,.2f}".replace('.', ',')
                st.success(f"Taxa SELIC acumulada em {nome_mes}/{ano_procurado}: {taxa_formatada}%")
                st.success(f"Valor corrigido: R$ {valor_corrigido:,.2f}".replace('.', ','))
            else:
                st.warning(f"A taxa SELIC para {nome_mes}/{ano_procurado} não está disponível na tabela.")
        else:
            st.warning(f"Não foi possível encontrar o ano {ano_procurado} na tabela SELIC.")
    else:
        st.error("Falha ao recuperar a tabela SELIC.")
