import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import base64
import os

# --- função para converter a imagem local em base64 ---
# Esta versão não exibe um erro na tela, apenas ignora a imagem se não for encontrada
def get_base64_of_bin_file(bin_file):
    if not os.path.exists(bin_file):
        # Se o arquivo não existe, retorna uma string vazia para o CSS
        return ""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return ""

# --- Pega o base64 da imagem de fundo ---
# O código continua o mesmo, pois ele já trata o retorno vazio
img_base64 = get_base64_of_bin_file("background.png")
img_data_url = f"data:image/png;base64,{img_base64}" if img_base64 else ""

# --- Configuração da Página e CSS com background ---
st.set_page_config(page_title="Calculadora SELIC", page_icon="📈", layout="centered")

CHILE_CSS = f"""
<style>
    :root {{
        --brand-blue: #0033A0;
        --brand-red: #D52B1E;
        --bg: #f5f7fa;
        --surface: #ffffff;
        --text: #1f2d3a;
        --muted: #6f7a89;
        --radius: 10px;
        --shadow: 0 8px 20px rgba(0,0,0,0.08);
    }}

    /* Estilo para o background do aplicativo Streamlit */
    [data-testid="stAppViewContainer"] > .main {{
        background: 
            linear-gradient(rgba(245,247,250,0.85), rgba(245,247,250,0.85)),
            url("{img_data_url}") center/cover no-repeat;
        background-attachment: fixed;
    }}
    /* ... (restante do seu CSS permanece o mesmo) ... */
</style>
"""

st.markdown(CHILE_CSS, unsafe_allow_html=True)

# ... (resto do código do aplicativo) ...
