import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_base64 = get_base64_of_bin_file("latam.jpg")

st.set_page_config(page_title="Calculadora SELIC", page_icon="📈", layout="centered")

CHILE_CSS = f"""
<style>
    /* CSS igual do código anterior, mantém o mesmo estilo */
</style>
"""

st.markdown(CHILE_CSS, unsafe_allow_html=True)

st.title("📈 Calculadora SELIC")
st.markdown(
    '<p style="text-align: center; font-size: 1.1em; color: white; font-weight: bold;">Corrige valores monetários aplicando a taxa SELIC</p>',
    unsafe_allow_html=True
)

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
    7: 'Julho', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
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
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
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

    ano_inicial = data_inicial.year
    mes_inicial_num = data_inicial.month

    taxa_total_somada = 0.0
    ano_mais_recente = tabela_df['Ano'].max()

    ano_atual = ano_inicial
    mes_atual = mes_inicial_num + 1

    while True:
        if ano_atual > ano_mais_recente:
            break

        linha_ano = tabela_df[tabela_df['Ano'] == ano_atual]
        if linha_ano.empty:
            break

        dados_do_ano = linha_ano.iloc[0]

        if mes_atual > 12:
            mes_atual = 1
            ano_atual += 1
            continue

        mes_nome = meses_colunas[mes_atual]

        hoje = datetime.now()
        if ano_atual == hoje.year and mes_atual > hoje.month:
            break

        valor_taxa = dados_do_ano.get(mes_nome, None)
        if pd.isna(valor_taxa):
            break

        taxa_total_somada += valor_taxa

        mes_atual += 1

    taxa_total_somada += 1.0

    return taxa_total_somada, None

url_selic = 'https://www3.bcb.gov.br/selic/serie/port/tabelaSelic'
id_tabela_mensal = 'lstValoresMensais'  # id atualizado conforme sua indicação

if st.button("Calcular"):
    with st.spinner('Buscando dados e calculando...'):
        tabela_mensal = buscar_tabela_por_id(url_selic, id_tabela_mensal)
        if tabela_mensal is not None:
            total_taxa, _ = processar_tabela_mensal_e_somar(tabela_mensal, data_selecionada)
            if total_taxa is not None and total_taxa > 0:
                valor_corrigido = valor_digitado * (1 + (total_taxa / 100))

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
