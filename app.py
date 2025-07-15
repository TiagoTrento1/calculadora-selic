import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Calculadora SELIC Acumulada", layout="centered")

st.title("💰 Calculadora SELIC Acumulada")
st.markdown("Insira um valor e selecione o mês/ano para calcular o valor com a taxa SELIC acumulada do site da SEF/SC.")

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

if st.button("Calcular SELIC"):
    st.info("Buscando taxa SELIC... Isso pode levar alguns segundos.")

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
        driver.get(url)

        table_element = driver.find_element(By.XPATH, "//table[contains(@class, 'gridStyle')]")
        table_html = table_element.get_attribute('outerHTML')
        selic_df = pd.read_html(table_html)[0]

        driver.quit()

        mes_procurado = data_selecionada.month
        ano_procurado = data_selecionada.year

        meses_abreviados = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                            'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        nome_mes = meses_abreviados[mes_procurado - 1]

        if not selic_df.empty:
            linha_ano = selic_df[selic_df.iloc[:, 0] == ano_procurado]

            if not linha_ano.empty and nome_mes in selic_df.columns:
                taxa_selic_encontrada = linha_ano[nome_mes].values[0]
                taxa_selic_encontrada = float(str(taxa_selic_encontrada).replace(',', '.'))

                resultado = valor_digitado * (taxa_selic_encontrada / 100)

                st.success(f"**Taxa SELIC Acumulada ({nome_mes}/{ano_procurado}):** {taxa_selic_encontrada:.2f}%")
                st.success(f"**Valor Calculado:** R$ {resultado:.2f}")
            else:
                st.warning(f"Não foi possível encontrar a taxa SELIC para {nome_mes}/{ano_procurado}.")
        else:
            st.error("Tabela SELIC não encontrada ou vazia.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao buscar a taxa SELIC: {e}")
