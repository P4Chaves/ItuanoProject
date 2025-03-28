import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import scipy.stats as stats

# Configuração da página
st.set_page_config(page_title="Desempenho Esportivo - Ituano", layout="wide")

# Título e Introdução
st.title("Análise de Desempenho Esportivo - Ituano")
st.markdown("""
Esta dashboard tem como objetivo analisar o desempenho esportivo dos jogadores do Ituano, 
utilizando dados de jogos para identificar padrões e insights.
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
    
    # Layout da Dashboard
    st.sidebar.header("Filtros")
    selected_year = st.sidebar.selectbox("Selecione o Ano", df['ano'].unique())
    df_filtered = df[df['ano'] == selected_year]
    
    # Intervalo de Confiança para estatísticas de gols
    st.subheader("Intervalo de Confiança - Gols Marcados")
    gols = df_filtered['home_score'].dropna()
    mean_gols = np.mean(gols)
    conf_int = stats.t.interval(0.95, len(gols)-1, loc=mean_gols, scale=stats.sem(gols))
    
    st.write(f"Média de gols: {mean_gols:.2f}")
    st.write(f"Intervalo de confiança 95%: ({conf_int[0]:.2f}, {conf_int[1]:.2f})")
    
    # Gráficos de análise
    st.subheader("Visualizações de Dados")
    
    # Gráfico de dispersão entre finalizações e gols
    if 'statistics_total_shots' in df_filtered.columns:
        scatter_fig = px.scatter(df_filtered, x='statistics_total_shots', y='home_score', 
                                 title="Relação entre Finalizações e Gols", 
                                 labels={"statistics_total_shots": "Finalizações", "home_score": "Gols"})
        st.plotly_chart(scatter_fig)
    
    # Histograma de gols marcados
    hist_fig = px.histogram(df_filtered, x='home_score', nbins=10, title="Distribuição de Gols por Jogo")
    st.plotly_chart(hist_fig)
    
    # Conclusão e interpretação
    st.subheader("Interpretação dos Resultados:")
    st.markdown("""
    - A análise de intervalos de confiança ajuda a entender a variabilidade do desempenho do time.
    - O gráfico de dispersão mostra se há relação entre finalizações e gols.
    - A distribuição de gols permite avaliar se há uma tendência nos jogos.
    """)