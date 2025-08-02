import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- Configuração da Página e Estilos CSS ---
st.set_page_config(page_title="Calculadora SELIC", page_icon="📈", layout="centered")

st.markdown(
    """
    <style>
        /* (seu CSS existente aqui...) */
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📈 Calculadora SELIC")
st.markdown(
    '<p style="text-align: center; font-size: 1.1em; color: white; font-weight: bold;">Corrige valores monetários aplicando a taxa SELIC</p>',
    unsafe_allow_html=True
)

st.divider()

# --- Entrada de Dados do Usuário ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    valor_digitado = st.number_input(
        "**Valor base para o cálculo (R$):**",
        min_value=0.01,
        format="%.2f",
        value=1000.00
    )

st.divider()

st.markdown(
    '<p style="text-align: center; font-size: 1.1em; color: white; font-weight: bold;">Selecione a Data de Vencimento:</p>',
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

st.divider()

# --- Funções de Web Scraping e Processamento de Dados ---
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
            st.error(f"Tabela com id '{tabela_id}' não encontrada na página.")
            return None
    except Exception as e:
        st.error(f"Erro ao buscar a tabela SELIC: {e}")
        return None

def processar_tabela_mensal_e_somar(tabela_df, data_inicial):
    meses_colunas = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dezembro'
    }
    colunas_esperadas = ['Ano'] + list(meses_colunas.values())
    if tabela_df.shape[1] < len(colunas_esperadas):
        st.error("Estrutura da tabela mensal inesperada.")
        return None, None

    tabela_df.columns = colunas_esperadas
    tabela_df['Ano'] = pd.to_numeric(tabela_df['Ano'], errors='coerce').dropna().astype(int)
    for mes_nome in meses_colunas.values():
        tabela_df[mes_nome] = pd.to_numeric(
            tabela_df[mes_nome].astype(str).str.replace(',', '.'),
            errors='coerce'
        )

    mes_inicial_num = data_inicial.month
    ano_inicial = data_inicial.year
    taxa_total = 0.0

    linha_ano = tabela_df[tabela_df['Ano'] == ano_inicial]
    if linha_ano.empty:
        st.warning(f"Não foram encontrados dados para o ano {ano_inicial}.")
        return 0.0, []

    dados_do_ano = linha_ano.iloc[0]
    for i in range(mes_inicial_num + 1, 13):
        if ano_inicial == datetime.now().year and i > datetime.now().month:
            break
        mes_nome = meses_colunas[i]
        if pd.notna(dados_do_ano.get(mes_nome)):
            taxa_total += dados_do_ano[mes_nome]
        else:
            break

    taxa_total += 1.0
    return taxa_total, None

# --- Lógica Principal ---
url_selic = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
id_tabela_mensal = "lstValoresMensais"

if st.button("Calcular"):
    with st.spinner('Buscando dados e calculando...'):
        tabela = buscar_tabela_por_id(url_selic, id_tabela_mensal)
        if tabela is not None:
            total_taxa, _ = processar_tabela_mensal_e_somar(tabela, data_selecionada)
            if total_taxa is not None and total_taxa > 0:
                valor_corrigido = valor_digitado * (1 + (total_taxa / 100))
                st.info(f"**Taxa SELIC calculada a partir de {data_selecionada.strftime('%m/%Y')}:** {total_taxa:,.2f}%")
                st.metric(
                    label=f"**Valor Corrigido (R$):**",
                    value=f"R$ {valor_corrigido:,.2f}",
                    delta_color="off"
                )
            else:
                st.warning("Não foi possível calcular a SELIC.")
        else:
            st.error("Falha ao carregar a tabela SELIC.")

# --- Rodapé ---
st.markdown(
    """
    <div class="footer">
        Desenvolvido por <strong>Tiago Trento</strong><br><br>
        <a class="linkedin-btn" href="https://www.linkedin.com/in/tiago-trento/" target="_blank">
            Meu LinkedIn
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
