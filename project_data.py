import numpy as np
import copy
from utils2 import *
from plotter import Plotter

class ProjectData:
    def __init__(self, project_name:str, call_traces):
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
                methodDataCopy.set_values(allValuesAfterOutlierRemoval)
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
    
    def get_means(self):
        return [trace.mean for trace in self.call_traces]
    
    def filter_highest(self, percentage=25):
        means = self.get_means()
        quantile = np.percentile(means, np.abs(100-percentage))
        filtered = [d for d,mean in zip(self.call_traces, means) if mean >= quantile]
        return ProjectData(self.project_name, filtered)
    
    def filter_lowest(self, percentage=10):
        means = self.get_means()
        quantile = np.percentile(means, percentage)
        filtered = [d for d,mean in zip(self.call_traces, means) if mean <= quantile]
        return ProjectData(self.project_name, filtered)
    
    def plot_quantiles(self, highest:bool, save:bool, begin_label:int):
        label_plot = f'{"Highest" if highest else "Lowest"} CT {self.project_name}' if save else None

        # Assign labels to each CallTrace
        for i, trace in enumerate(self.call_traces, start=begin_label):
            trace.label = f'CT{i}'

        Plotter.violin_and_boxplot(
            project_data=self,
            ylabel="Energy Consumption (J)",
            save_path=label_plot,
            bottom=0
        )