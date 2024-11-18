import numpy as np
import copy
from utils2 import *
import plotter
import importlib
importlib.reload(plotter)
from plotter import Plotter
from scipy.stats import shapiro
import csv

class ProjectData:
    def __init__(self, project_name:str, call_traces):
        self.project_name = project_name
        self.call_traces = call_traces

    def filter_outliers(self):
        print("---------------")
        print("Remove outliers")
        print("---------------")
        only_25_values_and_more = []
        for method_data in self.call_traces:
            method_data_copy = copy.deepcopy(method_data)
            all_values = method_data_copy.values
            all_values_after_outlier_removal = remove_outliers_by_std(all_values)
            if (len(all_values_after_outlier_removal) >= 25):
                method_data_copy.set_values(all_values_after_outlier_removal)
                only_25_values_and_more.append(method_data_copy)
        print("Len without outliers (with at least 25 values) : ", len(only_25_values_and_more))
        print()
        self.call_traces = only_25_values_and_more
        return self
    
    def filter_non_normal(self):
        print("-----------------")
        print("Shapiro-Wilk test")
        print("-----------------")
        normal_data = []
        for document in self.call_traces:
            values = document.values
            _, p = shapiro(values)
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

    def to_csv(self, file_path):
        """
        Export the project's call traces to a CSV file.

        Parameters:
        - file_path: Path to the output CSV file.
        """
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Project Name", "Label", "Mean", "Std-dev", "Values"])

            for trace in self.call_traces:
                writer.writerow([
                    self.project_name,
                    trace.label,
                    trace.mean,
                    trace.std_dev,
                    ";".join(map(str, trace.values))])