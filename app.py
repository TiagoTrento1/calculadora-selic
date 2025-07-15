import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait # Adicionar para esperar elementos
from selenium.webdriver.support import expected_conditions as EC # Adicionar para esperar elementos

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

# --- Botão de Cálculo ---
if st.button("Calcular SELIC"):
    if valor_digitado is None or data_selecionada is None:
        st.error("Por favor, preencha o valor e selecione a data.")
    else:
        st.info("Buscando taxa SELIC... Isso pode levar alguns segundos.")

        driver = None # Inicializa driver como None
        try:
            # Configurar as opções do Chrome para rodar em modo headless no Streamlit Cloud
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # *** SOLUÇÃO CHAVE AQUI ***
            # Aponta diretamente para o executável do Chromium no ambiente do Streamlit Cloud.
            # O Chromedriver geralmente "acompanha" o Chromium ou é encontrado se este for especificado.
            chrome_options.binary_location = "/usr/bin/chromium-browser" 
            
            # Tentar iniciar o driver sem especificar o service.executable_path explicitamente no Service()
            # Se o binary_location for definido, o Selenium muitas vezes infere o driver.
            # ou, podemos passar o service_log_path para depuração.
            
            # A forma mais direta e que geralmente funciona para ambientes como o Streamlit Cloud
            # é omitir o Service() e passar o executable_path diretamente nas options do Chrome.
            # No entanto, com as versões mais recentes do Selenium, usar o Service é o padrão.
            # Vamos tentar a combinação de Service com o caminho do Chromedriver e o binary_location para Chromium.

            # O erro "Unable to obtain driver" pode ocorrer se o Chromedriver não estiver em /usr/bin/chromedriver.
            # No Streamlit Cloud, o Chromedriver pode estar em /usr/local/bin/chromedriver ou ser gerenciado de outra forma.
            # A forma mais robusta é usar o `executable_path` dentro das `options` para o Chromedriver
            # E o `binary_location` para o Chromium.

            # Tentativa 1: Especificar o driver via Service (o que fizemos antes)
            # service = Service("/usr/bin/chromedriver") # O erro pode estar aqui se o Chromedriver não estiver EXATAMENTE nesse local
            # driver = webdriver.Chrome(service=service, options=chrome_options)

            # Tentativa 2 (MAIS ROBUSTA): Tentar sem `webdriver_manager` e sem um `Service` explícito para o driver,
            # deixando o Selenium inferir, ou especificar o caminho do driver nas opções.
            # Como você já está sem webdriver_manager, vamos tentar uma abordagem mais direta.
            
            # Vamos tentar passar o caminho do chromedriver diretamente nas opções para compatibilidade
            # com ambientes onde o driver e o binário do browser podem estar em locais diferentes ou
            # o Service() não está inferindo corretamente.
            
            # ATENÇÃO: Se /usr/bin/chromedriver ainda não funcionar, teremos que investigar os logs
            # do Streamlit Community Cloud para ver onde o chromedriver está de fato.
            # Para o Streamlit Community Cloud, a forma mais resiliente é usar apenas o `binary_location`
            # e deixar o Selenium tentar encontrar o driver automaticamente, ou usar uma abordagem como
            # `selenium-wire` que pode ter seu próprio Chromedriver embutido para ambientes Docker.
            
            # No entanto, para persistir com a abordagem atual, vamos tentar o seguinte:
            # Adicionar o caminho do chromedriver diretamente nas opções, pois o Service pode estar
            # buscando de um PATH diferente.
            
            # A forma mais recomendada agora é instanciar o Service e passar o caminho do chromedriver.
            # Se "/usr/bin/chromedriver" não funcionar, o driver pode estar em "/usr/local/bin/chromedriver"
            # ou o Streamlit Cloud tem um caminho de driver diferente.
            
            # Vamos garantir que a importação de Service esteja correta, o que já está.
            # E que a instância de Service esteja no lugar certo, o que também já está.
            
            # O erro "Unable to obtain driver for chrome" sugere que o Selenium NÃO CONSEGUE SEQUER INICIAR
            # o chromedriver no PATH que você deu.
            # Isso é quase sempre um problema de PERMISSÕES ou o EXECUTÁVEL NÃO EXISTE NO CAMINHO.
            
            # Vamos forçar o caminho do CHROMEDRIVER e também do BINÁRIO do CHROME.
            # O Streamlit Community Cloud tem um comportamento específico para isso.
            # Tente esta combinação, que costuma resolver:

            # Definir o caminho para o executável do Chromedriver no ambiente do Streamlit Cloud
            # Este é o caminho padrão onde o Chromedriver costuma estar em sistemas Linux/Docker
            # e onde o Streamlit Community Cloud o coloca.
            CHROMEDRIVER_PATH = "/usr/bin/chromedriver" 
            
            # Definir o caminho para o binário do Chromium/Chrome no ambiente do Streamlit Cloud
            # Este é o navegador que o Chromedriver vai controlar.
            CHROME_BINARY_PATH = "/usr/bin/chromium-browser" # Este é o mais comum no Streamlit Cloud

            chrome_options.binary_location = CHROME_BINARY_PATH
            
            # A partir do Selenium 4.6+, a forma recomendada de especificar o driver é via Service.
            # O erro "Unable to obtain driver" vem se o Service NÃO consegue achar o driver nesse caminho.
            # Isso geralmente significa que o arquivo NÃO EXISTE OU NÃO TEM PERMISSÃO DE EXECUÇÃO.
            
            # Vamos garantir que o service seja criado com o caminho correto.
            service = Service(CHROMEDRIVER_PATH) 
            
            # Tente também adicionar argumentos para logs do Chromedriver, pode ajudar na depuração
            # service.service_args = ['--verbose', '--log-path=/tmp/chromedriver.log'] # Útil para depurar

            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Aumentar o tempo de espera implícita para garantir que elementos carreguem
            driver.implicitly_wait(10) # Espera até 10 segundos para encontrar elementos

            url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
            driver.get(url)

            # Usar WebDriverWait para esperar a tabela carregar, é mais robusto que implicitly_wait para elementos específicos
            # O seletor abaixo é um PALPITE. Você DEVE inspecionar o site e verificar o seletor da tabela exata!
            wait = WebDriverWait(driver, 20) # Espera até 20 segundos
            table_element = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'gridStyle')]")))

            # Extrair o HTML da tabela
            table_html = table_element.get_attribute('outerHTML')

            # Usar pandas para ler a tabela HTML (mais robusto)
            # O pandas tenta encontrar todas as tabelas e você seleciona a correta
            dfs = pd.read_html(table_html)
            
            # Supondo que a tabela correta seja a primeira encontrada ou uma específica
            # Você precisará verificar a estrutura da tabela no site para saber o índice correto.
            selic_df = dfs[0] # Ou dfs[1], dfs[2] dependendo de quantas tabelas existam na página.

            # ... (o resto do seu código para filtrar e calcular) ...
            
            # Para fins de depuração, mostre o DataFrame completo
            # st.write("DataFrame da SELIC carregado:")
            # st.dataframe(selic_df)


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
                        # Adicione um tratamento de erro para a conversão de float
                        try:
                            taxa_str = str(row.iloc[-1]).replace(',', '.').strip() # Última coluna, substitui ',' por '.'
                            taxa_selic_encontrada = float(taxa_str)
                        except ValueError:
                            st.warning(f"Não foi possível converter a taxa '{taxa_str}' para número na linha {index}. Pulando.")
                            continue # Pula para a próxima linha
                        break
            
            if taxa_selic_encontrada > 0:
                resultado = valor_digitado * (taxa_selic_encontrada / 100)
                st.success(f"**Taxa SELIC Acumulada ({data_selecionada.strftime('%m/%Y')}):** {taxa_selic_encontrada:.2f}%")
                st.success(f"**Valor Calculado:** R$ {resultado:.2f}")
            else:
                st.warning(f"Não foi possível encontrar a taxa SELIC para {data_selecionada.strftime('%m/%Y')}.")

        except Exception as e:
            st.error(f"Ocorreu um erro ao buscar a taxa SELIC: {e}")
            st.error("Verifique os detalhes do erro nos logs do Streamlit Cloud.")
            # st.exception(e) # Para exibir o traceback completo no Streamlit app (útil para depuração)
        finally:
            if driver:
                driver.quit() # Fechar o navegador ao finalizar
