import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import base64
import os

# --- Configuração da Página e CSS sem background de imagem ---
st.set_page_config(page_title="Calculadora SELIC", page_icon="📈", layout="centered")

# O CSS foi simplificado, removendo a parte de background da imagem.
CHILE_CSS = """
<style>
    :root {
        --brand-blue: #0033A0;
        --brand-red: #D52B1E;
        --bg: #f5f7fa;
        --surface: #ffffff;
        --text: #1f2d3a;
        --muted: #6f7a89;
        --radius: 10px;
        --shadow: 0 8px 20px rgba(0,0,0,0.08);
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--text);
        margin: 0;
        background-color: var(--bg); /* Retorna ao background padrão */
    }
    
    /* Outros estilos específicos para Streamlit */
    [data-testid="stAppViewContainer"] > .main {
        background-color: var(--bg);
    }

    h1 {
        color: var(--brand-blue);
        text-align: center;
        margin-bottom: 10px;
        font-weight: 700;
    }

    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label,
    .stMarkdown h3 strong {
        font-weight: 600;
        color: var(--text) !important;
        font-size: 1.1em;
        margin-bottom: 5px;
    }

    .stNumberInput, .stSelectbox {
        background-color: var(--brand-blue);
        border-radius: var(--radius);
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: var(--shadow);
        position: relative;
    }

    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] input {
        color: #fff !important;
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 6px;
        padding: 10px;
        font-weight: 500;
        outline: none !important;
        box-shadow: none !important;
        caret-color: var(--brand-red) !important;
    }

    div[data-baseweb="select"] div[role="button"] {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-red) 100%);
        color: white;
        border-radius: var(--radius);
        padding: 0.85em 1.6em;
        font-size: 1.1em;
        font-weight: 700;
        width: 100%;
        border: none;
        transition: filter .25s ease, transform .15s ease;
        margin-top: 15px;
        box-shadow: 0 12px 24px rgba(213,43,30,0.35);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, var(--brand-red) 0%, var(--brand-blue) 100%);
        filter: brightness(1.05);
        cursor: pointer;
        transform: translateY(-1px);
    }
    .stButton>button:active {
        transform: translateY(1px);
    }

    div[data-testid="stAlert"] {
        border-radius: var(--radius);
        padding: 16px;
        margin-top: 15px;
        font-size: 1.05em;
        font-weight: 600;
        background-color: var(--surface);
        border-left: 6px solid var(--brand-blue);
        color: var(--text) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
        color: var(--text) !important;
    }

    [data-testid="stMetric"] {
        display: none;
    }

    .stDivider {
        margin: 12px 0;
        border-top: 2px solid rgba(0,0,0,0.08);
    }
    .stMarkdown p:last-of-type {
        margin-bottom: 8px;
    }
    .stMarkdown h3 {
        margin-top: 8px;
        margin-bottom: 8px;
        color: var(--brand-blue);
    }
</style>
"""

st.markdown(CHILE_CSS, unsafe_allow_html=True)

# --- Título e descrição ---
st.title("📈 Calculadora SELIC")
st.markdown(
    '<p style="text-align: center; font-size: 1.1em; color: black; font-weight: bold;">Corrige valores monetários aplicando a taxa SELIC</p>',
    unsafe_allow_html=True
)

# --- Entrada de valor base ---
st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <div style="width: 300px;">
    """,
    unsafe_allow_html=True
)
st.markdown(
    '<p style="text-align: center; font-size: 1.1em; color: black; font-weight: bold; margin-bottom: 5px;">Valor base para o cálculo (R$)</p>',
    unsafe_allow_html=True
)
valor_digitado = st.number_input(
    label="",
    min_value=0.01,
    format="%.2f",
    value=1000.00,
    label_visibility="collapsed"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- Seleção de data de vencimento ---
st.markdown(
    '<p style="text-align: center; font-size: 1.1em; color: black; font-weight: bold;">Selecione a Data de Vencimento</p>',
    unsafe_allow_html=True
)
col_mes, col_ano = st.columns(2)

current_year = datetime.now().year
current_month = datetime.now().month

anos_disponiveis = list(range(2000, current_year + 1))
anos_disponiveis.reverse()

meses_nomes = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}
meses_selecao = list(meses_nomes.values())

with col_mes:
    mes_selecionado_nome = st.selectbox(
        "Mês:",
        options=meses_selecao,
        index=current_month -
