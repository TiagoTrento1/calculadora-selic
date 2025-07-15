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

def buscar_tabelas_selic():
    url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        # Captura todas as tabelas, com header na linha 4 (índice 4 = 5a linha)
        tables = pd.read_html(response.text, header=4)

        st.write(f"Total de tabelas encontradas: {len(tables)}")
        for i, tabela in enumerate(tables):
            st.write(f"--- Tabela índice {i} ---")
            st.dataframe(tabela.head())

        return tables

    except Exception as e:
        st.error(f"Erro ao buscar ou processar as tabelas SELIC: {e}")
        return None

if st.button("Carregar tabelas"):
    tabelas = buscar_tabelas_selic()
    if tabelas is not None:
        st.write("Por favor, observe as tabelas acima e escolha o índice da tabela ACUMULADA para usar no cálculo.")

indice_acumulada = st.number_input(
    "Digite o índice da tabela acumulada para usar no cálculo:",
    min_value=0,
    max_value=10,
    value=2,
    step=1
)

def processar_tabela_acumulada(tabela, mes_ano):
    # Renomeia colunas
    tabela.columns = ['Ano', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    tabela['Ano'] = pd.to_numeric(tabela['Ano'], errors='coerce')
    tabela = tabela.dropna(subset=['Ano'])
    tabela['Ano'] = tabela['Ano'].astype(int)

    for mes in ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']:
        tabela[mes] = pd.to_numeric(tabela[mes], errors='coerce') / 100

    ano_procurado = mes_ano.year
    mes_procurado = mes_ano.month
    nome_mes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][mes_procurado - 1]

    linha_ano = tabela[tabela['Ano'] == ano_procurado]

    if not linha_ano.empty:
        taxa = linha_ano.iloc[0][nome_mes]
        if pd.notnull(taxa):
            return taxa
        else:
            st.warning(f"Taxa SELIC acumulada para {nome_mes}/{ano_procurado} não disponível.")
            return None
    else:
        st.warning(f"Ano {ano_procurado} não encontrado na tabela.")
        return None

if st.button("Calcular SELIC"):
    tabelas = buscar_tabelas_selic()
    if tabelas is not None and len(tabelas) > indice_acumulada:
        selic_acumulada = tabelas[indice_acumulada]
        st.subheader("Tabela SELIC acumulada selecionada:")
        st.dataframe(selic_acumulada)

        taxa = processar_tabela_acumulada(selic_acumulada, data_selecionada)
        if taxa is not None:
            valor_corrigido = valor_digitado * (1 + taxa)
            taxa_formatada = f"{taxa * 100:,.2f}%".replace('.', ',')
            st.success(f"Taxa SELIC acumulada em {data_selecionada.strftime('%m/%Y')}: {taxa_formatada}")
            st.success(f"Valor corrigido: R$ {valor_corrigido:.2f}")
    else:
        st.error("Tabela acumulada não disponível ou índice inválido.")
