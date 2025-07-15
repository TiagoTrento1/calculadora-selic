import streamlit as st
import pandas as pd
import requests

def buscar_tabela_selic():
    url = "https://sat.sef.sc.gov.br/tax.net/tax.Net.CtacteSelic/TabelasSelic.aspx"
    try:
        response = requests.get(url)
        response.raise_for_status()
        tables = pd.read_html(response.text, header=3)

        # A tabela acumulada geralmente está no índice 2 (confirme no seu caso)
        df = tables[2]

        df.columns = ['Ano', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').astype(int)
        for mes in ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']:
            df[mes] = pd.to_numeric(df[mes], errors='coerce') / 100

        return df

    except Exception as e:
        st.error(f"Erro ao buscar ou processar a tabela SELIC: {e}")
        return None

def main():
    st.title("Correção Monetária com SELIC Acumulada")

    df_selic = buscar_tabela_selic()
    if df_selic is None:
        st.stop()

    anos = df_selic['Ano'].dropna().astype(int).tolist()
    ano_escolhido = st.selectbox("Ano", anos)

    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    mes_escolhido = st.selectbox("Mês", meses)

    valor_original = st.number_input("Valor Original (R$)", min_value=0.0, format="%.2f")

    if st.button("Calcular Valor Corrigido"):
        taxa = df_selic.loc[df_selic['Ano'] == ano_escolhido, mes_escolhido].values
        if len(taxa) == 0 or pd.isna(taxa[0]):
            st.error("Taxa SELIC para esse período não encontrada.")
        else:
            taxa = taxa[0]
            valor_corrigido = valor_original * (1 + taxa)
            st.write(f"Taxa acumulada até {mes_escolhido}/{ano_escolhido}: {taxa*100:.2f}%")
            st.write(f"Valor corrigido: R$ {valor_corrigido:.2f}")

    with st.expander("Tabela SELIC Acumulada"):
        st.dataframe(df_selic.style.format("{:.4f}"))

if __name__ == "__main__":
    main()
