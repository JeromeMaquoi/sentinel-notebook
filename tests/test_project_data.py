import unittest
from scipy.stats import norm
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

        self.normal_trace = CallTrace(values=norm.rvs(size=30, loc=10, scale=1).tolist())
        self.non_normal_trace = CallTrace(values=[1, 1, 1, 1, 20, 30, 40])  # Skewed distribution
        self.project_data2 = ProjectData(
            project_name="TestProject",
            call_traces=[self.normal_trace, self.non_normal_trace]
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

    def test_filter_non_normal(self):
        self.project_data2.filter_non_normal()
        self.assertEqual(len(self.project_data2.call_traces), 1)
        self.assertEqual(self.project_data2.call_traces[0], self.normal_trace)

    def test_filter_highest(self):
        traces = [
            CallTrace(values=np.random.normal(loc=5, scale=1, size=30).tolist()),
            CallTrace(values=np.random.normal(loc=35, scale=1, size=30).tolist()),
            CallTrace(values=np.random.normal(loc=10, scale=1, size=30).tolist()),
            CallTrace(values=np.random.normal(loc=1, scale=1, size=30).tolist())
        ]
        project_data = ProjectData("TestProjectHigh", traces)

        # Filter to keep top 25% by mean
        filtered_data = project_data.filter_highest(percentage=25)
        self.assertEqual(len(filtered_data.call_traces), 1)
        self.assertTrue(all(trace.mean >= 30 for trace in filtered_data.call_traces))

    def test_filter_lowest(self):
        # Add additional CallTrace instances with different mean values
        traces = [
            CallTrace(values=np.random.normal(loc=5, scale=1, size=30).tolist()),  # Lower mean
            CallTrace(values=np.random.normal(loc=15, scale=1, size=30).tolist()),  # Higher mean
            CallTrace(values=np.random.normal(loc=10, scale=1, size=30).tolist())   # Middle mean
        ]
        project_data = ProjectData("TestProjectLow", traces)

        # Filter to keep bottom 50% by mean
        filtered_data = project_data.filter_lowest(percentage=10)

        # Check that only the traces with lower means remain
        self.assertEqual(len(filtered_data.call_traces), 1)
        self.assertTrue(all(trace.mean <= 8 for trace in filtered_data.call_traces))

if __name__ == "__main__":
    unittest.main()
