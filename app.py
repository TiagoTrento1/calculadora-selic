import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Calculadora SELIC Acumulada", layout="centered")

st.title("💰 Calculadora SELIC Acumulada")
st.markdown("Insira um valor e selecione o mês/ano para calcular o valor com a taxa SELIC acumulada do site da SEF/SC.")

# Entrada de dados
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
    url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tables = pd.read_html(response.text)
        st.info("Tabela SELIC carregada com sucesso.")
        return tables[0]
    except Exception as e:
        st.error(f"Erro ao buscar a tabela SELIC: {e}")
        return None

def normalizar_mes(mes_numero):
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    return meses[mes_numero - 1]

if st.button("Calcular SELIC"):
    selic_df = buscar_tabela_selic()
    
    if selic_df is not None:
        st.write("Pré-visualização da Tabela SELIC:")
        st.dataframe(selic_df)

        ano_procurado = data_selecionada.year
        mes_procurado = data_selecionada.month
        mes_nome = normalizar_mes(mes_procurado)

        # Confere se a primeira coluna é de ano e limpa espaços
        selic_df.iloc[:,0] = selic_df.iloc[:,0].astype(str).str.strip()

        # Filtra o ano desejado
        linha_ano = selic_df[selic_df.iloc[:,0] == str(ano_procurado)]

        if not linha_ano.empty:
            # Verifica se o mês está nas colunas
            if mes_nome in linha_ano.columns:
                taxa_selic_encontrada = linha_ano[mes_nome].values[0]

                if pd.notna(taxa_selic_encontrada):
                    taxa = float(str(taxa_selic_encontrada).replace(',', '.'))
                    resultado = valor_digitado * (taxa / 100)

                    st.success(f"**Taxa SELIC Acumulada para {mes_nome}/{ano_procurado}:** {taxa:.2f}%")
                    st.success(f"**Valor Calculado:** R$ {resultado:.2f}")
                else:
                    st.warning(f"Não há taxa registrada para {mes_nome}/{ano_procurado}.")
            else:
                st.warning(f"O mês '{mes_nome}' não foi encontrado nas colunas da tabela SELIC.")
        else:
            st.warning(f"Não foi possível encontrar o ano {ano_procurado} na tabela SELIC.")
    else:
        st.error("Não foi possível recuperar a tabela SELIC.")
