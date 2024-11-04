import numpy as np

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

    def set_values(self, values):
        self.values = values
        self.median = np.median(values)
        self.mean = np.mean(values)
        self.std_dev = np.std(values)

    def __str__(self):
        return f"CallTrace(class_method_signature='{self.class_method_signature}', line_number={self.line_number}, median={self.median}, mean={self.mean}, values={self.values})"