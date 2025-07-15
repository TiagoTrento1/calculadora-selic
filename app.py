import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd # Para facilitar a leitura da tabela
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
    min_value=datetime(2000, 1, 1).date(), # Limite inferior razoável
    max_value=datetime.now().date() # Não permitir data futura
)

# --- Botão de Cálculo ---
if st.button("Calcular SELIC"):
    if valor_digitado is None or data_selecionada is None:
        st.error("Por favor, preencha o valor e selecione a data.")
    else:
        st.info("Buscando taxa SELIC... Isso pode levar alguns segundos.")

        try:
            # Configurar as opções do Chrome para rodar em modo headless
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox") # Necessário em alguns ambientes de nuvem/Linux
            chrome_options.add_argument("--disable-dev-shm-usage") # Otimização para ambientes Docker/Linux
            chrome_options.add_argument("--disable-gpu") # Desabilitar GPU

            # Usar webdriver_manager para gerenciar o driver
            # Em ambientes como Streamlit Community Cloud, o driver pode já estar disponível
            # ou você pode precisar de uma configuração mais específica para o PATH.
            # Para local, ChromeDriverManager() é ótimo.
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
            driver.get(url)

            # Esperar que a tabela esteja visível (ajuste o seletor se necessário)
            # Pode ser necessário usar WebDriverWait para maior robustez
            # from selenium.webdriver.support.ui import WebDriverWait
            # from selenium.webdriver.support import expected_conditions as EC
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.gridStyle")))

            # Encontrar a tabela de juros SELIC acumulados
            # Inspecione o HTML do site para encontrar o seletor exato da tabela
            # Exemplo: 'table.gridStyle' ou 'table#ctl00_contentPlaceHolder_GridView1'
            table_element = driver.find_element(By.XPATH, "//table[contains(@class, 'gridStyle')]") # Ajuste o XPath/CSS Selector

            # Extrair o HTML da tabela
            table_html = table_element.get_attribute('outerHTML')

            # Usar pandas para ler a tabela HTML (mais robusto)
            # O pandas tenta encontrar todas as tabelas e você seleciona a correta
            dfs = pd.read_html(table_html)

            # Supondo que a tabela correta seja a primeira encontrada ou uma específica
            # Você precisará verificar a estrutura da tabela no site para saber o índice correto.
            selic_df = dfs[0] # Ou dfs[1], dfs[2] dependendo de quantas tabelas existam na página.

            # Normalizar nomes das colunas e limpar dados se necessário
            # Ex: selic_df.columns = ['Mês/Ano', 'Taxa Mensal', ..., 'Acumulada']
            # Verifique as colunas reais da tabela no site!

            # Filtrar a linha correspondente ao mês e ano selecionados
            mes_procurado = data_selecionada.month
            ano_procurado = data_selecionada.year

            taxa_selic_encontrada = 0.0

            # Itere pelas linhas para encontrar o valor
            # Assumindo que a coluna de Mês/Ano é a primeira e a de Acumulada é a última (ou uma específica)
            for index, row in selic_df.iterrows():
                # Adapte os nomes das colunas conforme o `pd.read_html` as interpreta
                # Ex: 'Mês/Ano', 'Taxa de Juros SELIC - Acumulados (em %)'
                # Verifique os nomes das colunas no DataFrame `selic_df` após a leitura.
                coluna_mes_ano = row.iloc[0] # Assumindo primeira coluna é Mes/Ano (ex: "01/2024")

                if isinstance(coluna_mes_ano, str) and '/' in coluna_mes_ano:
                    m, a = map(int, coluna_mes_ano.split('/'))
                    if m == mes_procurado and a == ano_procurado:
                        # Assumindo a coluna da taxa acumulada é a última (ou índice 4/5)
                        # Verifique o nome real da coluna ou o índice no DataFrame
                        taxa_str = str(row.iloc[-1]).replace(',', '.').strip() # Última coluna, substitui ',' por '.'
                        taxa_selic_encontrada = float(taxa_str)
                        break

            if taxa_selic_encontrada > 0:
                resultado = valor_digitado * (taxa_selic_encontrada / 100)
                st.success(f"**Taxa SELIC Acumulada ({data_selecionada.strftime('%m/%Y')}):** {taxa_selic_encontrada:.2f}%")
                st.success(f"**Valor Calculado:** R$ {resultado:.2f}")
            else:
                st.warning(f"Não foi possível encontrar a taxa SELIC para {data_selecionada.strftime('%m/%Y')}.")

        except Exception as e:
            st.error(f"Ocorreu um erro ao buscar a taxa SELIC: {e}")
            st.error("Por favor, tente novamente mais tarde ou verifique os logs para detalhes.")
        finally:
            if 'driver' in locals() and driver:
                driver.quit() # Fechar o navegador ao finalizar