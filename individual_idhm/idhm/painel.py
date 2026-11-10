"""Tela Streamlit do IDHM (Atlas do Desenvolvimento Humano)."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from .analise import COMPONENTES, tratar_dados, calcular_estatisticas, identificar_outliers

FONTE = "https://www.undp.org/pt/brazil/idhm-uf-2010"

def mostrar():
    st.title("📚 IDHM nos estados brasileiros")
    st.write("Indicador individual: IDHM e dimensões de renda, longevidade e educação — 2010")
    st.sidebar.subheader("Filtros do IDHM")
    arquivo = st.sidebar.file_uploader("Carregar CSV ou XLSX do IDHM", type=["csv", "xlsx"], key="idhm_upload")
    try:
        if arquivo is None:
            tabela = pd.read_csv(Path(__file__).parent / "dados" / "idhm_uf_2010.csv")
            st.sidebar.caption("Base padrão: Atlas do Desenvolvimento Humano, Censo 2010")
        elif arquivo.name.lower().endswith(".csv"):
            try:
                tabela = pd.read_csv(arquivo, sep=None, engine="python")
            except UnicodeDecodeError:
                arquivo.seek(0)
                tabela = pd.read_csv(arquivo, sep=None, engine="python", encoding="latin-1")
        else:
            tabela = pd.read_excel(arquivo)
        dados = tratar_dados(tabela)
    except (ValueError, OSError, pd.errors.ParserError) as erro:
        st.error(f"Erro na leitura da base: {erro}")
        st.info("Colunas esperadas: uf, regiao, idhm_2010, idhm_renda_2010, idhm_longevidade_2010, idhm_educacao_2010")
        st.stop()
    if dados.empty:
        st.warning("A base está vazia depois do tratamento.")
        st.stop()
    componente = st.sidebar.selectbox("Indicador analisado", list(COMPONENTES))
    coluna = COMPONENTES[componente]
    regioes = st.sidebar.multiselect("Regiões", sorted(dados.regiao.unique()), default=sorted(dados.regiao.unique()), key="idhm_regioes")
    por_regiao = dados[dados.regiao.isin(regioes)]
    ufs = st.sidebar.multiselect("Estados", sorted(por_regiao.uf.unique()), default=sorted(por_regiao.uf.unique()), key="idhm_ufs")
    filtrados = por_regiao[por_regiao.uf.isin(ufs)].copy()
    if filtrados.empty:
        st.warning("Selecione pelo menos um estado.")
        st.stop()
    e = calcular_estatisticas(filtrados[coluna])
    outliers = identificar_outliers(filtrados, coluna)
    st.caption("Estatísticas das UFs selecionadas; a média simples entre estados não é o IDHM nacional.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Média", f"{e['media']:.3f}")
    c2.metric("Mediana", f"{e['mediana']:.3f}")
    c3.metric("IQR", f"{e['iqr']:.3f}")
    c4.metric("Outliers", len(outliers))
    c5, c6, c7 = st.columns(3)
    c5.metric("Desvio padrão", f"{e['desvio_padrao']:.3f}")
    c6.metric("Amplitude", f"{e['amplitude']:.3f}")
    c7.metric("UFs selecionadas", len(filtrados))
    abas = st.tabs(["Ranking", "Boxplot", "Dimensões do IDHM"])
    with abas[0]:
        fig = px.bar(filtrados.sort_values(coluna), x="uf", y=coluna, color="regiao",
                     labels={"uf": "Estado", coluna: componente, "regiao": "Região"}, title=f"Comparação entre estados — {componente}")
        st.plotly_chart(fig, use_container_width=True)
    with abas[1]:
        fig = px.box(filtrados, y=coluna, points="all", hover_name="uf",
                     labels={coluna: componente}, title="Distribuição e valores extremos")
        st.plotly_chart(fig, use_container_width=True)
    with abas[2]:
        longos = filtrados.melt(id_vars=["uf", "regiao"], value_vars=list(COMPONENTES.values())[1:],
                               var_name="dimensao", value_name="indice")
        longos["dimensao"] = longos["dimensao"].map({v:k for k,v in COMPONENTES.items()})
        fig = px.bar(longos, x="uf", y="indice", color="dimensao", barmode="group",
                     title="Renda, Longevidade e Educação por UF")
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Análise estatística")
    moda = "não há moda única" if e["moda"] is None else f"{e['moda']:.3f}"
    st.write(f"Q1: **{e['q1']:.3f}** | Q2: **{e['q2']:.3f}** | Q3: **{e['q3']:.3f}** | Moda: **{moda}**")
    st.write(f"Variância: **{e['variancia']:.5f}** | Limites dos outliers: **{e['limite_inferior']:.3f}** a **{e['limite_superior']:.3f}**")
    if outliers.empty:
        st.info("Não foram encontrados outliers no recorte selecionado.")
    else:
        st.write("Estados identificados como outliers pelo critério 1,5 × IQR:")
        st.dataframe(outliers[["uf", coluna]], hide_index=True)
    st.subheader("Interpretação para os gestores")
    maior = filtrados.loc[filtrados[coluna].idxmax()]
    menor = filtrados.loc[filtrados[coluna].idxmin()]
    st.write(f"No recorte escolhido, **{maior['uf']}** tem o maior índice ({maior[coluna]:.3f}) e **{menor['uf']}** tem o menor ({menor[coluna]:.3f}).")
    if componente == "IDHM geral":
        for uf in ["Maranhão", "Pará", "Acre", "Bahia", "Minas Gerais"]:
            tabela_uf = filtrados[filtrados.uf == uf]
            if not tabela_uf.empty:
                linha = tabela_uf.iloc[0]
                partes = {"Educação":linha.idhm_educacao_2010, "Renda":linha.idhm_renda_2010, "Longevidade":linha.idhm_longevidade_2010}
                st.write(f"Em {uf}, a menor dimensão é **{min(partes, key=partes.get)}** ({min(partes.values()):.3f}).")
        st.write("A dimensão mais baixa pode indicar onde aprofundar diagnósticos e planejar políticas públicas. Não representa, isoladamente, a causa do resultado geral.")
    if e["media"] > e["mediana"]:
        st.write("A média ficou acima da mediana, mostrando influência dos estados com valores mais altos.")
    elif e["media"] < e["mediana"]:
        st.write("A média ficou abaixo da mediana, mostrando influência dos estados com valores mais baixos.")
    st.caption("Limitação: esta base contém 2010, portanto não permite afirmar como o índice evoluiu depois. Não há dados municipais nem de investimento público nesta versão.")
    st.subheader("Dados e fonte")
    st.dataframe(filtrados, hide_index=True, use_container_width=True)
    st.download_button("Baixar dados tratados", dados.to_csv(index=False).encode("utf-8-sig"),
                       file_name="idhm_tratado.csv", mime="text/csv", key="idhm_download")
    st.markdown(f"[Fonte: PNUD — Ranking IDHM das UFs, 2010]({FONTE})")
    st.markdown("[Leitura complementar: Atlas Brasil](https://www.atlasbrasil.org.br/)")
