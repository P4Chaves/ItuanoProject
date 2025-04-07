import subprocess
import sys
import base64
from io import BytesIO

# Garantir que todas as dependências sejam instaladas antes de rodar o código
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Código pra consertar deploy, evitem mexer
try:
    import plotly.express as px
except ModuleNotFoundError:
    install_package("plotly")
    import plotly.express as px

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import scipy.stats as stats

# Configuração da página
st.set_page_config(page_title="Desempenho Esportivo - Ituano", layout="wide")

# Carregar imagem em base64 e centralizar
with open("ItuanoFC.png", "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode()

st.markdown(f"""
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{img_base64}' width='400'>
    </div>
""", unsafe_allow_html=True)

# Carregar o CSV automaticamente
csv_path = "dados-completos-Ituano.csv"
df = pd.read_csv(csv_path)

# Criar abas com tamanho maior
abas = st.tabs(["📊 Página Inicial", "⚽ Eficiência Ofensiva", "🧾 Conclusões"])

# ABA 1: Introdução
with abas[0]:
    st.title("Análise de Desempenho Esportivo - Ituano")
    st.header("Descrição do Problema e Contexto do Mercado")
    st.markdown("""
    O desempenho esportivo de um clube de futebol é um fator determinante para sua competitividade, crescimento e posicionamento no cenário nacional e internacional. 

    Neste estudo, nosso **foco principal** é analisar a **performance individual dos jogadores** do Ituano ao longo dos anos. Queremos entender como cada atleta contribui para o sucesso ofensivo da equipe, identificando os jogadores mais eficientes e aqueles cujo desempenho pode estar abaixo do esperado.

    Dessa forma, vamos investigar:
    - Quais jogadores apresentam um desempenho mais consistente ao longo das temporadas?
    - Existe um padrão de artilheiros que se repete anualmente ou há muita variação?
    - O Ituano tem uma dependência excessiva de poucos jogadores para marcar gols?

    ### Evolução do Ituano ao Longo dos Anos
    Além do foco nos jogadores, também podemos observar se a equipe como um todo tem melhorado, piorado ou mantido um desempenho estável. 

    Fatores que podem influenciar essa performance incluem mudanças na escalação, novas contratações, alterações táticas e até mesmo aspectos físicos e psicológicos dos jogadores. 

    **Melhoria, Piora ou Estagnação:** Os dados irão indicar se houve um progresso contínuo ou se o time tem enfrentado dificuldades ofensivas em algumas temporadas específicas. Essa informação pode ser crucial para treinadores e gestores do clube.

    ### Perguntas Investigativas
    Com base nisso, nossa análise busca responder:
    - O Ituano tem melhorado sua performance ofensiva ao longo dos anos?
    - Os gols marcados estão distribuídos de forma equilibrada entre os jogadores ou dependem de poucos artilheiros?
    - Existe uma variação significativa no desempenho dos jogadores entre temporadas?
    - O Ituano possui jogadores consistentes que se destacam regularmente?
    - Como a equipe pode otimizar seu desempenho com base nos dados analisados?
    """)

# ABA 2: Eficiência Ofensiva
with abas[1]:
    st.header("Eficiência Ofensiva por Ano")
    st.subheader("Seleção de Ano")
    selected_year = st.selectbox("Selecione o Ano", df['ano'].unique())
    df_filtered = df[df['ano'] == selected_year]

    st.subheader("Visualização do Dataset")
    st.dataframe(df_filtered.head())

    gols_jogadores = df_filtered.groupby("player_name")["statistics_goals"].sum().dropna()
    mean_gols = np.mean(gols_jogadores)
    conf_int = stats.t.interval(0.95, len(gols_jogadores)-1, loc=mean_gols, scale=stats.sem(gols_jogadores))

    st.subheader(f"Média de gols por jogador: {mean_gols:.2f}")
    st.subheader(f"Intervalo de confiança 95%: ({conf_int[0]:.2f}, {conf_int[1]:.2f})")

    melhores = gols_jogadores.nlargest(5)
    piores = gols_jogadores.nsmallest(5)

    st.write("**Top 5 Artilheiros:**")
    st.dataframe(melhores)

    st.write("**Jogadores com Menos Gols:**")
    st.dataframe(piores)

    st.subheader("Gols por Minuto Jogado")
    df_filtered = df_filtered[df_filtered["statistics_minutes_played"] > 0].copy()
    df_filtered["gols_por_minuto"] = df_filtered["statistics_goals"] / df_filtered["statistics_minutes_played"]

    top_gpm = df_filtered.groupby("player_name")["gols_por_minuto"].mean().sort_values(ascending=False).head(5)
    st.dataframe(top_gpm)

    st.subheader("Eficiência de Passes")
    df_filtered["taxa_acerto"] = df_filtered["statistics_accurate_pass"] / df_filtered["statistics_total_pass"]
    df_filtered["passes_por_minuto"] = df_filtered["statistics_accurate_pass"] / df_filtered["statistics_minutes_played"]

    top_passes = df_filtered.groupby("player_name")["statistics_accurate_pass"].sum().sort_values(ascending=False).head(5)
    top_taxa = df_filtered.groupby("player_name")["taxa_acerto"].mean().sort_values(ascending=False).head(5)
    top_passes_minuto = df_filtered.groupby("player_name")["passes_por_minuto"].mean().sort_values(ascending=False).head(5)

    st.write("**Jogadores com mais passes certos:**")
    st.dataframe(top_passes)
    st.write("**Jogadores com maior taxa de acerto de passes:**")
    st.dataframe(top_taxa)
    st.write("**Jogadores com mais passes certos por minuto jogado:**")
    st.dataframe(top_passes_minuto)

# ABA 3: Conclusões
with abas[2]:
    st.header("Conclusões Gerais da Análise")
    st.markdown("""
    Com base nos dados analisados ao longo dos anos, é possível obter uma visão mais clara do desempenho ofensivo dos jogadores do Ituano e entender como isso impacta nos resultados do time. Abaixo, sintetizamos as principais conclusões:

    ### ✅ Melhores Jogadores por Eficiência (Gols por Minuto Jogado)
    Avaliamos os jogadores com base na métrica de gols marcados proporcionalmente aos minutos em campo. Esse indicador permite destacar atletas que, mesmo com menos tempo jogado, foram altamente produtivos.
    """)

    top_jogadores_ano = df[df["statistics_minutes_played"] > 0].copy()
    top_jogadores_ano["gols_por_minuto"] = top_jogadores_ano["statistics_goals"] / top_jogadores_ano["statistics_minutes_played"]

    for ano in sorted(top_jogadores_ano["ano"].unique()):
        st.subheader(f"Destaques de {ano}")
        ano_df = top_jogadores_ano[top_jogadores_ano["ano"] == ano]
        top_ano = (
            ano_df.groupby("player_name")[["statistics_goals", "statistics_minutes_played"]]
            .sum()
            .assign(gols_por_minuto=lambda x: x["statistics_goals"] / x["statistics_minutes_played"])
            .sort_values("gols_por_minuto", ascending=False)
            .head(3)
        )
        st.markdown("**Top 3 Jogadores com Maior Eficiência Ofensiva:**")
        st.dataframe(top_ano.style.format({
            "statistics_goals": "{:.0f}",
            "statistics_minutes_played": "{:.0f}",
            "gols_por_minuto": "{:.4f}"
        }))

    st.markdown("""
    ### 📉 Variação no Desempenho por Ano
    - **2022**: Ano de maior destaque ofensivo, com a média de gols por jogador acima das outras temporadas. Jogadores como *Rafael Elias* e *Gabriel Barros* foram grandes protagonistas.
    - **2023**: Queda visível na produtividade ofensiva, com menos jogadores se destacando e um declínio na eficiência geral.
    - **2024**: Estagnação ofensiva, com poucos jogadores mantendo uma taxa regular de gols por minuto, o que pode indicar problemas no ataque ou esquema tático.

    ### ⚠️ Dependência de Poucos Jogadores
    A análise revelou que em várias temporadas o Ituano dependeu de poucos jogadores para marcar a maior parte dos gols. Essa dependência é arriscada, especialmente em caso de lesões ou transferências.

    ### 📈 Eficiência nos Passes
    A análise de passes mostrou que:
    - Alguns jogadores não só realizaram muitos passes certos como também mantiveram alta taxa de acerto.
    - Quando ponderado por tempo em campo, foi possível identificar jogadores com alta contribuição tática, garantindo a manutenção da posse de bola e organização ofensiva.

    ### 🧠 Considerações Finais
    - Jogadores com alta taxa de **gols por minuto** e **passes certos por minuto** demonstram ser mais eficientes taticamente e tecnicamente.
    - A comissão técnica pode utilizar essas métricas para decisões mais embasadas em escalações, substituições e reforços para as próximas temporadas.
    """)