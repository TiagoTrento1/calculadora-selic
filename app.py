import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Calculadora SELIC Acumulada", page_icon="📈", layout="centered")

# CSS customizado para botão do LinkedIn e estilo geral
st.markdown(
    """
    <style>
        h1 { color: #003366; }

        .stButton>button {
            background-color: #003366;
            color: white;
            border-radius: 5px;
            padding: 0.5em 1em;
        }

        .footer {
            text-align: center;
            font-size: 0.9em;
            color: #888;
            margin-top: 3em;
        }

        .linkedin-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background-color: #0e76a8;
            color: white !important;
            padding: 0.5em 1em;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            transition: background-color 0.3s;
        }

        .linkedin-btn:hover {
            background-color: #08475e;
            color: white !important;
            text-decoration: none;
        }

        .linkedin-icon {
            width: 18px;
            height: 18px;
            fill: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📈 Calculadora SELIC Acumulada")
st.write("Corrija valores monetários aplicando a taxa SELIC acumulada até o mês/ano selecionado.")

st.divider()

valor_digitado = st.number_input(
    "Valor base para o cálculo (R$):",
    min_value=0.01,
    format="%.2f",
    value=1000.00
)

data_selecionada = st.date_input(
    "Selecione o mês/ano para aplicar a SELIC acumulada:",
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
            st.error(f"Tabela com id '{tabela_id}' não encontrada.")
            return None
    except Exception as e:
        st.error(f"Erro ao buscar tabela: {e}")
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

if st.button("Calcular"):
    with st.spinner('Calculando...'):
        tabela_acumulada = buscar_tabela_id(url_selic, id_tabela)

        if tabela_acumulada is not None:
            taxa = processar_tabela(tabela_acumulada, data_selecionada)

            if taxa is not None:
                taxa_formatada = f"{taxa * 100:,.2f}%".replace('.', ',')
                valor_corrigido = valor_digitado * (1 + taxa)

                st.success(f"Taxa SELIC acumulada em {data_selecionada.strftime('%m/%Y')}: **{taxa_formatada}**")
                st.success(f"Valor corrigido: **R$ {valor_corrigido:,.2f}**")
            else:
                st.warning("Taxa SELIC não disponível para a data selecionada.")

# Rodapé com botão do LinkedIn estilizado
st.markdown(
    """
    <div class="footer">
        Desenvolvido por <strong>Tiago Trento</strong><br><br>
        <a class="linkedin-btn" href="https://www.linkedin.com/in/tiago-trento/" target="_blank">
            <svg class="linkedin-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                <path d="M100.28 448H7.4V148.9h92.88zm-46.44-340C24.35 108 0 83.66 0 53.64a53.64 53.64 0 0 1 53.64-53.64c29.92 0 53.64 24.35 53.64 53.64 0 30.02-24.35 54.36-53.64 54.36zM447.9 448h-92.68V302.4c0-34.7-12.4-58.4-43.24-58.4-23.6 0-37.6 15.8-43.8 31.1-2.2 5.3-2.8 12.7-2.8 20.1V448h-92.8s1.2-269.7 0-297.1h92.8v42.1c12.3-19 34.3-46.1 83.5-46.1 60.9 0 106.6 39.8 106.6 125.4V448z"/>
            </svg>
            Meu LinkedIn
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
