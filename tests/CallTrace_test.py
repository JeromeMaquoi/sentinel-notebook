import unittest
import numpy as np
from call_trace import CallTrace
from project_data import ProjectData

class Test_CallTrace(unittest.TestCase):
    def test_call_trace_simple_initialization(self):
        values = [1, 2, 2, 3, 3, 3, 100, 101, 102]
        self.trace1 = CallTrace(values=values)
        self.assertEqual(values, self.trace1.values, "The encoded values are not the same")
        self.assertEqual(np.mean(values), self.trace1.mean, "The mean is not correct")

    def test_call_trace_filter_outliers_change_mean(self):
        values = [1] * 25 + [10000]
        self.trace1 = CallTrace(values=values)
        self.assertEqual(self.trace1.mean, 385.5769230769231)
        self.project_data = ProjectData(project_name="test", call_traces=[self.trace1])

        self.project_data.filter_outliers()

        self.assertEqual(1, self.project_data.call_traces[0].mean)
