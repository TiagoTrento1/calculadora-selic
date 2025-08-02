import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import base64

# --- função para converter a imagem local em base64 ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- pega o base64 da imagem latam.jpg (deve estar na mesma pasta) ---
img_base64 = get_base64_of_bin_file("latam.jpg")

# --- Configuração da Página e CSS com background do avião LATAM ---
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

    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: var(--text);
        margin: 0;
        background: 
            linear-gradient(rgba(245,247,250,0.85), rgba(245,247,250,0.85)),
            url("data:image/jpg;base64,{img_base64}") center/cover no-repeat;
        background-attachment: fixed;
    }}

    h1 {{
        color: var(--brand-blue);
        text-align: center;
        margin-bottom: 10px;
        font-weight: 700;
    }}

    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label,
    .stMarkdown h3 strong {{
        font-weight: 600;
        color: var(--surface) !important;
        font-size: 1.1em;
        margin-bottom: 5px;
    }}

    .stNumberInput, .stSelectbox {{
        background-color: var(--brand-blue);
        border-radius: var(--radius);
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: var(--shadow);
        position: relative;
    }}

    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] input {{
        color: #fff !important;
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 6px;
        padding: 10px;
        font-weight: 500;
        outline: none !important;
        box-shadow: none !important;
        caret-color: var(--brand-red) !important;
    }}

    div[data-baseweb="select"] div[role="button"] {{
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }}

    .stButton>button {{
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
    }}
    .stButton>button:hover {{
        background: linear-gradient(135deg, var(--brand-red) 0%, var(--brand-blue) 100%);
        filter: brightness(1.05);
        cursor: pointer;
        transform: translateY(-1px);
    }}
    .stButton>button:active {{
        transform: translateY(1px);
    }}

    div[data-testid="stAlert"] {{
        border-radius: var(--radius);
        padding: 16px;
        margin-top: 15px;
        font-size: 1.05em;
        font-weight: 600;
        background-color: var(--surface);
        border-left: 6px solid var(--brand-blue);
        color: var(--text) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }}
    div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {{
        color: var(--text) !important;
    }}

    [data-testid="stMetric"] {{
        display: none;
    }}

    .stDivider {{
        margin: 12px 0;
        border-top: 2px solid rgba(0,0,0,0.08);
    }}
    .stMarkdown p:last-of-type {{
        margin-bottom: 8px;
    }}
    .stMarkdown h3 {{
        margin-top: 8px;
        margin-bottom: 8px;
        color: var(--brand-blue);
    }}
</style>
"""

st.markdown(CHILE_CSS, unsafe_allow_html=True)

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

    ano_selecionado = data_inicial.year
    mes_selecionado = data_inicial.month
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month

    taxa_total_somada = 0.0

    # Se for ano atual, somar do mês seguinte até mês atual
    if ano_selecionado == ano_atual:
        linha_ano = tabela_df[tabela_df['Ano'] == ano_atual]
        if linha_ano.empty:
            st.warning(f"Não foram encontrados dados para o ano {ano_atual}.")
            return 0.0, []
        linha_ano = linha_ano.iloc[0]

        mes_inicial = mes_selecionado + 1
        if mes_inicial > mes_atual:
            return 1.0, None  # Nenhuma taxa a somar (mês selecionado no futuro)

        for m in range(mes_inicial, mes_atual + 1):
            mes_nome = meses_colunas[m]
            if pd.notna(linha_ano[mes_nome]):
                taxa_total_somada += linha_ano[mes_nome]

    # Se for ano anterior, soma da taxa de dezembro daquele ano em diante até última taxa disponível
    elif ano_selecionado < ano_atual:
        anos_disponiveis = sorted(tabela_df['Ano'].unique())
        anos_pos_selecao = [ano for ano in anos_disponiveis if ano >= ano_selecionado]

        # Somar dezembro do ano selecionado
        linha_ano = tabela_df[tabela_df['Ano'] == ano_selecionado]
        if linha_ano.empty:
            st.warning(f"Não foram encontrados dados para o ano {ano_selecionado}.")
            return 0.0, []
        linha_ano = linha_ano.iloc[0]
        if pd.notna(linha_ano['Dezembro']):
            taxa_total_somada += linha_ano['Dezembro']

        # Somar meses de anos seguintes até faltar dado
        for ano in anos_pos_selecao[1:]:
            linha = tabela_df[tabela_df['Ano'] == ano]
            if linha.empty:
                continue
            linha = linha.iloc[0]
            for mes in range(1, 13):
                mes_nome = meses_colunas[mes]
                if pd.notna(linha[mes_nome]):
                    taxa_total_somada += linha[mes_nome]
                else:
                    # Para de somar se faltar dado (último mês disponível)
                    return taxa_total_somada + 1.0, None

    else:
        # Ano futuro selecionado - não aplica correção
        return 1.0, None

    return taxa_total_somada + 1.0, None

def corrigir_valor(valor_inicial, data_vencimento):
    # URL e IDs da tabela (ajuste se necessário)
    url = "https://www3.bcb.gov.br/selic/"
    tabela_id = "tabelaMensalSelic"  # ajustar para o ID correto da tabela mensal no site do BCB

    tabela_mensal = buscar_tabela_por_id(url, tabela_id)
    if tabela_mensal is None:
        return None

    fator_correção, _ = processar_tabela_mensal_e_somar(tabela_mensal, data_vencimento)

    if fator_correção is None:
        st.warning("Não foi possível calcular o fator de correção.")
        return None

    valor_corrigido = valor_inicial * fator_correção
    return valor_corrigido

# --- Botão para calcular ---
if st.button("Calcular Valor Corrigido"):
    valor_corrigido = corrigir_valor(valor_digitado, data_selecionada)
    if valor_corrigido is not None:
        st.success(f"Valor corrigido pela taxa SELIC: R$ {valor_corrigido:,.2f}")
    else:
        st.error("Não foi possível calcular o valor corrigido.")

