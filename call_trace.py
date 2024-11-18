import numpy as np

class CallTrace:
    def __init__(self, label, mean, std_dev, values):
        self.values = values
        self.mean = mean
        self.std_dev = std_dev
        self.label = label

    def __str__(self):
        return f"CallTrace(label={self.label}, mean={self.mean}, std-dev={self.std_dev}, values={self.values})"