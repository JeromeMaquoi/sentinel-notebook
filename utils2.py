import pandas as pd
import json
from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import copy
from scipy.stats import shapiro

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

def aggregate_joular_node_entity_by_value(repo_name:str, min_nb_values:int):
    client = MongoClient('mongodb://localhost:27017/')
    cursor = client['sentinelBackend']['joular_node_entity'].aggregate([
        {
            '$match': {
                'commit.repository.name': repo_name
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
        }
    ])
    return [doc for doc in cursor]

def get_ancestors_from_joular_node_entity_id(id:str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['sentinelBackend']
    collection = db['joular_node_entity']

    doc = collection.find_one({"_id":id},{"_id":0, "ancestors":1})
    if (doc["ancestors"] != []):
        ancestor_ids = doc["ancestors"]
        ancestors = collection.find({"_id": {"$in":ancestor_ids}},{"_id":0, "measurableElement.classMethodSignature":1, "lineNumber":1})
        for ancestor in ancestors:
            print(f'{ancestor["measurableElement"]["classMethodSignature"]} {ancestor["lineNumber"]}')
    else:
        print("There are no ancestors :/")

def mean_dict(data):
    return [np.mean(d["values"]) for d in data]

# --------------------------------
# OUTLIERS AND NORMAL DISTRIBUTION
# --------------------------------

def removeOutliers(data):
    print("Len with outliers : ", len(data))
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
    normal_data = []
    for document in data:
        values = document["values"]
        stat, p = shapiro(values)
        if (p > 0.05):
            normal_data.append(document)
    print("Number of normal distributions : ", len(normal_data))
    return normal_data

def filter_highest_data(data, means, highest_percentage=25):
    quantile = np.percentile(means, np.abs(100-highest_percentage))
    return [d for d,mean in zip(data, means) if mean >= quantile]

# ----
# PLOT
# ----

def violin_and_boxplot(data:list, labels=None, ylabel="Values", save_path=None):
    """
    Create a combined violin and box plot for the given data.
    
    Parameters:
    - data: List of lists, where each inner list contains the values for a particular category/document.
    - labels: List of labels for the x-axis corresponding to the data categories/documents.
    - ylabel: Label for the y-axis.
    - save_path: Path to save the plot as a file (optional).
    """
    fig, ax = plt.subplots(figsize=(8,6))
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

    plt.show()