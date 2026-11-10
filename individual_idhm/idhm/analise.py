"""Tratamento de dados e cálculos estatísticos para o IDHM por UF (2010)."""
import numpy as np
import pandas as pd

COLUNAS = ["uf", "regiao", "idhm_2010", "idhm_renda_2010", "idhm_longevidade_2010", "idhm_educacao_2010"]
COMPONENTES = {
    "IDHM geral": "idhm_2010",
    "Renda": "idhm_renda_2010",
    "Longevidade": "idhm_longevidade_2010",
    "Educação": "idhm_educacao_2010",
}

def tratar_dados(tabela):
    dados = tabela.copy()
    dados.columns = dados.columns.str.strip().str.lower()
    ausentes = [c for c in COLUNAS if c not in dados.columns]
    if ausentes:
        raise ValueError("Colunas ausentes: " + ", ".join(ausentes))
    dados = dados[COLUNAS].copy()
    for c in ["uf", "regiao"]:
        dados[c] = dados[c].astype("string").str.strip()
    for c in COLUNAS[2:]:
        dados[c] = pd.to_numeric(dados[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    dados = dados.dropna(subset=COLUNAS).drop_duplicates(subset="uf")
    dados = dados[dados[COLUNAS[2:]].ge(0).all(axis=1) & dados[COLUNAS[2:]].le(1).all(axis=1)]
    return dados.reset_index(drop=True)

def calcular_estatisticas(valores):
    serie = pd.to_numeric(pd.Series(valores), errors="coerce").dropna()
    if serie.empty:
        raise ValueError("Nenhum valor numérico disponível")
    q1, q2, q3 = np.percentile(serie, [25, 50, 75])
    iqr = q3 - q1
    modas = serie.mode()
    return {
        "media": float(serie.mean()), "mediana": float(q2),
        "moda": None if len(modas) == len(serie) else float(modas.iloc[0]),
        "q1": float(q1), "q2": float(q2), "q3": float(q3),
        "iqr": float(iqr), "amplitude": float(serie.max()-serie.min()),
        "variancia": float(serie.var(ddof=0)), "desvio_padrao": float(serie.std(ddof=0)),
        "limite_inferior": float(q1-1.5*iqr), "limite_superior": float(q3+1.5*iqr),
    }

def identificar_outliers(dados, coluna):
    e = calcular_estatisticas(dados[coluna])
    return dados[(dados[coluna] < e["limite_inferior"]) | (dados[coluna] > e["limite_superior"])].copy()
