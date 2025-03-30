import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import scipy.stats as stats

# Configuração da página
st.set_page_config(page_title="Desempenho Esportivo - Ituano", layout="wide")

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

### Perguntas Investigativas
Com base nisso, nossa análise busca responder:
- O Ituano tem melhorado sua performance ofensiva ao longo dos anos?
- Os gols marcados estão distribuídos de forma equilibrada entre os jogadores ou dependem de poucos artilheiros?
- Existe uma variação significativa no desempenho dos jogadores entre temporadas?
- O Ituano possui jogadores consistentes que se destacam regularmente?
- Como a equipe pode otimizar seu desempenho com base nos dados analisados?

Agora, carregue o arquivo CSV contendo os dados para que possamos aprofundar essa investigação com análises estatísticas e gráficos detalhados.
""")

# Carregar os dados
uploaded_file = st.file_uploader("Carregue o arquivo CSV dos jogos", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Exibir uma amostra dos dados
    st.subheader("Visualização do Dataset")
    st.dataframe(df.head())
    
    # Identificar colunas numéricas para análise
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    
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
    st.subheader("Intervalo de Confiança - Gols por Jogador")
    gols_jogadores = df_filtered.groupby("nome_jogador")["statistics_goals"].sum().dropna()
    mean_gols = np.mean(gols_jogadores)
    conf_int = stats.t.interval(0.95, len(gols_jogadores)-1, loc=mean_gols, scale=stats.sem(gols_jogadores))
    
    st.write(f"Média de gols por jogador: {mean_gols:.2f}")
    st.write(f"Intervalo de confiança 95%: ({conf_int[0]:.2f}, {conf_int[1]:.2f})")
    
    # Melhores e piores jogadores
    st.subheader("Destaques - Melhores e Piores Jogadores")
    melhores = gols_jogadores.nlargest(5)
    piores = gols_jogadores.nsmallest(5)
    
    st.write("**Top 5 Artilheiros:**")
    st.dataframe(melhores)
    
    st.write("**Jogadores com Menos Gols:**")
    st.dataframe(piores)
    
    # Gráficos de análise
    st.subheader("Visualizações de Dados")
    
    # Gráfico de barras dos artilheiros
    bar_fig = px.bar(melhores, x=melhores.index, y=melhores.values, title="Top 5 Artilheiros do Ituano",
                     labels={"x": "Jogador", "y": "Gols"})
    st.plotly_chart(bar_fig)
    
    # Histograma de distribuição de gols por jogador
    hist_fig = px.histogram(gols_jogadores, nbins=10, title="Distribuição de Gols por Jogador")
    st.plotly_chart(hist_fig)
    
    # Conclusão e interpretação
    st.subheader("Interpretação dos Resultados")
    st.markdown("""
    - A análise de intervalos de confiança ajuda a entender a variabilidade do desempenho dos jogadores.
    - O gráfico de artilheiros destaca os jogadores com maior impacto ofensivo.
    - A distribuição de gols permite avaliar a consistência dos jogadores ao longo do tempo.
    """)
