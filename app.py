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
        # Usa header=3 conforme pedido
        tables = pd.read_html(response.text, header=3)
        selic_df = tables[0]

        # Ajusta o nome da primeira coluna para facilitar a busca
        selic_df.rename(columns={selic_df.columns[0]: "Ano"}, inplace=True)

        return selic_df
    except Exception as e:
        st.error(f"Erro ao buscar a tabela SELIC: {e}")
        return None

if st.button("Calcular SELIC"):
    selic_df = buscar_tabela_selic()
    if selic_df is not None:
        ano_procurado = data_selecionada.year
        mes_procurado = data_selecionada.strftime('%b')  # mês abreviado Jan, Feb, Mar, ...

        # O site está em português, então vamos mapear o mês em português:
        meses_portugues = {
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        }
        mes_procurado = meses_portugues[mes_procurado] if isinstance(mes_procurado, int) else meses_portugues[data_selecionada.month]

        # Procura a linha do ano desejado
        linha_ano = selic_df[selic_df['Ano'] == ano_procurado]

        if linha_ano.empty:
            st.warning(f"Não foi possível encontrar o ano {ano_procurado} na tabela SELIC.")
        else:
            # Pega o valor da taxa SELIC para o mês escolhido
            try:
                taxa_str = linha_ano.iloc[0][mes_procurado]
                taxa_str = str(taxa_str).replace(',', '.').strip()
                taxa_selic = float(taxa_str)

                resultado = valor_digitado * (taxa_selic / 100)

                st.success(f"**Taxa SELIC Acumulada ({mes_procurado}/{ano_procurado}):** {taxa_selic:.2f}%")
                st.success(f"**Valor Calculado:** R$ {resultado:.2f}")
            except KeyError:
                st.warning(f"O mês '{mes_procurado}' não foi encontrado nas colunas da tabela SELIC.")
            except Exception as e:
                st.error(f"Erro ao calcular a taxa SELIC: {e}")
    else:
        st.error("Não foi possível recuperar a tabela SELIC.")
