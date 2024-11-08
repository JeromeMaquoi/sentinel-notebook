""" import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import utils
from sklearn.manifold import TSNE
import plotly.graph_objects as go

METHOD_DF = "Method"
CLASS_DF = "Class"
JOULAR_VALUES_DF = "JoularValues"
MEAN_JOULAR_VALUES_DF = "MeanJoularValue"
REPO_DF = "Repository"

def createBoxplotJoular(repositoryName, methodName, allValues):
    df = pd.DataFrame({"allValues":allValues})
    fig = px.box(df, y="allValues", title="Joular values for " + methodName + " of repository " +repositoryName, points="outliers")
    fig.show()

def plot_call_graph_from_node(graph: nx.DiGraph, start_node: str):
    subgraph = nx.dfs_tree(graph, source=start_node)
    pos = nx.spring_layout(subgraph)
    nx.draw(subgraph, pos)
    plt.show()

def createViolinJoular(data, granularity="Repository", points="all"):
    dataAllRepositories = []
    for doc in data:
        dataAllRepositories.extend({"Repository": doc["commit"]["repository"]["name"], "Values":val, "Class": doc["measurableElement"]["className"]} for val in doc["allValues"])
    df = pd.DataFrame(dataAllRepositories)

    figRepository = px.violin(df, y="Values", x=granularity, points=points)
    figRepository.show()

def createMultipleBoxplot(dataOneRepo):
    dataframePreparation = []
    for method in dataOneRepo:
        dataframePreparation.append({"Method": method["measurableElement"]["methodSignature"], "Values":method["allValues"], "Class":method["measurableElement"]["className"]})
    df = pd.DataFrame(dataframePreparation)
    print(df)
    fig = px.box(df, x="Method", y="Values", points="outliers")
    fig.show()

def createBarChart(dataframe, xAxisName, yAxisName, title):
    fig = px.bar(dataframe, x=xAxisName, y=yAxisName, title=title)
    fig.update_layout(yaxis_range=[0, 40])
    return fig

def createSubplot(fig1, fig2, title):
    fig1Traces = []
    fig2Traces = []
    for trace in range(len(fig1["data"])):
        fig1Traces.append(fig1["data"][trace])
    for trace in range(len(fig2["data"])):
        fig2Traces.append(fig2["data"][trace])

    
    figure = make_subplots(rows=1, cols=2, subplot_titles=("Joular values", "Ck values"))
    for traces in fig1Traces:
        figure.append_trace(traces, row=1, col=1)
    for traces in fig2Traces:
        figure.append_trace(traces, row=1, col=2)

    figure.update_layout(title_text=title)
    figure.show()

def createBoxplot(dataframe, title):
    return px.box(dataframe, y="value", title=title, points="all")




def createBoxplotBarchartFigure(df, ckMetric, repository):    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for index, row in df.iterrows():
        showLegend = False
        if index == 1:
            showLegend = True
        nameBar = utils.getNamesXAxis(row)

        # Box plot
        boxTrace = go.Box(
            #x=[getNamesXAxis(row)],
            y=row[JOULAR_VALUES_DF],
            name=nameBar,
            marker=dict(color='rgb(252,141,98)'),
            legendgroup="boxplots",
            showlegend=showLegend
        )
        fig.add_trace(boxTrace, secondary_y=True)

        # Bar chart
        xBarChart = [nameBar]
        yBarChart = [row[ckMetric]]
        traceBarchart = go.Bar(x=xBarChart, y=yBarChart, name=ckMetric, marker=dict(color='rgb(141,160,203)'), legendgroup="barcharts", showlegend=showLegend)
        fig.add_trace(traceBarchart)

    # Trendline for the bar chart
    overallTrendline = np.polyfit(np.arange(len(df)), df[ckMetric], 1)
    overallSlope = overallTrendline[0]
    overallTrendlineValues = np.polyval(overallTrendline, np.arange(len(df)))
    traceTrendline = go.Scatter(x=[f"{getNamesXAxis(row)}" for _, row in df.iterrows()], y=overallTrendlineValues, name=f'Trendline for {ckMetric} (Slope: {overallSlope:.2f})', mode="lines", line=dict(color='red'))
    #fig.add_trace(traceTrendline)
        
    fig['layout'].update(legend=dict(traceorder='normal'))
    fig['layout'].update(title= "Energy consumption of 3 methods for project Spoon", height=500)
    fig.update_yaxes(title_text="Energy consumption (J)")
    fig.show()

def createScatterPlot(df, ckMetric, repoName):
    fig = go.Figure()
    scatterTrace = go.Scatter(
        x=df[ckMetric],
        y=df[MEAN_JOULAR_VALUES_DF],
        mode="markers",
        text=[f"{getNamesXAxis(row)}" for _, row in df.iterrows()]
    )
    fig.add_trace(scatterTrace)

    # Update layout
    fig.update_layout(
        title=f"{ckMetric} and mean of Joular values, for each method of repository \"{repoName}\"",
        xaxis_title=ckMetric,
        yaxis_title="Mean of Joular Values"
    )

    fig.show()

def createTsneFigure(df, coloredFeature, perplexity=30):
    X_tsne = utils.createTsneResult(df, perplexity)
    hover_data = {'Method': df[METHOD_DF], 'Class': df[CLASS_DF], 'Repository': df[REPO_DF]}

    fig = px.scatter(
        X_tsne, x=0, y=1,
        hover_data=hover_data,
        color=df[coloredFeature], labels={'color':coloredFeature}
    )
    fig.show() """