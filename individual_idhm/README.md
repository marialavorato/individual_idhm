# Números que Falam — IDHM

**Parte individual 2 — IDHM das unidades da federação (ano 2010).**

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

O painel usa os valores oficiais do IDHM das 27 UFs, com renda, longevidade e educação. As funções de tratamento e estatística ficam em `idhm/analise.py`, e a interface Streamlit em `idhm/painel.py`.

O programa permite carregar outro CSV/XLSX com as mesmas colunas, filtrar regiões, estados e componentes, comparar no gráfico de barras, analisar o boxplot e verificar média, mediana, moda, quartis, IQR, amplitude, variância, desvio padrão e outliers.

**Fonte:** PNUD/Atlas do Desenvolvimento Humano no Brasil, dados do Censo 2010: https://www.undp.org/pt/brazil/idhm-uf-2010

**Limitação:** esse arquivo contém apenas o ano de 2010, por UF, não os municípios ou dados recentes. Não fornece investimento público e não deve ser usado para afirmar evolução temporal.

**Para apresentar:** o IDHM sintetiza longevidade, educação e renda. Comparar cada componente ajuda a identificar a menor dimensão em cada estado e a formular perguntas para gestores públicos. Valores mais baixos não demonstram, por si só, as causas das diferenças.
