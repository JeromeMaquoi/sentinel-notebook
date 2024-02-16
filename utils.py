import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def main():
    pass

if __name__ == "__main__":
    main()

def exportDataframeToFile(df : pd.DataFrame, filePath : str):
    df.to_csv(filePath, index=False)

def exportDiGraphToCsv(graph : nx.DiGraph, filePath : str):
    nx.write_edgelist(graph, filePath, delimiter=",")

def export_graph_with_headers(graph: nx.DiGraph, filePath: str, delimiter:str = ','):
    with open(filePath, 'w') as f:
        f.write("Source,Target,Type\n")
        for edge in graph.edges():
            f.write(delimiter.join(map(str, edge)) + "\n")

def plot_call_graph_from_node(graph: nx.DiGraph, start_node: str):
    subgraph = nx.dfs_tree(graph, source=start_node)
    pos = nx.spring_layout(subgraph)
    nx.draw(subgraph, pos)
    plt.show()

def get_subgraph_with_start_node(graph: nx.DiGraph, start_node: str):
    return nx.dfs_tree(graph, source=start_node)