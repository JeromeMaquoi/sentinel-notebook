import pandas as pd
from pymongo import MongoClient
import numpy as np
import statistics
import plotly.express as px
import call_trace
import project_data

import importlib
importlib.reload(call_trace)
importlib.reload(project_data)
from call_trace import CallTrace
from project_data import ProjectData

def main():
    pass

if __name__ == "__main__":
    main()

def get_all_data_from_one_repo(repo_name:str, min_nb_values:int, excluded_words:str=" ", excluded_first_ancestor_class:str=" "):
    all_data = aggregate_joular_node_entity_by_value(repo_name=repo_name, min_nb_values=min_nb_values, excluded_words=excluded_words, excluded_first_ancestor_class=excluded_first_ancestor_class)
    call_traces = [CallTrace(values=doc["values"], class_method_signature=doc["measurableElement"].get("classMethodSignature", ""), line_number=doc.get("lineNumber")) for doc in all_data]

    project_data = ProjectData(project_name=repo_name, call_traces=call_traces)
    project_data.filter_outliers().filter_non_normal()
    
    return project_data

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

""" def get_call_trace_from_joular_node_entity_id(id:str):
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
    return call_trace """

""" def get_ck_metric_from_joular_node_entity(repo_name:str, class_name:str, method_name:str, name:str="fanout"):
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

    return sum_fanout """



# -------------
# LISTS METHODS
# -------------

#def sort_entities_by_id_list(id_list:list, cursor):
    #"""
    #The ancestors of one entity are sorted from the most distant ancestor to the closest #one. The first element of the list will be the farthest ancestor and the last element #will be the direct parent.
    #"""
    #documents_by_id = {doc['_id']: doc for doc in cursor}
    #return [documents_by_id[id] for id in id_list if id in documents_by_id]

# --------------------------------
# OUTLIERS AND NORMAL DISTRIBUTION
# --------------------------------

def remove_outliers_by_std(all_values):
    mean = np.mean(all_values)
    std_dev = np.std(all_values)
    return [x for x in all_values if (np.abs(mean - x) <= 3 * std_dev)]