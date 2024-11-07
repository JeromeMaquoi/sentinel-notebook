import unittest
from call_trace import CallTrace
from project_data import ProjectData
from utils2 import *

class TestProjectData(unittest.TestCase):
    def setUp(self):
        # Sample data with outliers
        self.trace1 = CallTrace(values=[1, 2, 2, 3, 3, 3, 100, 101, 102] * 3)  # Contains outliers
        self.trace2 = CallTrace(values=[5] * 30)  # No outliers, exactly 30 values
        self.trace3 = CallTrace(values=[10, 12, 10, 10, 11, 13, 11, 1000] + [10]*18)  # Contains significant outlier

        # Create ProjectData with a mix of call traces
        self.project_data = ProjectData(
            project_name="test_project",
            call_traces=[self.trace1, self.trace2, self.trace3]
        )

    def test_filter_outliers_removes_outliers(self):
        # Apply the filter_outliers method
        self.project_data.filter_outliers()
        
        # Verify that traces with outliers have fewer values after filtering
        # Original trace1 should lose its outliers
        filtered_trace1_values = remove_outliers_by_std(self.trace1.values)
        self.assertEqual(len(self.project_data.call_traces[0].values), len(filtered_trace1_values))

        # Original trace3 should also lose its outliers
        filtered_trace3_values = remove_outliers_by_std(self.trace3.values)
        self.assertEqual(len(self.project_data.call_traces[2].values), len(filtered_trace3_values))

    def test_filter_outliers_keeps_traces_with_at_least_25_values(self):
        # Apply the filter_outliers method
        self.project_data.filter_outliers()

        # Verify that the remaining traces have at least 25 values
        for trace in self.project_data.call_traces:
            self.assertGreaterEqual(len(trace.values), 25)

    def test_filter_outliers_removes_traces_with_fewer_than_25_values(self):
        # Create a call trace with fewer than 25 values after outlier removal
        trace4 = CallTrace(values=[1000, 2000, 3000, 4000, 5000] + [5]*20)  # Many extreme outliers
        self.project_data.call_traces.append(trace4)

        # Apply the filter_outliers method
        self.project_data.filter_outliers()

        # Ensure trace4 has been removed due to fewer than 25 values after outlier filtering
        self.assertNotIn(trace4, self.project_data.call_traces)

    def test_filter_outliers_no_outliers(self):
        # A trace with no outliers should remain unchanged
        trace_no_outliers = CallTrace(values=[20] * 40)  # No outliers
        project_data = ProjectData(
            project_name="test_project_no_outliers",
            call_traces=[trace_no_outliers]
        )

        # Apply the filter_outliers method
        project_data.filter_outliers()

        self.assertTrue(project_data.call_traces)
        # The trace should remain unchanged
        self.assertEqual(len(project_data.call_traces[0].values), 40)

if __name__ == "__main__":
    unittest.main()
