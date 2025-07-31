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

        /* Estilo para o número de entrada */
        div[data-testid="stNumberInput"] label {
            font-weight: bold;
            color: white; /* MUDANÇA AQUI: Cor da label para branco */
        }

        /* Estilo para os selectboxes (mês/ano) */
        div[data-testid="stSelectbox"] label {
            font-weight: bold;
            color: white; /* MUDANÇA AQUI: Cor da label para branco */
        }

        .stButton>button {
            background-color: #003366;
            color: white;
            border-radius: 5px;
            padding: 0.5em 1em;
            width: 100%; /* Botão "Calcular" ocupa a largura total da coluna */
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

        /* Estilo para o valor corrigido em destaque */
        [data-testid="stMetric"] {
            background-color: #e0f2f7; /* Fundo azul claro */
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #003366;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            margin-top: 20px;
        }
        [data-testid="stMetric"] label {
            font-size: 1.2em !important;
            color: #003366 !important;
            font-weight: bold;
        }
        [data-testid="stMetric"] div[data-testid="stMetricValue"] {
            font-size: 2.5em !important; /* Aumenta o tamanho da fonte */
            color: #003366 !important;
            font-weight: bolder !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📈 Calculadora SELIC")
st.write("Corrige valores monetários aplicando a taxa SELIC:")

st.divider()

# --- Entrada de Dados do Usuário ---
col1, col2 = st.columns([2, 1])

with col1:
    valor_digitado = st.number_input(
        "**Valor base para o cálculo (R$):**", # O negrito aqui não afeta a cor via CSS
        min_value=0.01,
        format="%.2f",
        value=1000.00
    )

st.markdown("---")

st.markdown("### **Selecione a Data de Vencimento:**")

col_mes, col_ano = st.columns(2)

current_year = datetime.now().year
current_month = datetime.now().month

anos_disponiveis = list(range(2000, current_year + 1))
anos_disponiveis.reverse()

meses_nomes = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}
meses_selecao = list(meses_nomes.values())

with col_mes:
    mes_selecionado_nome = st.selectbox(
        "Mês:", # O negrito aqui não afeta a cor via CSS
        options=meses_selecao,
        index=current_month - 1
    )
    mes_selecionado_num = [k for k, v in meses_nomes.items() if v == mes_selecionado_nome][0]

with col_ano:
    ano_selecionado = st.selectbox(
        "Ano:", # O negrito aqui não afeta a cor via CSS
        options=anos_disponiveis,
        index=0
    )

data_selecionada = datetime(ano_selecionado, mes_selecionado_num, 1).date()

st.markdown("---")

# --- Funções de Web Scraping e Processamento de Dados ---
def buscar_tabela_por_id(url, tabela_id):
    """
    Busca uma tabela HTML por ID em uma URL e a retorna como um DataFrame Pandas.
    """
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
    
    linha_ano = tabela_df[tabela_df['Ano'] == ano_inicial]

    if linha_ano.empty:
        st.warning(f"Não foram encontrados dados para o ano {ano_inicial} na tabela mensal. Certifique-se de que o ano selecionado está presente nos dados da SELIC.")
        return 0.0, []

    dados_do_ano = linha_ano.iloc[0]

    for i in range(mes_inicial_num + 1, 13): 
        mes_nome = meses_colunas[i]
        
        # Garante que a data não seja futura em relação à data atual (2025-07-30)
        if ano_inicial == datetime.now().year and i > datetime.now().month:
            break 
        
        if mes_nome in dados_do_ano and pd.notna(dados_do_ano[mes_nome]):
            taxa_do_mes = dados_do_ano[mes_nome]
            taxa_total_somada += taxa_do_mes
        else:
            break 
            
    taxa_total_somada += 1.0 

    return taxa_total_somada, None

# --- Lógica Principal da Aplicação Streamlit ---
url_selic = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
id_tabela_mensal = "lstValoresMensais"

if st.button("Calcular"):
    with st.spinner('Buscando dados e calculando...'):
        tabela_mensal = buscar_tabela_por_id(url_selic, id_tabela_mensal)

        if tabela_mensal is not None:
            total_taxa, _ = processar_tabela_mensal_e_somar(tabela_mensal, data_selecionada)

            if total_taxa is not None and total_taxa > 0:
                valor_corrigido = valor_digitado * (1 + (total_taxa / 100))

                st.info(f"**Taxa SELIC calculada a partir de {data_selecionada.strftime('%m/%Y')}:** {total_taxa:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ','))
                
                st.metric(
                    label=f"**Valor Corrigido (R$):**",
                    value=f"R$ {valor_corrigido:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
                    delta_color="off"
                )
            else:
                st.warning(f"Não foi possível calcular. Verifique se há dados disponíveis para o ano de {data_selecionada.year} a partir do mês seguinte ao selecionado, ou se a data é muito recente/futura.")
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
