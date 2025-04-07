import subprocess
import sys

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

# Exibir logo do Ituano
st.image("ItuanoFC.png", width=400)

# Tabs de navegação
aba_inicial, aba_eficiencia = st.tabs(["Inicial", "Eficiência Ofensiva"])

# Carregar o CSV automaticamente sem precisar de upload
csv_path = "dados-completos-Ituano.csv"  # Certifique-se de que o arquivo está no mesmo diretório do código
df = pd.read_csv(csv_path)

with aba_inicial:
    # Título e Introdução
    st.title("Análise de Desempenho Esportivo - Ituano")

    # Análise detalhada antes do upload do CSV
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

with aba_eficiencia:
    # Exibir uma amostra dos dados
    st.subheader("Visualização do Dataset")
    st.dataframe(df.head())

    # Hipóteses e perguntas investigativas
    st.subheader("Hipóteses e Perguntas")
    st.markdown("""
    - O desempenho do Ituano melhora jogando em casa?
    - Há jogadores que se destacam consistentemente em diferentes métricas?
    - Qual a relação entre finalizações e gols marcados?
    """)

    # Filtro de seleção de ano dentro da página
    st.subheader("Seleção de Ano")
    selected_year = st.selectbox("Selecione o Ano", df['ano'].unique())
    df_filtered = df[df['ano'] == selected_year]

    # Intervalo de Confiança para estatísticas de gols por jogador
    gols_jogadores = df_filtered.groupby("player_name")["statistics_goals"].sum().dropna()
    minutos_jogados = df_filtered.groupby("player_name")["statistics_minutes_played"].sum().dropna()

    gols_por_minuto = (gols_jogadores / minutos_jogados).dropna()
    gols_por_minuto = gols_por_minuto[gols_por_minuto != np.inf]

    mean_gpm = np.mean(gols_por_minuto)
    conf_int_gpm = stats.t.interval(0.95, len(gols_por_minuto)-1, loc=mean_gpm, scale=stats.sem(gols_por_minuto))

    st.subheader(f"Média de gols por minuto jogado: {mean_gpm:.4f}")
    st.subheader(f"Intervalo de confiança 95%: ({conf_int_gpm[0]:.4f}, {conf_int_gpm[1]:.4f})")

    # Melhores e piores jogadores
    st.subheader("Destaques - Melhores e Piores Jogadores em Gols por Minuto")
    melhores = gols_por_minuto.nlargest(5)
    piores = gols_por_minuto.nsmallest(5)

    st.write("**Top 5 em Gols por Minuto:**")
    st.dataframe(melhores)

    st.write("**5 Jogadores com Menor Eficiência:**")
    st.dataframe(piores)

    # Gráficos de análise
    st.subheader("Visualizações de Dados")

    # Gráfico de barras dos mais eficientes em gols por minuto
    bar_fig_gpm = px.bar(melhores, x=melhores.index, y=melhores.values, title="Top 5 Jogadores Mais Eficientes (Gols por Minuto)",
                         labels={"x": "Jogador", "y": "Gols por Minuto"})
    st.plotly_chart(bar_fig_gpm)

    # Histograma de distribuição
    hist_fig_gpm = px.histogram(gols_por_minuto, nbins=10, title="Distribuição - Gols por Minuto")
    st.plotly_chart(hist_fig_gpm)

    # Eficiência de passes
    st.subheader("Eficiência de Passes")
    df_filtered["taxa_acerto"] = df_filtered["statistics_accurate_pass"] / df_filtered["statistics_total_pass"]
    df_filtered["passes_por_minuto"] = df_filtered["statistics_total_pass"] / df_filtered["statistics_minutes_played"]

    top_passes_certos = df_filtered.groupby("player_name")["statistics_accurate_pass"].sum().nlargest(5)
    top_taxa_acerto = df_filtered.groupby("player_name")["taxa_acerto"].mean().nlargest(5)
    top_passes_minuto = df_filtered.groupby("player_name")["passes_por_minuto"].mean().nlargest(5)

    st.write("**Top 5 Jogadores com Mais Passes Certos:**")
    st.dataframe(top_passes_certos)

    st.write("**Top 5 Jogadores com Maior Taxa de Acerto de Passes:**")
    st.dataframe(top_taxa_acerto)

    st.write("**Top 5 Jogadores com Mais Passes por Minuto:**")
    st.dataframe(top_passes_minuto)

    # Conclusão e interpretação
    st.subheader("Conclusões da Análise")
    st.markdown("""
    Com base nos dados analisados, podemos tirar algumas conclusões importantes sobre o desempenho dos jogadores do Ituano ao longo dos anos.

    - **Melhores Jogadores:** O Ituano tem alguns jogadores que consistentemente se destacam como artilheiros. Esses atletas são fundamentais para o sucesso ofensivo da equipe.

    - **Variação no Desempenho:** A análise demonstrou que 2022 foi o melhor ano para o Ituano no quesito gols e poder ofensivo, mas as seguintes temporadas mostram que seu desempenho nesse quesito só caiu.

    - **Dependência de Jogadores:** Em muitas temporadas, o Ituano depende de poucos jogadores para marcar gols, o que pode ser um risco caso esses atletas sofram lesões ou tenham uma queda de rendimento.

    - **Eficiência de Passes:** Alguns jogadores não apenas entregam muitos passes certos, mas também o fazem de forma consistente com relação ao tempo em campo. Isso demonstra inteligência tática e capacidade de manter a posse de bola.
    """)
