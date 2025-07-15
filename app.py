import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Calculadora SELIC Acumulada", layout="centered")

st.title("💰 Calculadora SELIC Acumulada")
st.markdown("Insira um valor e selecione o mês/ano para calcular o valor com a taxa SELIC acumulada do site da SEF/SC.")

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

def buscar_tabela_selic():
    """Busca a tabela SELIC acumulada do site da SEF/SC"""
    url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tables = pd.read_html(response.text)
        return tables[0]  # Supondo que a tabela desejada é a primeira
    except Exception as e:
        st.error(f"Erro ao buscar a tabela SELIC: {e}")
        return None

# --- Botão para mostrar as colunas e primeiras linhas da tabela ---
if st.button("Ver colunas da tabela SELIC"):
    dados = buscar_tabela_selic()
    if dados is not None:
        st.write("Colunas da tabela:", dados.columns.tolist())
        st.write("Primeiras linhas da tabela:", dados.head())
    else:
        st.error("Não foi possível recuperar a tabela SELIC.")

# --- Botão de Cálculo ---
if st.button("Calcular SELIC"):
    selic_df = buscar_tabela_selic()
    
    if selic_df is not None:
        # Mostrar para debug (pode comentar depois)
        # st.write(selic_df.head())

        mes_procurado = data_selecionada.month
        ano_procurado = data_selecionada.year

        # A tabela vem com 'Ano/Mês' na primeira coluna, meses como colunas à direita
        # Vamos extrair o valor da taxa SELIC para o ano e mês escolhidos

        # Ajuste: a primeira coluna contém os anos, as outras as taxas por mês (abreviações)

        # Colunas de meses provavelmente em inglês ou abreviadas (Jan, Feb, Mar, Apr, May, Jun,...)
        # Precisamos mapear o mês selecionado para o nome da coluna correspondente
        
        # Mapeamento de número do mês para abreviação que aparece na tabela
        meses_abrev = {
            1: "Jan",
            2: "Fev",
            3: "Mar",
            4: "Abr",
            5: "Mai",
            6: "Jun",
            7: "Jul",
            8: "Ago",
            9: "Set",
            10: "Out",
            11: "Nov",
            12: "Dez"
        }

        # Normalizar nomes das colunas para remover espaços e padronizar
        selic_df.columns = selic_df.columns.str.strip()

        if 'Ano/Mês' not in selic_df.columns:
            st.error("Coluna 'Ano/Mês' não encontrada na tabela SELIC.")
        else:
            try:
                # Filtrar linha do ano selecionado
                linha_ano = selic_df[selic_df['Ano/Mês'] == ano_procurado]

                if linha_ano.empty:
                    st.warning(f"Ano {ano_procurado} não encontrado na tabela SELIC.")
                else:
                    mes_coluna = meses_abrev.get(mes_procurado)
                    if mes_coluna not in selic_df.columns:
                        st.warning(f"Mês '{mes_coluna}' não encontrado nas colunas da tabela SELIC.")
                    else:
                        taxa_str = linha_ano.iloc[0][mes_coluna]
                        if pd.isna(taxa_str):
                            st.warning(f"Taxa SELIC para {mes_coluna}/{ano_procurado} não está disponível.")
                        else:
                            # Converter taxa para float, tratando vírgula
                            taxa_selic_encontrada = float(str(taxa_str).replace(',', '.'))

                            resultado = valor_digitado * (taxa_selic_encontrada / 100)
                            st.success(f"**Taxa SELIC Acumulada ({mes_coluna}/{ano_procurado}):** {taxa_selic_encontrada:.2f}%")
                            st.success(f"**Valor Calculado:** R$ {resultado:.2f}")

            except Exception as e:
                st.error(f"Erro ao processar a tabela SELIC: {e}")

    else:
        st.error("Não foi possível recuperar a tabela SELIC.")
