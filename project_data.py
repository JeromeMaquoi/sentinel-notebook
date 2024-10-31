import numpy as np
import copy
from utils2 import *

class ProjectData:
    def __init__(self, project_name, call_traces):
        self.project_name = project_name
        self.call_traces = call_traces

    def filter_outliers(self):
        print("---------------")
        print("Remove outliers")
        print("---------------")
        only25ValuesAndMore = []
        for methodData in self.call_traces:
            methodDataCopy = copy.deepcopy(methodData)
            allValues = methodDataCopy.values
            allValuesAfterOutlierRemoval = removeOutliersByStd(allValues)
            #allValuesAfterOutlierRemoval = removeOutliersByZScore(allValues)
            if (len(allValuesAfterOutlierRemoval) >= 25):
                methodDataCopy.values = allValuesAfterOutlierRemoval
                only25ValuesAndMore.append(methodDataCopy)
        print("Len without outliers (with at least 25 values) : ", len(only25ValuesAndMore))
        print()
        self.call_traces = only25ValuesAndMore
        return self
    
    def filter_non_normal(self):
        print("-----------------")
        print("Shapiro-Wilk test")
        print("-----------------")
        normal_data = []
        for document in self.call_traces:
            values = document.values
            stat, p = shapiro(values)
            if (p > 0.05):
                normal_data.append(document)
        print("Number of normal distributions : ", len(normal_data))
        print()
        self.call_traces = normal_data
        return self