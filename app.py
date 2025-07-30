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

data_limite_selecao = datetime.now().date().replace(day=1) 

data_selecionada = st.date_input(
    "Selecione o mês/ano INICIAL para o cálculo:",
    value=data_limite_selecao,
    min_value=datetime(2000, 1, 1).date(),
    max_value=data_limite_selecao
)

st.divider()

# --- Função de busca da tabela mais robusta ---
def buscar_tabela_selic(url):
    """
    Busca a tabela de SELIC Acumulada na URL, identificando-a pelo seu cabeçalho.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontra todas as tabelas na página
        todas_tabelas = soup.find_all('table')
        
        tabela_encontrada = None
        for tabela_html in todas_tabelas:
            # Converte a tabela HTML para DataFrame
            try:
                # Tenta ler a tabela. errors='ignore' evita quebras se a tabela for inválida
                df_temp = pd.read_html(str(tabela_html), header=0, decimal=',', thousands='.', errors='ignore')
                
                if df_temp and isinstance(df_temp, list) and len(df_temp) > 0:
                    df = df_temp[0]
                    # Verifica se o DataFrame contém colunas esperadas da tabela de acumulados
                    # Os nomes podem variar ligeiramente, então verificamos se 'mês/ano' ou 'acumulado' estão em alguma coluna
                    colunas_str = [str(col).lower() for col in df.columns]
                    
                    if ('mês/ano' in ' '.join(colunas_str) or 'mes/ano' in ' '.join(colunas_str)) and \
                       ('acumulado' in ' '.join(colunas_str) or 'juros' in ' '.join(colunas_str)):
                        tabela_encontrada = df
                        break # Encontramos a tabela, saímos do loop
            except ValueError:
                # pd.read_html pode falhar se não encontrar tabelas válidas no HTML
                continue 
            except Exception as e:
                # Outros erros ao processar a tabela
                print(f"Erro ao tentar ler uma tabela: {e}") # Apenas para depuração
                continue
        
        if tabela_encontrada is not None:
            return tabela_encontrada
        else:
            st.error("Tabela de SELIC Acumulada não encontrada na página. A estrutura do site pode ter mudado.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao acessar a URL: {e}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao buscar a página: {e}")
        return None

# --- Restante das Funções (inalteradas, mas incluídas para contexto) ---

def processar_tabela_acumulada(tabela_df, data_inicial):
    """
    Processa a tabela de SELIC acumulada para somar as taxas do mês inicial
    e dos meses subsequentes no mesmo ano.
    """
    if tabela_df.shape[1] < 2:
        st.error("A estrutura da tabela acumulada é inesperada. Verifique as colunas.")
        return None, None

    # Ajusta os nomes das colunas baseado na estrutura comum da tabela de acumulados
    # Após a busca mais robusta, o nome das colunas pode variar.
    # Vamos tentar inferir a coluna de Mês/Ano e a de Taxa Acumulada.
    
    col_mes_ano = None
    col_taxa = None
    
    # Encontra a coluna de Mês/Ano (pode ser "Mês/Ano", "Mes/Ano", "Mês" + "Ano")
    for col in tabela_df.columns:
        col_lower = str(col).lower()
        if 'mês' in col_lower or 'mes' in col_lower:
            col_mes_ano = col
        if ('acumulado' in col_lower or 'selic' in col_lower) and ('%' in col_lower or 'juros' in col_lower):
            col_taxa = col
        if col_mes_ano and col_taxa: # Se ambos forem encontrados, parar
            break

    if not col_mes_ano or not col_taxa:
        st.error("Não foi possível identificar as colunas 'Mês/Ano' e 'Taxa Acumulada' na tabela lida.")
        # st.dataframe(tabela_df) # Descomente para depurar localmente e ver os nomes das colunas
        return None, None

    tabela_df_processada = tabela_df[[col_mes_ano, col_taxa]].copy()
    tabela_df_processada.columns = ['MesAno', 'TaxaAcumulada']

    # Converte 'TaxaAcumulada' para numérico, tratando erros
    tabela_df_processada['TaxaAcumulada'] = pd.to_numeric(
        tabela_df_processada['TaxaAcumulada'].astype(str).str.replace(',', '.'), 
        errors='coerce'
    )
    
    # Converte 'MesAno' para datetime
    tabela_df_processada['MesAno_dt'] = pd.to_datetime(tabela_df_processada['MesAno'], format='%m/%Y', errors='coerce')
    
    # Filtra linhas com datas inválidas
    tabela_df_processada = tabela_df_processada.dropna(subset=['MesAno_dt', 'TaxaAcumulada'])
    
    mes_inicial = data_inicial.month
    ano_inicial = data_inicial.year
    
    taxa_total_somada = 0.0
    taxas_detalhadas = []
    
    iniciar_soma = False

    # Ordena o DataFrame para garantir que a iteração seja do mês mais antigo para o mais recente
    tabela_df_processada = tabela_df_processada.sort_values(by='MesAno_dt')

    for index, row in tabela_df_processada.iterrows():
        mes_tabela = row['MesAno_dt'].month
        ano_tabela = row['MesAno_dt'].year
        taxa_mes = row['TaxaAcumulada']

        if ano_tabela == ano_inicial:
            if not iniciar_soma:
                if mes_tabela >= mes_inicial:
                    iniciar_soma = True
            
            if iniciar_soma:
                taxa_total_somada += taxa_mes
                taxas_detalhadas.append(f"{row['MesAno']}: {taxa_mes:,.2f}%".replace('.', '#').replace(',', '.').replace('#', ','))
        
        elif ano_tabela > ano_inicial and iniciar_soma:
             break # Parar de somar se o ano ultrapassar o ano inicial

    return taxa_total_somada, taxas_detalhadas


url_selic = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"

if st.button("Calcular"):
    with st.spinner('Buscando dados e calculando...'):
        tabela_acumulada = buscar_tabela_selic(url_selic) # Chama a nova função de busca

        if tabela_acumulada is not None:
            total_taxa, taxas_detalhadas = processar_tabela_acumulada(tabela_acumulada, data_selecionada)

            if total_taxa is not None and total_taxa > 0:
                valor_corrigido = valor_digitado * (1 + (total_taxa / 100))

                st.success(f"Soma das taxas SELIC acumuladas a partir de {data_selecionada.strftime('%m/%Y')}:")
                for detalhe in taxas_detalhadas:
                    st.write(f"- {detalhe}")
                st.success(f"**Total acumulado:** **{total_taxa:,.2f}%**".replace('.', '#').replace(',', '.').replace('#', ','))
                st.metric(
                    label=f"Valor corrigido a partir de {valor_digitado:,.2f}",
                    value=f"R$ {valor_corrigido:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
                    delta_color="off"
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
