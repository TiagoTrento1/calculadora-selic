import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Calculadora SELIC Acumulada", page_icon="📈")

st.title("📈 Calculadora SELIC Acumulada")

st.markdown("Informe o valor e a data de referência para calcular o valor corrigido pela taxa SELIC acumulada.")

st.divider()

valor_digitado = st.number_input(
    "💰 Valor base para o cálculo (R$):",
    min_value=0.01,
    format="%.2f",
    value=1000.00
)

data_selecionada = st.date_input(
    "📅 Selecione o mês/ano para aplicar a SELIC acumulada:",
    value=datetime.now().date(),
    min_value=datetime(2000, 1, 1).date(),
    max_value=datetime.now().date()
)

st.divider()

def buscar_tabela_id(url, tabela_id):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tabela_html = soup.find('table', id=tabela_id)
        if tabela_html:
            tabela = pd.read_html(str(tabela_html), header=0)[0]
            return tabela
        else:
            st.error(f"❌ Tabela com id '{tabela_id}' não encontrada na página.")
            return None
    except Exception as e:
        st.error(f"❌ Erro ao buscar tabela: {e}")
        return None

def processar_tabela(tabela, mes_ano):
    tabela.columns = ['Ano', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    tabela['Ano'] = pd.to_numeric(tabela['Ano'], errors='coerce')
    tabela = tabela.dropna(subset=['Ano']).astype({'Ano': 'int'})

    for mes in ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']:
        tabela[mes] = pd.to_numeric(tabela[mes], errors='coerce') / 10000

    nome_mes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][mes_ano.month - 1]
    
    linha_ano = tabela[tabela['Ano'] == mes_ano.year]

    if not linha_ano.empty:
        taxa = linha_ano.iloc[0][nome_mes]
        return taxa if pd.notnull(taxa) else None
    return None

url_selic = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
id_tabela = "lstAcumulado"

if st.button("🔍 Calcular SELIC Acumulada"):
    with st.spinner('Buscando tabela SELIC acumulada e calculando...'):
        tabela_acumulada = buscar_tabela_id(url_selic, id_tabela)

        if tabela_acumulada is not None:
            taxa = processar_tabela(tabela_acumulada, data_selecionada)

            if taxa is not None:
                taxa_formatada = f"{taxa * 100:,.2f}%".replace('.', ',')
                valor_corrigido = valor_digitado * (1 + taxa)

                st.success(f"✅ Taxa SELIC acumulada em {data_selecionada.strftime('%m/%Y')}: **{taxa_formatada}**")
                st.success(f"💵 Valor corrigido: **R$ {valor_corrigido:,.2f}**")
            else:
                st.warning("⚠️ Taxa SELIC não disponível para a data selecionada.")
