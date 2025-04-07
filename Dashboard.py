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

        # Cálculo do intervalo de confiança
        gols_min = top_ano["gols_por_minuto"].values
        media = np.mean(gols_min)
        intervalo = stats.t.interval(0.95, len(gols_min)-1, loc=media, scale=stats.sem(gols_min))
        amplitude = intervalo[1] - intervalo[0]

        # Guarda para comparação entre os anos
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

    st.markdown("""
    Observa-se que anos com **menor amplitude** do intervalo (como 2022, por exemplo) indicam uma performance mais estável entre os melhores jogadores. Já amplitudes maiores sugerem que o time dependeu de um ou dois destaques bem acima da média dos demais, o que pode ser um risco de dependência excessiva.
    """)
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
 
 