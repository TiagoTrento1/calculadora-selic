import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import unicodedata

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

def limpar_texto(texto):
    """Remove espaços, acentos e normaliza para 3 primeiras letras capitalizadas."""
    if not isinstance(texto, str):
        texto = str(texto)
    texto = texto.strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')  # Remove acentos
    return texto[:3].capitalize()

def buscar_tabela_selic():
    """Busca a tabela SELIC acumulada do site da SEF/SC e normaliza colunas."""
    url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tables = pd.read_html(response.text)
        selic_df = tables[0]  # Supondo que a tabela desejada é a primeira
        
        # Normaliza as colunas para os 3 primeiros caracteres capitalizados, sem acento e espaços
        selic_df.columns = [limpar_texto(col) for col in selic_df.columns]
        
        st.write(f"Colunas normalizadas: {selic_df.columns.tolist()}")
        
        return selic_df
    except Exception as e:
        st.error(f"Erro ao buscar a tabela SELIC: {e}")
        return None

# --- Botão de Cálculo ---
if st.button("Calcular SELIC"):
    selic_df = buscar_tabela_selic()
    
    if selic_df is not None:
        mes_procurado = data_selecionada.month
        ano_procurado = data_selecionada.year

        # Mapeia número do mês para abreviação de 3 letras conforme tabela
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        mes_str = meses[mes_procurado - 1]

        if 'Ano' not in selic_df.columns:
            st.error("Coluna 'Ano' não encontrada na tabela SELIC.")
        elif mes_str not in selic_df.columns:
            st.error(f"O mês '{mes_str}' não foi encontrado nas colunas normalizadas da tabela SELIC.")
        else:
            # Filtra a linha do ano procurado
            linha_ano = selic_df[selic_df['Ano'] == ano_procurado]

            if linha_ano.empty:
                st.warning(f"Não foi possível encontrar o ano {ano_procurado} na tabela SELIC.")
            else:
                taxa_str = str(linha_ano.iloc[0][mes_str]).replace(',', '.').strip()
                try:
                    taxa_selic_encontrada = float(taxa_str)
                    resultado = valor_digitado * (taxa_selic_encontrada / 100)
                    st.success(f"**Taxa SELIC Acumulada ({mes_str}/{ano_procurado}):** {taxa_selic_encontrada:.2f}%")
                    st.success(f"**Valor Calculado:** R$ {resultado:.2f}")
                except ValueError:
                    st.error(f"Valor inválido para a taxa SELIC no mês {mes_str}/{ano_procurado}: '{taxa_str}'")
    else:
        st.error("Não foi possível recuperar a tabela SELIC.")
