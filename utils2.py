import pandas as pd
import json
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import copy
from scipy.stats import shapiro
import statistics
import plotly.express as px

def main():
    pass

if __name__ == "__main__":
    main()


def read_json_file(file_path:str):
    json_data = []
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file]
        json_str = '[' + ','.join(lines) + ']'
        print(json_str)
        json_data = json.loads(json_str)

    return pd.DataFrame(json_data)

def get_all_data_from_one_repo(repo_name:str, min_nb_values:int, excluded_words:str=" ", excluded_first_ancestor_class:str=" "):
    all_data = aggregate_joular_node_entity_by_value(repo_name=repo_name, min_nb_values=min_nb_values, excluded_words=excluded_words, excluded_first_ancestor_class=excluded_first_ancestor_class)
    all_data_without_outliers = removeOutliers(all_data)
    return removeNonNormalData(all_data_without_outliers)


# ------------------------------------
# DATABASE DATA FETCHING / AGGREGATION
# ------------------------------------

def aggregate_joular_node_entity_by_value(repo_name:str, min_nb_values:int, excluded_words:str=" ", excluded_first_ancestor_class:str=" "):
    print("-------------------------------------")
    print("Aggregation of the JoularNodeEntities")
    print("-------------------------------------")
    client = MongoClient('mongodb://localhost:27017/')
    cursor = client['sentinelBackend']['joular_node_entity'].aggregate([
        {
            '$match': {
                'commit.repository.name': repo_name,
                'measurableElement.className':{
                    '$not': {
                        '$regex': excluded_words
                    }
                }
            }
        }, {
            '$group': {
                '_id': {
                    'measurableElement': '$measurableElement', 
                    'lineNumber': '$lineNumber', 
                    'hasValue': {
                        '$cond': {
                            'if': {
                                '$ifNull': [
                                    '$value', False
                                ]
                            }, 
                            'then': True, 
                            'else': False
                        }
                    }, 
                    'iteration': '$iteration', 
                    'sizeAncestors': {
                        '$size': '$ancestors'
                    }
                }, 
                'valuesForOneIteration': {
                    '$push': '$value'
                }, 
                'ancestors': {
                    '$first': '$ancestors'
                }, 
                'parent': {
                    '$first': '$parent'
                }, 
                'iteration': {
                    '$first': '$iteration'
                },
                'id': {
                    '$first': '$_id'
                }
            }
        }, {
            '$addFields': {
                'nbValuesForOneIteration': {
                    '$size': '$valuesForOneIteration'
                }
            }
        }, {
            '$match': {
                'nbValuesForOneIteration': {
                    '$lte': 1
                }
            }
        }, {
            '$group': {
                '_id': {
                    'measurableElement': '$_id.measurableElement', 
                    'lineNumber': '$_id.lineNumber', 
                    'hasValue': '$_id.hasValue', 
                    'sizeAncestors': '$_id.sizeAncestors'
                }, 
                'allIterations': {
                    '$addToSet': '$_id.iteration'
                }, 
                'values': {
                    '$push': {
                        '$arrayElemAt': [
                            '$valuesForOneIteration', 0
                        ]
                    }
                }, 
                'iteration': {
                    '$first': '$iteration'
                }, 
                'ancestors': {
                    '$first': '$ancestors'
                }, 
                'parent': {
                    '$first': '$parent'
                },
                'id': {
                    '$first': '$id'
                }
            }
        }, {
            '$addFields': {
                'nbIterations': {
                    '$size': '$allIterations'
                }, 
                'nbValues': {
                    '$size': '$values'
                }
            }
        }, {
            '$project': {
                '_id': 0, 
                'allIterations': 1, 
                'iteration': 1, 
                'values': 1, 
                'lineNumber': '$_id.lineNumber', 
                'measurableElement': '$_id.measurableElement', 
                'commit': '$_id.commit', 
                'ancestors': '$ancestors', 
                'parent': '$parent', 
                'nbValues': '$nbValues', 
                'nbIterations': '$nbIterations',
                'id':1
            }
        }, {
            '$match': {
                'nbValues': {
                    '$gte': min_nb_values
                }
            }
        }, {
            '$lookup': {
                'from': 'joular_node_entity',
                'let': {
                    'firstAncestorId': {
                        '$arrayElemAt': ['$ancestors', 0]
                    }
                },
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$eq': ['$_id', '$$firstAncestorId']
                            }
                        }
                    },
                    {
                        '$project': {
                            'measurableElement.className': 1
                        }
                    }
                ],
                'as': 'firstAncestor'
            }
        }, {
            '$unwind': '$firstAncestor'
        }, {
            '$match': {
                'firstAncestor.measurableElement.className': {
                    '$not': {
                        '$regex': excluded_first_ancestor_class
                    }
                }
            }
        }
    ])
    result = [doc for doc in cursor]
    print(f'Number of documents : {len(result)}')
    print()
    return result

def get_call_trace_from_joular_node_entity_id(id:str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['sentinelBackend']
    collection = db['joular_node_entity']

    call_trace = []

    doc = collection.find_one({"_id":id})
    if (doc["ancestors"] != []):
        ancestor_ids = doc["ancestors"]
        cursor = collection.find({"_id": {"$in":ancestor_ids}},{"_id":1, "measurableElement.classMethodSignature":1, "lineNumber":1, "measurableElement.className":1, "measurableElement.methodName":1})
        ancestors = sort_entities_by_id_list(doc["ancestors"], cursor)
        for ancestor in ancestors:
            call_trace.append(ancestor)
            print(f'{ancestor["measurableElement"]["classMethodSignature"]} {ancestor["lineNumber"]}')
    else:
        print("There are no ancestors :/")
    call_trace.append(doc)
    print(doc["measurableElement"]["classMethodSignature"] + " " + str(doc["lineNumber"]))
    print()
    return call_trace

def get_ck_metric_from_joular_node_entity(repo_name:str, class_name:str, method_name:str, name:str="fanout"):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['sentinelBackend']
    collection = db['ck_entity']
    doc = collection.find_one({"commit.repository.name":repo_name, "measurableElement.className":class_name, "measurableElement.methodName":method_name, "name":name})
    
    if doc == None:
        return 0
    return doc["value"]


def get_sum_fanout_of_call_trace(repo_name:str, call_trace):
    sum_fanout = 0
    for item in call_trace:
        class_name = item["measurableElement"]["className"]
        method_name = item["measurableElement"]["methodName"]
        fanout = get_ck_metric_from_joular_node_entity(repo_name=repo_name, class_name=class_name, method_name=method_name, name="fanout")
        sum_fanout += fanout

    return sum_fanout



# -------------
# LISTS METHODS
# -------------

def sort_entities_by_id_list(id_list:list, cursor):
    """
    The ancestors of one entity are sorted from the most distant ancestor to the closest one. The first element of the list will be the farthest ancestor and the last element will be the direct parent.
    """
    documents_by_id = {doc['_id']: doc for doc in cursor}
    return [documents_by_id[id] for id in id_list if id in documents_by_id]

def create_dataframe_metric_energy(all_normal_data_without_outliers, repo_name:str):
    data = []

    for item in all_normal_data_without_outliers:
        median = statistics.median(item["values"])
        call_trace = get_call_trace_from_joular_node_entity_id(item["id"])
        sum_fanout = get_sum_fanout_of_call_trace(repo_name, call_trace)

        data.append({
            'energy_consumption_median': median,
            'fanout':sum_fanout,
            'identifier': item["measurableElement"]["methodName"]
        })
    return pd.DataFrame(data)

# --------------------------------
# OUTLIERS AND NORMAL DISTRIBUTION
# --------------------------------

def removeOutliers(data):
    print("---------------")
    print("Remove outliers")
    print("---------------")
    only25ValuesAndMore = []
    for methodData in data:
        methodDataCopy = copy.deepcopy(methodData)
        allValues = methodDataCopy["values"]
        #allValuesAfterStd = removeOutliersByStd(allValues)
        allValuesAfterOutlierRemoval = removeOutliersByZScore(allValues)
        if (len(allValuesAfterOutlierRemoval) >= 25):
            methodDataCopy["values"] = allValuesAfterOutlierRemoval
            only25ValuesAndMore.append(methodDataCopy)
    print("Len without outliers (with at least 25 values) : ", len(only25ValuesAndMore))
    print()
    return only25ValuesAndMore

def removeOutliersByStd(allValues):
    mean = np.mean(allValues)
    stdDev = np.std(allValues)
    return [x for x in allValues if (np.abs(mean - x) <= 3 * stdDev)]

def removeOutliersByZScore(allValues, threshold=3):
    allValues = np.array(allValues)
    zScores = np.abs(stats.zscore(allValues))
    #zScores = np.abs((data - np.mean(data)) / np.std(data))
    """boolScore = zScores < threshold
    for i in range(len(allValues)):
        print(str(allValues[i]) + "   " + str(zScores[i]) + "  " + str(boolScore[i]))"""
    return allValues[zScores < threshold].tolist()

def removeNonNormalData(data:list):
    print("-----------------")
    print("Shapiro-Wilk test")
    print("-----------------")
    normal_data = []
    for document in data:
        values = document["values"]
        stat, p = shapiro(values)
        if (p > 0.05):
            normal_data.append(document)
    print("Number of normal distributions : ", len(normal_data))
    print()
    return normal_data

def filter_highest_data(data, means, highest_percentage=25):
    quantile = np.percentile(means, np.abs(100-highest_percentage))
    return [d for d,mean in zip(data, means) if mean >= quantile]

def filter_lowest_data(data, means, lowest_percentage=10):
    quantile = np.percentile(means, lowest_percentage)
    return [d for d,mean in zip(data, means) if mean <= quantile]

def mean_dict(data):
    return [np.mean(d["values"]) for d in data]

def get_median(data:list):
    return statistics.median(data)

# ----
# PLOT
# ----

def scatter_plot(df:pd.DataFrame):
    fig = px.scatter(df, x='energy_consumption_median', y='fanout', hover_data=['identifier'],
                     labels={'energy_consumption': 'Energy Consumption (J)', 'fanout': 'Fanout'},
                     title='Interactive Scatter Plot of Energy Consumption vs Fanout')
    
    # Show plot
    fig.show()


def plot_quantile_data(all_normal_data_without_outliers, percentage_quantile:int, highest:bool, save:bool):
    all_project_means = mean_dict(all_normal_data_without_outliers)
    #violin_and_boxplot(all_project_means)
    if highest:
        quantile = filter_highest_data(all_normal_data_without_outliers, all_project_means, percentage_quantile)
    else:
        quantile = filter_lowest_data(all_normal_data_without_outliers, all_project_means, percentage_quantile)
    first_quartile_values = [doc["values"] for doc in quantile]
    labels = [doc["measurableElement"]["classMethodSignature"] + " " + str(doc["lineNumber"]) for doc in quantile]

    for doc in quantile:
        get_call_trace_from_joular_node_entity_id(doc["id"])
        median = get_median(doc["values"])
        print("Median : ", round(median, 2))
        if save:
            label = f'{doc["measurableElement"]["classMethodSignature"]} {doc["lineNumber"]}'
            violin_and_boxplot(doc["values"], bottom=0, height=3, width=2, save_path=label)
        else:
            violin_and_boxplot(doc["values"], bottom=0, height=3, width=2)
        print("=========================================================")

    violin_and_boxplot(first_quartile_values, labels=labels, bottom=0)


def violin_and_boxplot(data:list, labels=None, ylabel="Energy Consumption (J)", save_path=None, bottom=None, height=5, width=8):
    """
    Create a combined violin and box plot for the given data.
    
    Parameters:
    - data: List of lists, where each inner list contains the values for a particular category/document.
    - labels: List of labels for the x-axis corresponding to the data categories/documents.
    - ylabel: Label for the y-axis.
    - save_path: Path to save the plot as a file (optional).
    - bottom: Minimum y-axis limit.
    - height: Height of the plot.
    - width: Width of the plot.
    """

    def create_plot(ax):
        violins = ax.violinplot(
            data,
            showextrema=False
        )

        # Customize violin plot aesthetics
        for pc in violins["bodies"]:
            pc.set_facecolor('white')
            pc.set_edgecolor('black')
            pc.set_linewidth(0.6)
            pc.set_alpha(1)

        # Create the boxplot
        lineprops=dict(linewidth=0.5)
        medianprops=dict(color='black')
        ax.boxplot(
            data,
            whiskerprops=lineprops,
            boxprops=lineprops,
            medianprops=medianprops
        )

        # Customize plot style
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        if labels:
            ax.set_xticklabels(labels, rotation=90, ha='left')
        ax.set_ylabel(ylabel)  # Update ylabel as per your data
        if bottom != None:
            ax.set_ylim(bottom=bottom)

    fig, ax = plt.subplots(figsize=(width,height))
    create_plot(ax)
    plt.tight_layout()
    plt.show()

    if save_path:
        fig_save, ax_save = plt.subplots(figsize=(2,3))
        create_plot(ax_save)

        plt.savefig("/home/jerome/Documents/Assistant/Recherche/joular-scripts/sentinel-notebook/plots/" + save_path + ".jpg", bbox_inches='tight', dpi=300)
        plt.close(fig_save)