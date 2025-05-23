import subprocess
import sys
import base64

# Garantir que todas as dependências sejam instaladas antes de rodar o código
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import plotly.express as px
except ModuleNotFoundError:
    install_package("plotly")
    import plotly.express as px

import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats

st.set_page_config(page_title="Desempenho Esportivo - Ituano", layout="wide")

# Função para exibir imagem centralizada via base64
def show_image_centered(image_path, width=400):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <img src='data:image/png;base64,{encoded}' width='{width}'/>
            </div>
            """,
            unsafe_allow_html=True
        )

# Mostrar logo do Ituano centralizada
show_image_centered("ItuanoFC.png", width=400)

# Carregar CSV automaticamente
csv_path = "dados-completos-Ituano.csv"
df = pd.read_csv(csv_path)

# Abas principais
aba1, aba2, aba3 = st.tabs(["📊 Página Inicial", "⚽ Eficiência Ofensiva", "📌 Conclusões"])

with aba1:
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

with aba2:
    st.header("Eficiência Ofensiva dos Jogadores")
    st.subheader("Seleção de Ano")
    selected_year = st.selectbox("Selecione o Ano", df['ano'].unique())
    df_filtered = df[df['ano'] == selected_year]

    st.subheader("Média e Intervalo de Confiança de Gols")
    gols_jogadores = df_filtered.groupby("player_name")["statistics_goals"].sum().dropna()
    mean_gols = np.mean(gols_jogadores)
    conf_int = stats.t.interval(0.95, len(gols_jogadores)-1, loc=mean_gols, scale=stats.sem(gols_jogadores))

    st.markdown(f"**Média de gols por jogador:** {mean_gols:.2f}")
    st.markdown(f"**Intervalo de confiança (95%):** ({conf_int[0]:.2f}, {conf_int[1]:.2f})")

    st.subheader("Top 5 Artilheiros e Piores Marcadores")
    melhores = gols_jogadores.nlargest(5)
    piores = gols_jogadores.nsmallest(5)

    st.write("**Top 5 Artilheiros:**")
    st.dataframe(melhores)

    st.write("**Jogadores com Menos Gols:**")
    st.dataframe(piores)

    st.subheader("Visualizações de Dados")
    bar_fig = px.bar(melhores, x=melhores.index, y=melhores.values, title="Top 5 Artilheiros do Ituano",
                     labels={"x": "Jogador", "y": "Gols"})
    st.plotly_chart(bar_fig)

    hist_fig = px.histogram(gols_jogadores, nbins=10, title="Distribuição de Gols por Jogador")
    st.plotly_chart(hist_fig)

    st.subheader("Eficiência de Passes")
    passes_df = df_filtered[df_filtered["statistics_minutes_played"] > 0].copy()
    passes_df["pass_accuracy"] = passes_df["statistics_accurate_pass"] / passes_df["statistics_total_pass"]
    passes_df["passes_certos_por_minuto"] = passes_df["statistics_accurate_pass"] / passes_df["statistics_minutes_played"]

    top_passes = passes_df.sort_values("statistics_accurate_pass", ascending=False).head(5)
    st.markdown("**Jogadores com mais passes certos:**")
    st.dataframe(top_passes[["player_name", "statistics_accurate_pass"]])

    top_accuracy = passes_df.sort_values("pass_accuracy", ascending=False).head(5)
    st.markdown("**Melhores taxas de acerto de passe:**")
    st.dataframe(top_accuracy[["player_name", "pass_accuracy"]])

    top_por_minuto = passes_df.sort_values("passes_certos_por_minuto", ascending=False).head(5)
    st.markdown("**Passes certos por minuto jogado:**")
    st.dataframe(top_por_minuto[["player_name", "passes_certos_por_minuto"]])

    # NOVA SEÇÃO — Testes de Hipótese
    st.header("📊 Testes de Hipótese Estatística")

    # Hipótese 1: Média de gols por minuto dos Top 3 de 2022 vs 2023
    st.subheader("Comparação: Média de Gols por Minuto (Top 3 - 2022 x 2023)")

    df_gpm = df[df["statistics_minutes_played"] > 0].copy()
    df_gpm["gols_por_minuto"] = df_gpm["statistics_goals"] / df_gpm["statistics_minutes_played"]

    top_2022 = df_gpm[df_gpm["ano"] == 2022].groupby("player_name")["gols_por_minuto"].mean().nlargest(3)
    top_2023 = df_gpm[df_gpm["ano"] == 2023].groupby("player_name")["gols_por_minuto"].mean().nlargest(3)

    t_stat, p_value = stats.ttest_ind(top_2022, top_2023, equal_var=False)

    st.markdown(f"**Valor de p:** {p_value:.4f}")

    fig_box1 = px.box(df_gpm[df_gpm["ano"].isin([2022, 2023])],
                      x="ano", y="gols_por_minuto",
                      title="Distribuição de Gols por Minuto (2022 x 2023)")

    st.plotly_chart(fig_box1)

    st.markdown("""
    **Teste realizado:** Teste t para duas amostras independentes (Welch’s t-test)

    **Hipóteses**
    - **H₀:** As médias de gols por minuto dos Top 3 jogadores de 2022 e 2023 são iguais.
    - **H₁:** As médias são diferentes.

    O boxplot exibe a variação das médias de gols por minuto por jogador. O valor de p indica se a diferença entre os anos é estatisticamente significativa:
    - Se p < 0.05 → existe diferença significativa.
    - Se p ≥ 0.05 → não há diferença estatística.

    **Nível de significância adotado:** 5%.
    """)

    if p_value < 0.05:
        st.markdown("✅ Como o valor de p é menor que 0.05, **rejeitamos a hipótese nula**. Há evidências de que a média de gols por minuto dos Top 3 de 2022 é diferente da de 2023.")
    else:
        st.markdown("⚠️ Como o valor de p é maior que 0.05, **não rejeitamos a hipótese nula**. Não há evidências de diferença significativa entre as médias de gols por minuto dos Top 3 de 2022 e 2023.")

    # Justificativa de Gestão para o Primeiro Gráfico
    st.header("Como esse resultado ajuda o Ituano?")
    st.markdown("""
    O gráfico acima compara o rendimento **individual** dos principais jogadores em termos de gols por minuto, permitindo que a comissão técnica avalie **quais perfis de atletas** têm mantido ou melhorado sua performance.

    Essas informações ajudam o Ituano a:
    - Decidir sobre **renovações e contratações**.
    - Identificar **quem deve receber maior tempo de jogo**.
    - Reforçar o **planejamento tático** com base em jogadores mais eficientes.

    Basear essas decisões em **dados concretos** reduz o risco de decisões equivocadas por percepções subjetivas.
    """)

    # Hipótese 2: Proporção de jogos com pelo menos 1 gol em 2022 vs 2024
    st.subheader("Comparação: Proporção de Jogos com Pelo Menos 1 Gol (2022 x 2024)")

    df["gols_ituano"] = df.apply(lambda row: row["home_score"] if row["home_or_away"] == "Home" else row["away_score"], axis=1)
    df["fez_gol"] = df["gols_ituano"] >= 1

    df_2022 = df[df["ano"] == 2022]
    df_2024 = df[df["ano"] == 2024]

    success_2022 = df_2022["fez_gol"].sum()
    n_2022 = df_2022.shape[0]

    success_2024 = df_2024["fez_gol"].sum()
    n_2024 = df_2024.shape[0]

    p1 = success_2022 / n_2022
    p2 = success_2024 / n_2024
    p_combined = (success_2022 + success_2024) / (n_2022 + n_2024)

    z_stat = (p1 - p2) / np.sqrt(p_combined * (1 - p_combined) * (1/n_2022 + 1/n_2024))
    p_value_z = 2 * (1 - stats.norm.cdf(abs(z_stat)))

    st.markdown(f"**Estatística z:** {z_stat:.4f}")
    st.markdown(f"**Valor de p:** {p_value_z:.4f}")

    proportion_df = pd.DataFrame({
        'Ano': ['2022', '2024'],
        'Proporção de Jogos com Gol': [p1, p2]
    })

    fig_bar = px.bar(proportion_df, x='Ano', y='Proporção de Jogos com Gol',
                     title='Proporção de Jogos com Pelo Menos 1 Gol (2022 x 2024)', text_auto='.2%')

    st.plotly_chart(fig_bar)

    st.markdown("""
    **Teste realizado:** Teste de Proporção para duas amostras independentes (Z para proporção)

    **Hipóteses**
    - **H₀:** As proporções de jogos com pelo menos 1 gol em 2022 e 2024 são iguais.
    - **H₁:** As proporções são diferentes.

    O gráfico acima mostra as proporções em cada ano. O valor de p indica a significância da diferença:
    - Se p < 0.05 → existe diferença significativa.
    - Se p ≥ 0.05 → não há diferença estatística.

    **Nível de significância adotado:** 5%.
    """)

    if p_value_z < 0.05:
        st.markdown("✅ Como o valor de p é menor que 0.05, **rejeitamos a hipótese nula**. Há evidências de que o desempenho ofensivo em termos de marcar gols mudou entre 2022 e 2024.")
    else:
        st.markdown("⚠️ Como o valor de p é maior que 0.05, **não rejeitamos a hipótese nula**. Não há evidências de diferença significativa no desempenho ofensivo entre 2022 e 2024.")

    st.header("Como esse resultado ajuda o Ituano?")
    st.markdown("""
    O gráfico acima mostra a **frequência com que o Ituano consegue marcar gols por temporada**, fornecendo uma visão **coletiva do desempenho ofensivo** do time.

    Essas informações ajudam o Ituano a:
    - **Avaliar a evolução ou regressão do time** como um todo no ataque.
    - Sustentar **decisões sobre a continuidade da comissão técnica**.
    - Identificar a **necessidade de reforços ofensivos**.

    Este monitoramento permite que o clube tome **decisões estratégicas mais seguras e baseadas em dados reais**, ao invés de apenas percepções ou achismos.
    """)


with aba3:
    st.header("Conclusões Gerais da Análise")
    st.markdown("""
    Com base nos dados analisados ao longo dos anos, é possível obter uma visão mais clara do desempenho ofensivo dos jogadores do Ituano e entender como isso impacta nos resultados do time.

    ### ✅ Melhores Jogadores por Eficiência (Gols por Minuto Jogado)
    """)

    top_jogadores_ano = df[df["statistics_minutes_played"] > 0].copy()
    top_jogadores_ano["gols_por_minuto"] = top_jogadores_ano["statistics_goals"] / top_jogadores_ano["statistics_minutes_played"]

    comparacoes = []

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

        gols_min = top_ano["gols_por_minuto"].values
        media = np.mean(gols_min)
        intervalo = stats.t.interval(0.95, len(gols_min)-1, loc=media, scale=stats.sem(gols_min))
        amplitude = intervalo[1] - intervalo[0]

        comparacoes.append({
            "ano": ano,
            "media": media,
            "limite_inferior": intervalo[0],
            "limite_superior": intervalo[1],
            "amplitude": amplitude
        })

        st.markdown("**Top 3 Jogadores com Maior Eficiência Ofensiva:**")
        st.dataframe(top_ano.style.format({
            "statistics_goals": "{:.0f}",
            "statistics_minutes_played": "{:.0f}",
            "gols_por_minuto": "{:.4f}"
        }))

        st.markdown(f"**Intervalo de Confiança (95%) da média de gols por minuto:** ({intervalo[0]:.4f}, {intervalo[1]:.4f})")

        st.markdown(f"""
        Com esses dados, podemos estimar que, considerando a média de gols por minuto dos três jogadores mais eficientes de {ano}, caso cada um deles atue por 90 minutos em uma partida, o time poderia esperar algo entre **{intervalo[0]*90:.2f}** e **{intervalo[1]*90:.2f} gols por jogo** vindos desse trio. 
        Isso significa que, ao longo de várias partidas, a produção ofensiva do time, apenas com esses três atletas, tenderia a ficar dentro desse intervalo.
        """)

    # Comparação entre anos
    st.markdown("""
    ### 📊 Comparação Entre os Anos (Consistência dos Top 3 Jogadores)
    Abaixo, comparamos a **amplitude** dos intervalos de confiança de cada ano. Quanto menor a amplitude, maior a **consistência** na eficiência ofensiva entre os Top 3 do ano.
    """)

    comparacoes_df = pd.DataFrame(comparacoes).sort_values("ano")
    st.dataframe(comparacoes_df.style.format({
        "media": "{:.4f}",
        "limite_inferior": "{:.4f}",
        "limite_superior": "{:.4f}",
        "amplitude": "{:.4f}"
    }))

    # ✅ Análise de Tendência com Regressão Linear Baseada nos Jogadores Individuais
    st.markdown("""
    ### 📈 Tendência Geral da Eficiência Ofensiva (Regressão Linear)
    Aplicamos uma regressão considerando **todos os jogadores que marcaram gols**, para verificar se a eficiência do elenco tem melhorado ou caído ao longo dos anos.

    Essa abordagem permite:
    - **Detectar a consistência geral do grupo**, e não apenas de poucos destaques.
    - **Avaliar o potencial do elenco como um todo**.
    - **Planejar ajustes de elenco** com base em dados reais e históricos.
    """)

    # Preparar os dados detalhados
    jogadores_validos = top_jogadores_ano.dropna(subset=['statistics_goals']).copy()
    jogadores_validos["gols_por_minuto"] = jogadores_validos["statistics_goals"] / jogadores_validos["statistics_minutes_played"]

    # Aplicar regressão
    from sklearn.linear_model import LinearRegression
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    X_detalhado = jogadores_validos[["ano"]].values
    y_detalhado = jogadores_validos["gols_por_minuto"].values
    model_detalhado = LinearRegression().fit(X_detalhado, y_detalhado)
    tendencia_detalhada = model_detalhado.predict(X_detalhado)

    # Criar gráfico com boxplot e linha de tendência
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    sns.boxplot(x="ano", y="gols_por_minuto", data=jogadores_validos, ax=ax3)
    sns.lineplot(x=jogadores_validos["ano"], y=tendencia_detalhada, color='red', linestyle='--', label='Tendência Linear', ax=ax3)
    ax3.set_title('Tendência Geral da Eficiência Ofensiva (Todos os Jogadores que Marcaram)')
    ax3.legend()
    st.pyplot(fig3)

    st.markdown("""
    A linha vermelha no gráfico mostra a **tendência geral** de crescimento ou queda na eficiência ofensiva do Ituano. 
    Essa visão permite que o clube **não dependa apenas da intuição ou do momento atual**, mas sim de uma **análise histórica e preditiva** para suas decisões esportivas e estratégicas.
    """)

    # ✅ Interpretação dos Resultados da Regressão e Boxplot
    st.markdown("""
    **O que o gráfico revela:**
    - Apesar de alguns destaques individuais em temporadas passadas, a **tendência geral é de queda ou estagnação na eficiência ofensiva**.
    - Isso indica que o elenco, como um todo, **não tem evoluído em capacidade ofensiva**, o que pode comprometer o desempenho em campeonatos futuros.
    - O clube deve **avaliar o desempenho coletivo**, não apenas de artilheiros isolados, e considerar **reforços, treinamentos específicos ou mudanças táticas** para reverter esse cenário.
    """)


    # 📊 Expectativa de gols para 10 partidas
    st.markdown("""
    ### 🎯 Expectativa de Gols para 10 Partidas (Top 3 Jogadores de Cada Ano)
    A seguir, apresentamos a projeção de gols esperados para 10 jogos completos (90 minutos) considerando os três jogadores mais eficientes de cada temporada. O gráfico mostra o intervalo inferior, a média e o intervalo superior de gols esperados.
    """)

    comparacoes_df["gols_esperados_inferior"] = comparacoes_df["limite_inferior"] * 90 * 10
    comparacoes_df["gols_esperados_media"] = comparacoes_df["media"] * 90 * 10
    comparacoes_df["gols_esperados_superior"] = comparacoes_df["limite_superior"] * 90 * 10

    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=comparacoes_df["ano"],
        y=comparacoes_df["gols_esperados_inferior"],
        name='Mínimo Esperado (IC 95%)',
        marker_color='rgb(199, 0, 57)'
    ))

    fig.add_trace(go.Bar(
        x=comparacoes_df["ano"],
        y=comparacoes_df["gols_esperados_media"] - comparacoes_df["gols_esperados_inferior"],
        name='Esperado Médio',
        marker_color='rgb(255, 195, 0)'
    ))

    fig.add_trace(go.Bar(
        x=comparacoes_df["ano"],
        y=comparacoes_df["gols_esperados_superior"] - comparacoes_df["gols_esperados_media"],
        name='Máximo Esperado (IC 95%)',
        marker_color='rgb(144, 238, 144)'
    ))

    fig.update_layout(
        barmode='stack',
        title='Expectativa de Gols para 10 Partidas dos Top 3 Jogadores (por Ano)',
        xaxis_title='Ano',
        yaxis_title='Gols Esperados em 10 Partidas',
        template='plotly_white',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    Essa projeção oferece uma visão prática do potencial ofensivo do time ao longo de 10 partidas completas, considerando o desempenho dos 3 principais finalizadores de cada temporada. 

    Um valor médio elevado indica um setor ofensivo produtivo e consistente, enquanto amplitudes muito grandes alertam para a irregularidade ou dependência de poucos atletas para marcar gols. 

    A comissão técnica pode, por exemplo, traçar metas de gols baseadas nesses números ou identificar temporadas com menor potencial ofensivo e agir no mercado de transferências para corrigir isso.
    """)

    # ✅ Adição: Variação no Desempenho incluindo 2025
    st.markdown("""
    ### 📉 Variação no Desempenho por Ano
    - **2022**: Ano de maior destaque ofensivo, com a média de gols por jogador acima das outras temporadas. Jogadores como *Rafael Elias* e *Gabriel Barros* foram grandes protagonistas.
    - **2023**: Queda visível na produtividade ofensiva, com menos jogadores se destacando e um declínio na eficiência geral.
    - **2024**: Estagnação ofensiva, com poucos jogadores mantendo uma taxa regular de gols por minuto, o que pode indicar problemas no ataque ou esquema tático.
    - **2025**: Pequena recuperação na média, mas a **amplitude ainda alta** revela que o time segue **dependendo de poucos jogadores**, o que mantém um risco estratégico.

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
