import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.title("Calculadora SELIC Acumulada (tabela pelo id)")

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

def buscar_tabela_id(url, tabela_id):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tabela_html = soup.find('table', id=tabela_id)
        if tabela_html:
            # Lê a tabela html para DataFrame, usando pandas
            tabela = pd.read_html(str(tabela_html), header=0)[0]  # header=4 conforme você indicou
            return tabela
        else:
            st.error(f"Tabela com id '{tabela_id}' não encontrada na página.")
            return None
    except Exception as e:
        st.error(f"Erro ao buscar tabela pelo id: {e}")
        return None

url_selic = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
id_tabela = "lstAcumulado"

if st.button("Carregar tabela SELIC acumulada"):
    tabela_acumulada = buscar_tabela_id(url_selic, id_tabela)
    if tabela_acumulada is not None:
        st.subheader("Tabela SELIC acumulada:")
        st.dataframe(tabela_acumulada.head(10))

        # Processar e calcular valor corrigido
        def processar_tabela(tabela, mes_ano):
            tabela.columns = ['Ano', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            tabela['Ano'] = pd.to_numeric(tabela['Ano'], errors='coerce')
            tabela = tabela.dropna(subset=['Ano'])
            tabela['Ano'] = tabela['Ano'].astype(int)

            for mes in ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']:
                tabela[mes] = pd.to_numeric(tabela[mes], errors='coerce') / 10000

            ano_procurado = mes_ano.year
            mes_procurado = mes_ano.month
            nome_mes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][mes_procurado - 1]

            linha_ano = tabela[tabela['Ano'] == ano_procurado]

            if not linha_ano.empty:
                taxa = linha_ano.iloc[0][nome_mes]
                if pd.notnull(taxa):
                    return taxa
                else:
                    st.warning(f"Taxa SELIC acumulada para {nome_mes}/{ano_procurado} não disponível.")
                    return None
            else:
                st.warning(f"Ano {ano_procurado} não encontrado na tabela.")
                return None

        taxa = processar_tabela(tabela_acumulada, data_selecionada)
        if taxa is not None:
            valor_corrigido = valor_digitado * (1 + taxa)
            taxa_formatada = f"{taxa * 100:,.2f}%".replace('.', ',')
            st.success(f"Taxa SELIC acumulada em {data_selecionada.strftime('%m/%Y')}: {taxa_formatada}")
            st.success(f"Valor corrigido: R$ {valor_corrigido:.2f}")
