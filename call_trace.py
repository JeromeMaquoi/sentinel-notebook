import numpy as np
from plotter import Plotter

class CallTrace:
    def __init__(self, values, class_method_signature="", line_number=None):
        self.values = values
        #self.id = id
        self.class_method_signature = class_method_signature
        self.line_number = line_number
        self.median = np.median(values)
        self.mean = np.mean(values)
        self.std_dev = np.std(values)
        self.label = ""

    def plot(self, save=False):
        label = f"{self.class_method_signature} {self.line_number}" if save else None
        Plotter.violin_and_boxplot(
            data=[self.values],
            ylabel="Energy Consumption (J)",
            save_path=label if save else None,
            bottom=0,
            height=3,
            width=2
        )
        print(f"Median: {round(self.median, 2)}")
        print("=========================================================")

    def __str__(self):
        return f"CallTrace(class_method_signature='{self.class_method_signature}', line_number={self.line_number}, median={self.median}, mean={self.mean}, values={self.values})"