import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Calculadora SELIC Acumulada", page_icon="📈", layout="centered")

# CSS customizado para botão do LinkedIn e estilo geral
st.markdown(
    """
    <style>
        h1 { color: #003366; }

        .stButton>button {
            background-color: #003366;
            color: white;
            border-radius: 5px;
            padding: 0.5em 1em;
        }

        .footer {
            text-align: center;
            font-size: 0.9em;
            color: #888;
            margin-top: 3em;
        }

        .linkedin-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background-color: #0e76a8;
            color: white !important;
            padding: 0.5em 1em;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
            transition: background-color 0.3s;
        }

        .linkedin-btn:hover {
            background-color: #08475e;
            color: white !important;
            text-decoration: none;
        }

        .linkedin-icon {
            width: 18px;
            height: 18px;
            fill: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📈 Calculadora SELIC Acumulada")
st.write("Corrige valores monetários aplicando a taxa SELIC acumulada do mês/ano selecionado **e somando as taxas acumuladas dos meses subsequentes** até o final do ano disponível na tabela.")

st.divider()

valor_digitado = st.number_input(
    "Valor base para o cálculo (R$):",
    min_value=0.01,
    format="%.2f",
    value=1000.00
)

# Ajustado para permitir seleção de meses futuros no mesmo ano, até a data atual para garantir dados
data_limite_selecao = datetime.now().date().replace(day=1) # Sempre o primeiro dia do mês atual
if data_limite_selecao.month == 1: # Se for janeiro, não permita ir para o ano anterior
    data_min_val = datetime(2000, 1, 1).date()
else:
    # Permite selecionar até o último dia do mês anterior ao atual
    data_min_val = datetime(2000, 1, 1).date() 

data_selecionada = st.date_input(
    "Selecione o mês/ano INICIAL para o cálculo:",
    value=data_limite_selecao, # Valor padrão para o primeiro dia do mês atual
    min_value=datetime(2000, 1, 1).date(), # Começa em 2000
    max_value=data_limite_selecao # O usuário pode selecionar até o mês atual (inclusive)
)

st.divider()

def buscar_tabela_id(url, tabela_id):
    """
    Busca uma tabela HTML por ID em uma URL e a retorna como um DataFrame Pandas.
    """
    try:
        response = requests.get(url, timeout=10) # Adiciona timeout
        response.raise_for_status()  # Levanta um HTTPError para respostas de erro (4xx ou 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        tabela_html = soup.find('table', id=tabela_id)
        
        if tabela_html:
            # pd.read_html retorna uma lista de DataFrames, pegamos o primeiro [0]
            # header=0 indica que a primeira linha é o cabeçalho
            # thousands='.' e decimal=',' são importantes para ler números no formato BR
            tabela = pd.read_html(str(tabela_html), header=0, decimal=',', thousands='.')[0]
            return tabela
        else:
            st.error(f"Tabela com id '{tabela_id}' não encontrada na página.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao acessar a URL: {e}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao buscar tabela: {e}")
        return None

def processar_tabela_acumulada(tabela_df, data_inicial):
    """
    Processa a tabela de SELIC acumulada para somar as taxas do mês inicial
    e dos meses subsequentes no mesmo ano.
    """
    # Renomear colunas para acesso mais fácil (verifique o nome real da primeira e última coluna após ler com pandas)
    # Por padrão, pd.read_html com header=0 deve pegar os nomes 'Mês/Ano' e 'Taxa de Juros SELIC - Acumulados (em %)'
    # ou algo similar. É CRÍTICO verificar o DataFrame retornado por `pd.read_html` localmente.
    
    # Tentativa de renomear com base na inspeção da página
    # A tabela com ID 'lstAcumulado' geralmente tem 2 colunas: 'Mês/Ano' e a taxa.
    
    if tabela_df.shape[1] < 2:
        st.error("A estrutura da tabela acumulada é inesperada. Verifique as colunas.")
        # st.dataframe(tabela_df) # Descomente para depurar localmente
        return None, None

    # Ajusta os nomes das colunas baseado na estrutura comum da tabela de acumulados
    # `tabela_df.columns[0]` geralmente é 'Mês/Ano' e `tabela_df.columns[1]` é a taxa.
    tabela_df.columns = ['MesAno', 'TaxaAcumulada']
    
    # Converte 'TaxaAcumulada' para numérico, tratando erros
    tabela_df['TaxaAcumulada'] = pd.to_numeric(
        tabela_df['TaxaAcumulada'].astype(str).str.replace(',', '.'), 
        errors='coerce'
    )
    
    # Converte 'MesAno' para datetime
    tabela_df['MesAno_dt'] = pd.to_datetime(tabela_df['MesAno'], format='%m/%Y', errors='coerce')
    
    # Filtra linhas com datas inválidas
    tabela_df = tabela_df.dropna(subset=['MesAno_dt', 'TaxaAcumulada'])
    
    mes_inicial = data_inicial.month
    ano_inicial = data_inicial.year
    
    taxa_total_somada = 0.0
    taxas_detalhadas = []
    
    # Variável de controle: True quando encontramos o mês inicial e começamos a somar
    iniciar_soma = False

    # Itera sobre o DataFrame do mais recente para o mais antigo (ou vice-versa, dependendo da ordem da tabela)
    # Vamos ordenar para garantir que a iteração seja do mês mais antigo para o mais recente dentro do ano
    tabela_df = tabela_df.sort_values(by='MesAno_dt')

    for index, row in tabela_df.iterrows():
        mes_tabela = row['MesAno_dt'].month
        ano_tabela = row['MesAno_dt'].year
        taxa_mes = row['TaxaAcumulada']

        # Verificar se estamos no ano correto
        if ano_tabela == ano_inicial:
            # Se ainda não começamos a somar, verificar se este é o mês inicial ou posterior
            if not iniciar_soma:
                if mes_tabela >= mes_inicial:
                    iniciar_soma = True
            
            # Se já começamos a somar
            if iniciar_soma:
                taxa_total_somada += taxa_mes
                taxas_detalhadas.append(f"{row['MesAno']}: {taxa_mes:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ',')) # Formata para BR
        
        # Parar de somar se o ano da tabela ultrapassar o ano inicial (assumindo que queremos somar APENAS para o ano inicial)
        elif ano_tabela > ano_inicial and iniciar_soma:
             break # Se queremos somar apenas até o final do ano inicial
        
        # Opcional: Se a tabela for muito antiga e o ano for menor que o ano inicial, podemos parar de olhar para trás
        # elif ano_tabela < ano_inicial and not iniciar_soma:
        #    continue # Continua procurando pelo ano inicial

    return taxa_total_somada, taxas_detalhadas


url_selic = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
id_tabela_acumulada = "ctl00_contentPlaceHolder_GridView1" # ID da tabela de acumulados

if st.button("Calcular"):
    with st.spinner('Buscando dados e calculando...'):
        tabela_acumulada = buscar_tabela_id(url_selic, id_tabela_acumulada)

        if tabela_acumulada is not None:
            total_taxa, taxas_detalhadas = processar_tabela_acumulada(tabela_acumulada, data_selecionada)

            if total_taxa is not None and total_taxa > 0:
                # A taxa do site já é um percentual, por exemplo, 0.12 significa 0.12%.
                # Para usar na correção, dividimos por 100.
                valor_corrigido = valor_digitado * (1 + (total_taxa / 100))

                st.success(f"Soma das taxas SELIC acumuladas a partir de {data_selecionada.strftime('%m/%Y')}:")
                for detalhe in taxas_detalhadas:
                    st.write(f"- {detalhe}")
                st.success(f"**Total acumulado:** **{total_taxa:,.2f}%**".replace('.', '#').replace(',', '.').replace('#', ','))
                st.metric(
                    label=f"Valor corrigido a partir de {valor_digitado:,.2f}",
                    value=f"R$ {valor_corrigido:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
                    delta_color="off" # Para não mostrar seta verde/vermelha
                )
            else:
                st.warning("Não foi possível encontrar dados ou a soma das taxas é zero para a data selecionada. Verifique se o mês/ano inicial tem dados e se há meses subsequentes.")
        else:
            st.error("Falha ao carregar a tabela SELIC. Tente novamente mais tarde.")

# Rodapé com botão do LinkedIn estilizado
st.markdown(
    """
    <div class="footer">
        Desenvolvido por <strong>Tiago Trento</strong><br><br>
        <a class="linkedin-btn" href="https://www.linkedin.com/in/tiago-trento/" target="_blank">
            <svg class="linkedin-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                <path d="M100.28 448H7.4V148.9h92.88zm-46.44-340C24.35 108 0 83.66 0 53.64a53.64 53.64 0 0 1 53.64-53.64c29.92 0 53.64 24.35 53.64 53.64 0 30.02-24.35 54.36-53.64 54.36zM447.9 448h-92.68V302.4c0-34.7-12.4-58.4-43.24-58.4-23.6 0-37.6 15.8-43.8 31.1-2.2 5.3-2.8 12.7-2.8 20.1V448h-92.8s1.2-269.7 0-297.1h92.8v42.1c12.3-19 34.3-46.1 83.5-46.1 60.9 0 106.6 39.8 106.6 125.4V448z"/>
            </svg>
            Meu LinkedIn
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
