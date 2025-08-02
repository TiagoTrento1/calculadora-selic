import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- Configuração da Página e Estilos CSS da LATAM ---
st.set_page_config(page_title="Calculadora SELIC", page_icon="📈", layout="centered")

LATAM_CSS = """
<style>
    :root {
        --latam-dark: #00306b;
        --latam-primary: #e20674;
        --latam-accent: #00a1e4;
        --latam-bg: #f5f7fa;
        --latam-surface: #ffffff;
        --latam-text: #1f2d3a;
        --latam-muted: #6f7a89;
        --radius: 10px;
        --shadow: 0 8px 20px rgba(0,0,0,0.08);
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--latam-text);
        background: var(--latam-bg);
        margin: 0;
    }

    h1 {
        color: var(--latam-dark);
        text-align: center;
        margin-bottom: 10px;
        font-weight: 700;
    }

    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label,
    .stMarkdown h3 strong {
        font-weight: 600;
        color: var(--latam-surface) !important;
        font-size: 1.1em;
        margin-bottom: 5px;
    }

    .stNumberInput, .stSelectbox {
        background-color: var(--latam-dark);
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
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 6px;
        padding: 10px;
        font-weight: 500;
        outline: none !important;
        box-shadow: none !important;
        caret-color: var(--latam-accent) !important;
    }

    div[data-baseweb="select"] div[role="button"] {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, var(--latam-primary) 0%, var(--latam-accent) 100%);
        color: white;
        border-radius: var(--radius);
        padding: 0.85em 1.6em;
        font-size: 1.1em;
        font-weight: 700;
        width: 100%;
        border: none;
        transition: filter .25s ease, transform .15s ease;
        margin-top: 15px;
        box-shadow: 0 12px 24px rgba(226,6,116,0.35);
    }
    .stButton>button:hover {
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
        background-color: var(--latam-surface);
        border-left: 6px solid var(--latam-primary);
        color: var(--latam-text);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
        color: inherit !important;
    }

    [data-testid="stMetric"] {
        background: #f0f8ff;
        padding: 22px;
        border-radius: 14px;
        border: 2px solid var(--latam-accent);
        box-shadow: var(--shadow);
        margin-top: 22px;
        text-align: center;
    }
    [data-testid="stMetric"] label {
        font-size: 1.4em !important;
        color: var(--latam-dark) !important;
        font-weight: 700;
        margin-bottom: 8px;
    }
    [data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 3.5em !important;
        color: var(--latam-primary) !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.08);
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
        color: var(--latam-dark);
    }

    .footer {
        text-align: center;
        font-size: 0.9em;
        color: var(--latam-muted);
        margin-top: 3em;
        padding: 24px 0;
        border-top: 1px solid rgba(0,0,0,0.05);
        background: var(--latam-surface);
        border-radius: 6px;
    }

    .linkedin-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: var(--latam-dark);
        color: white !important;
        padding: 0.6em 1.2em;
        border: none;
        border-radius: 5px;
        text-decoration: none;
        font-weight: 600;
        transition: filter .2s ease;
    }
    .linkedin-btn:hover {
        filter: brightness(1.1);
        text-decoration: none;
    }
    .linkedin-icon {
        width: 20px;
        height: 20px;
        fill: white;
    }

    @media (max-width: 768px) {
        h1 { font-size: 2em; }
        .stNumberInput, .stSelectbox { padding: 12px; margin-bottom: 8px; }
        .stButton>button { padding: 0.65em 1em; font-size: 1em; margin-top: 12px; }
        div[data-testid="stColumns"] { flex-direction: column; }
        div[data-testid="stColumns"] > div { width: 100% !important; }
        [data-testid="stMetric"] { padding: 16px; margin-top: 16px; }
        [data-testid="stMetric"] label { font-size: 1.1em !important; }
        [data-testid="stMetric"] div[data-testid="stMetricValue"] { font-size: 2.8em !important; }
        .stMarkdown h3 { margin-top: 5px; margin-bottom: 5px; }
        .stMarkdown p:last-of-type { margin-bottom: 5px; }
    }
    @media (max-width: 480px) {
        h1 { font-size: 1.8em; }
        .stNumberInput input, .stSelectbox div[data-baseweb="select"] input { font-size: 0.9em; }
        [data-testid="stMetric"] div[data-testid="stMetricValue"] { font-size: 2.2em !important; }
    }
</style>
"""

st.markdown(LATAM_CSS, unsafe_allow_html=True)

# --- Título e descrição ---
st.title("📈 Calculadora SELIC")
st.markdown(
    '<p style="text-align: center; font-size: 1.1em; color: white; font-weight: bold;">Corrige valores monetários aplicando a taxa SELIC</p>',
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
    '<p style="text-align: center; font-size: 1.1em; color: white; font-weight: bold; margin-bottom: 5px;">Valor base para o cálculo (R$)</p>',
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
    '<p style="text-align: center; font-size: 1.1em; color: white; font-weight: bold;">Selecione a Data de Vencimento</p>',
    unsafe_allow_html=True
)
col_mes, col_ano = st.columns(2)

current_year = datetime.now().year
current_month = datetime.now().month

anos_disponiveis = list(range(2000, current_year + 1))
anos_disponiveis.reverse()

meses_nomes = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Mai', 6: 'Junho',
    7: 'Julho', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Novembro', 12: 'Dezembro'
}
meses_selecao = list(meses_nomes.values())

with col_mes:
    mes_selecionado_nome = st.selectbox(
        "Mês:",
        options=meses_selecao,
        index=current_month - 1
    )
    mes_selecionado_num = [k for k, v in meses_nomes.items() if v == mes_selecionado_nome][0]

with col_ano:
    ano_selecionado = st.selectbox(
        "Ano:",
        options=anos_disponiveis,
        index=0
    )

data_selecionada = datetime(ano_selecionado, mes_selecionado_num, 1).date()

# --- Funções auxiliares ---
def buscar_tabela_por_id(url, tabela_id):
    """
    Busca uma tabela HTML por ID em uma URL e a retorna como um DataFrame Pandas.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tabela_html = soup.find('table', id=tabela_id)

        if tabela_html:
            tabela = pd.read_html(str(tabela_html), header=0, decimal=',', thousands='.')[0]
            return tabela
        else:
            st.error(f"Tabela com id '{tabela_id}' não encontrada na página. Verifique o ID no site.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao acessar a URL: {e}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao buscar tabela: {e}")
        return None

def processar_tabela_mensal_e_somar(tabela_df, data_inicial):
    """
    Processa a tabela de SELIC MENSAL, soma as taxas a partir do mês seguinte
    ao inicial e dos meses subsequentes no mesmo ano, e adiciona 1% ao total.
    """
    meses_colunas = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Novembro', 12: 'Dezembro'
    }

    colunas_esperadas = ['Ano'] + list(meses_colunas.values())

    if tabela_df.shape[1] < len(colunas_esperadas):
        st.error("A estrutura da tabela mensal é inesperada. Verifique as colunas.")
        return None, None

    tabela_df.columns = colunas_esperadas

    tabela_df['Ano'] = pd.to_numeric(tabela_df['Ano'], errors='coerce')
    tabela_df = tabela_df.dropna(subset=['Ano']).astype({'Ano': 'int'})

    for mes_nome in meses_colunas.values():
        tabela_df[mes_nome] = pd.to_numeric(
            tabela_df[mes_nome].astype(str).str.replace(',', '.'),
            errors='coerce'
        )

    mes_inicial_num = data_inicial.month
    ano_inicial = data_inicial.year

    taxa_total_somada = 0.0

    linha_ano = tabela_df[tabela_df['Ano'] == ano_inicial]

    if linha_ano.empty:
        st.warning(f"Não foram encontrados dados para o ano {ano_inicial} na tabela mensal. Certifique-se de que o ano selecionado está presente nos dados da SELIC.")
        return 0.0, []

    dados_do_ano = linha_ano.iloc[0]

    for i in range(mes_inicial_num + 1, 13):
        mes_nome = meses_colunas[i]

        # Garante que a data não seja futura em relação à data atual do servidor
        if ano_inicial == datetime.now().year and i > datetime.now().month:
            break

        if mes_nome in dados_do_ano and pd.notna(dados_do_ano[mes_nome]):
            taxa_do_mes = dados_do_ano[mes_nome]
            taxa_total_somada += taxa_do_mes
        else:
            break

    taxa_total_somada += 1.0

    return taxa_total_somada, None

# --- Lógica de cálculo ---
url_selic = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
id_tabela_mensal = "lstValoresMensais"

if st.button("Calcular"):
    with st.spinner('Buscando dados e calculando...'):
        tabela_mensal = buscar_tabela_por_id(url_selic, id_tabela_mensal)

        if tabela_mensal is not None:
            total_taxa, _ = processar_tabela_mensal_e_somar(tabela_mensal, data_selecionada)

            if total_taxa is not None and total_taxa > 0:
                valor_corrigido = valor_digitado * (1 + (total_taxa / 100))

                st.info(f"**Taxa SELIC calculada a partir de {data_selecionada.strftime('%m/%Y')}:** {total_taxa:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ','))
                
                st.metric(
                    label=f"**Valor Corrigido (R$):**",
                    value=f"R$ {valor_corrigido:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
                    delta_color="off"
                )
            else:
                st.warning(f"Não foi possível calcular. Verifique se há dados disponíveis para o ano de {data_selecionada.year} a partir do mês seguinte ao selecionado, ou se a data é muito recente/futura.")
        else:
            st.error("Falha ao carregar a tabela SELIC. Tente novamente mais tarde.")

# --- Rodapé ---
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
