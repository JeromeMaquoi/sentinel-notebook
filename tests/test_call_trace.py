import unittest
import numpy as np
from call_trace import CallTrace
from project_data import ProjectData

class TestCallTrace(unittest.TestCase):
    def test_call_trace_simple_initialization(self):
        values = [1, 2, 2, 3, 3, 3, 100, 101, 102]
        self.trace1 = CallTrace(values=values)
        self.assertEqual(values, self.trace1.values, "The encoded values are not the same")
        self.assertEqual(np.mean(values), self.trace1.mean, "The mean is not correct")
