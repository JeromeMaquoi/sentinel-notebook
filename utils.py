import pandas as pd
import networkx as nx
from sklearn.preprocessing import StandardScaler

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

def get_subgraph_with_start_node(graph: nx.DiGraph, start_node: str):
    return nx.dfs_tree(graph, source=start_node)

def sortData(data):
    return sorted(data, key=lambda x: x["allValues"], reverse=True)

def getTheFirstHighestValues(data, end=5):
    return data[:end]


# -----------------------------
# GET SPECIFIC FIELDS FROM DATA
# -----------------------------

MEASURABLE_ELEMENT = "measurableElement"
CLASS_NAME = "className"
METHOD_NAME = "methodName"
ALL_VALUES = "allValues"
COMMIT = "commit"
REPOSITORY = "repository"
REPO_NAME = "name"

# Repo data
def getRepositoryName(method):
    return method[COMMIT][REPOSITORY][REPO_NAME]

# Joular data
def getClassName(method):
    return method[MEASURABLE_ELEMENT][CLASS_NAME]

def getMethodName(method):
    return method[MEASURABLE_ELEMENT][METHOD_NAME]

def getAllJoularValues(method):
    return method[ALL_VALUES]

def getMeanOfAllJoularValues(method):
    return statistics.mean(getAllJoularValues(method))


# CK data
def getMetricName(ckData):
    return ckData["name"]

def getMetricValue(ckData):
    return ckData["value"]


# --------
# OUTLIERS
# --------
def removeOutliersByZScore(data, threshold=3):
    zScores = np.abs(stats.zscore(data))
    #zScores = np.abs((data - np.mean(data)) / np.std(data))
    """boolScore = zScores < threshold
    for i in range(len(data)):
        print(str(data[i]) + "   " + str(zScores[i]) + "  " + str(boolScore[i]))"""
    return data[zScores < threshold]

def removeOutliersByIQR(allValues):
    df = pd.DataFrame({"allValues":allValues})
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    """print("Q1 = ", Q1["allValues"])
    print("Q3 = ", Q3["allValues"])
    print("IQR = ", IQR["allValues"])
    print("Lower limit = ", Q1["allValues"] - 1.5 * IQR["allValues"])
    print("Upper limit = ", Q3["allValues"] + 1.5 * IQR["allValues"])"""
    return df[~((df < (Q1 - 1.5 * IQR))|(df > (Q3 + 1.5 * IQR))).any(axis=1)]


def matchOnlyArgsNames(matchedArgs):
    argsNames = []
    if len(matchedArgs) > 0:
        for matchedArg in matchedArgs[0].split(','):
            argName = re.sub(r'<.*?>', '', matchedArg).split('.')[-1]
            argsNames.append(argName)
    return argsNames

def simplifyMethodName(methodName):
    matches = re.findall(r'\[([^\]]+)', methodName)
    if len(matches) == 0:
        return methodName.split('/')[0] + '/'
    simplifiedArgs = matchOnlyArgsNames(matches)
    simplifiedName = methodName.split('/')[0] + '/' + str(len(simplifiedArgs)) + '[' + ','.join(simplifiedArgs) + ']'
    return simplifiedName

def getNamesXAxis(row):
    nameLegend = simplifyMethodName(row["Method"])
    return nameLegend #+ " " + row["Class"].split(".")[-1][:20]

def preprocessData(df):
    df['constructor'] = df['constructor'].astype(int)
    df['hasJavaDoc'] = df['hasJavaDoc'].astype(int)
    numericColumns = df.select_dtypes(include=['number']).columns
    X = df[numericColumns]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled

def createTsneResult(df, perplexity):
    X_scaled = preprocessData(df)
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    return tsne.fit_transform(X_scaled)