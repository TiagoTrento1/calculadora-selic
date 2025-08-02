import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import base64

# --- função para converter a imagem local em base64 ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{bin_file}' não encontrado. Certifique-se de que a imagem está na mesma pasta.")
        return None

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
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}
meses_selecao = list(meses_nomes.values())

with col_mes:
    mes_selecionado_nome = st.selectbox(
        "Mês:",
        options=meses_selecao,
        index=current_month - 1 if current_month > 1 else 0
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
    meses_colunas_map = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    tabela_df.columns = ['Ano'] + list(meses_colunas_map.values())
    tabela_df['Ano'] = pd.to_numeric(tabela_df['Ano'], errors='coerce')
    tabela_df = tabela_df.dropna(subset=['Ano']).astype({'Ano': 'int'})

    for mes_nome in meses_colunas_map.values():
        tabela_df[mes_nome] = pd.to_numeric(
            tabela_df[mes_nome].astype(str).str.replace(',', '.'),
            errors='coerce'
        )

    mes_inicial_num = data_inicial.month
    ano_inicial = data_inicial.year
    taxa_total_somada = 0.0
    
    hoje = datetime.now()
    ano_atual = hoje.year

    for ano in range(ano_inicial, ano_atual + 1):
        linha_ano = tabela_df[tabela_df['Ano'] == ano]
        if linha_ano.empty:
            continue
        
        dados_do_ano = linha_ano.iloc[0]
        
        inicio_loop = mes_inicial_num + 1 if ano == ano_inicial else 1
        
        for mes_num in range(inicio_loop, 13):
            # Parar o cálculo se o ano for o atual e o mês for o mês corrente ou futuro
            if ano == ano_atual and mes_num >= hoje.month:
                break
            
            mes_nome_abreviado = meses_colunas_map[mes_num]
            if mes_nome_abreviado in dados_do_ano and pd.notna(dados_do_ano[mes_nome_abreviado]):
                taxa_do_mes = dados_do_ano[mes_nome_abreviado]
                taxa_total_somada += taxa_do_mes
            else:
                return None, f"Taxa de {meses_nomes[mes_num]}/{ano} não encontrada."
    
    taxa_total_somada += 1.0
    return taxa_total_somada, None

# --- Cálculo ---
url_selic = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
id_tabela_mensal = "lstValoresMensais"

if st.button("Calcular"):
    if not img_base64:
        st.error("Não foi possível carregar a imagem de fundo. Verifique o arquivo `latam.jpg`.")
    else:
        with st.spinner('Buscando dados e calculando...'):
            tabela_mensal = buscar_tabela_por_id(url_selic, id_tabela_mensal)
            if tabela_mensal is not None:
                total_taxa, erro_msg = processar_tabela_mensal_e_somar(tabela_mensal, data_selecionada)
                if erro_msg:
                    st.warning(erro_msg)
                elif total_taxa is not None and total_taxa > 0:
                    valor_corrigido = valor_digitado * (1 + (total_taxa / 100))

                    # Info box
                    info_html = f"""
                    <div style="
                        background: #ffffff;
                        border-left: 6px solid #0033A0;
                        padding: 14px 16px;
                        border-radius: 8px;
                        color: #1f2d3a;
                        font-weight: 600;
                        font-size: 1em;
                        margin-bottom: 8px;
                    ">
                        Taxa SELIC calculada a partir de {data_selecionada.strftime('%m/%Y')}: {total_taxa:,.2f}%
                    </div>
                    """
                    st.markdown(info_html, unsafe_allow_html=True)

                    # Resultado com label centralizado e valor maior
                    resultado_html = f"""
                    <div style="
                        background: #ffffff;
                        padding: 28px 22px;
                        border-radius: 14px;
                        border: 2px solid #0033A0;
                        box-shadow: 0 10px 24px rgba(0,0,0,0.1);
                        margin-top: 10px;
                        text-align: center;
                        max-width: 500px;
                        margin-left: auto;
                        margin-right: auto;
                    ">
                        <div style="font-size: 2.4em; font-weight: 800; color: #0033A0; margin-bottom:6px;">
                            Valor Corrigido (R$):
                        </div>
                        <div style="font-size: 6.5em; font-weight: 900; color: #D52B1E; line-height:1;">
                            R$ {valor_corrigido:,.2f}
                        </div>
                    </div>
                    """
                    st.markdown(resultado_html.replace('.', '#').replace(',', '.').replace('#', ','), unsafe_allow_html=True)
                else:
                    st.warning("Não foi possível calcular com os dados disponíveis.")
            else:
                st.error("Falha ao carregar a tabela SELIC.")
