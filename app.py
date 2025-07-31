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
st.write("Corrige valores monetários aplicando a taxa SELIC")

st.divider()

# --- Entrada de Dados do Usuário ---
valor_digitado = st.number_input(
    "Valor base para o cálculo (R$):",
    min_value=0.01,
    format="%.2f",
    value=1000.00
)

data_limite_selecao = datetime.now().date().replace(day=1) 

data_selecionada = st.date_input(
    "Selecione a data de vencimento:",
    value=data_limite_selecao,
    min_value=datetime(2000, 1, 1).date(),
    max_value=data_limite_selecao
)

st.divider()

# --- Funções de Web Scraping e Processamento de Dados ---
def buscar_tabela_por_id(url, tabela_id):
    """
    Busca uma tabela HTML por ID em uma URL e a retorna como um DataFrame Pandas.
    """
    try:
        response = requests.get(url, timeout=10)
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

def processar_tabela_mensal_e_somar(tabela_df, data_inicial):
    """
    Processa a tabela de SELIC MENSAL, soma as taxas a partir do mês seguinte
    ao inicial e dos meses subsequentes no mesmo ano, e adiciona 1% ao total.
    """
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

    mes_inicial_num = data_inicial.month
    ano_inicial = data_inicial.year
    
    taxa_total_somada = 0.0
    taxas_detalhadas = []
    
    linha_ano = tabela_df[tabela_df['Ano'] == ano_inicial]

    if linha_ano.empty:
        st.warning(f"Não foram encontrados dados para o ano {ano_inicial} na tabela mensal.")
        return 0.0, []

    dados_do_ano = linha_ano.iloc[0]

    # --- AQUI ESTÁ A MUDANÇA: Começa a somar do mês seguinte (mes_inicial_num + 1) ---
    for i in range(mes_inicial_num + 1, 13): 
        mes_nome = meses_colunas[i]
        
        if mes_nome in dados_do_ano and pd.notna(dados_do_ano[mes_nome]):
            taxa_do_mes = dados_do_ano[mes_nome]
            taxa_total_somada += taxa_do_mes
            taxas_detalhadas.append(f"{mes_nome}/{ano_inicial}: {taxa_do_mes:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ','))
        else:
            break 
            
    # --- ADIÇÃO DO 1% AO TOTAL DAS TAXAS SOMADAS ---
    taxa_total_somada += 1.0 
    taxas_detalhadas.append("--------------------")
    taxas_detalhadas.append(f"**+ 1,00% (Adicional)**")
    # -----------------------------------------------

    return taxa_total_somada, taxas_detalhadas

# --- Lógica Principal da Aplicação Streamlit ---
url_selic = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
id_tabela_mensal = "lstValoresMensais"

if st.button("Calcular"):
    with st.spinner('Buscando dados e calculando...'):
        tabela_mensal = buscar_tabela_por_id(url_selic, id_tabela_mensal)

        if tabela_mensal is not None:
            total_taxa, taxas_detalhadas = processar_tabela_mensal_e_somar(tabela_mensal, data_selecionada)

            if total_taxa is not None and total_taxa > 0:
                valor_corrigido = valor_digitado * (1 + (total_taxa / 100))

                # Atualiza a mensagem para refletir que o cálculo começa do mês seguinte
                st.success(f"Soma das taxas SELIC mensais a partir de **{data_selecionada.strftime('%m/%Y')} (mês seguinte)** (com adicional de 1%):")
                for detalhe in taxas_detalhadas:
                    st.write(f"- {detalhe}")
                
                st.success(f"**Total das taxas:** **{total_taxa:,.2f}%**".replace('.', '#').replace(',', '.').replace('#', ','))
                
                st.metric(
                    label=f"Valor corrigido a partir de R$ {valor_digitado:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
                    value=f"R$ {valor_corrigido:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
                    delta_color="off"
                )
            else:
                st.warning(f"Não foi possível encontrar dados ou a soma das taxas é zero para o ano de {data_selecionada.year} a partir do mês seguinte ao selecionado. Verifique se há dados disponíveis.")
        else:
            st.error("Falha ao carregar a tabela SELIC. Tente novamente mais tarde.")

# --- Rodapé ---
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
