import numpy as np

class CallTrace:
    def __init__(self, values, label=""):
        self.values = values
        self.mean = np.mean(values)
        self.std_dev = np.std(values)
        self.label = label

    def __str__(self):
        return f"CallTrace(label={self.label}, mean={self.mean}, std-dev={self.std_dev}, values={self.values})"