import unittest
from unittest.mock import patch, MagicMock
from plotter import Plotter
from call_trace import CallTrace
from project_data import ProjectData

class TestPlotter(unittest.TestCase):
    def setUp(self):
        self.call_traces = [
            CallTrace(values=[1, 2, 3, 4, 5]),
            CallTrace(values=[5, 6, 7, 8, 9]),
            CallTrace(values=[2, 3, 5, 6, 8])
        ]
        self.project_data = ProjectData(project_name="TestProject", call_traces=self.call_traces)

    @patch("matplotlib.pyplot.show")
    def test_violin_and_boxplot_display(self, mock_show):
        Plotter.violin_and_boxplot(self.project_data)
        mock_show.assert_called_once()

    @patch("matplotlib.pyplot.subplots")
    def test_plot_data_correctness(self, mock_subplots):
        mock_fig, mock_ax = MagicMock(), MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        Plotter.violin_and_boxplot(self.project_data, bottom=0)

        data = [trace.values for trace in self.project_data.call_traces]
        means = [trace.mean for trace in self.project_data.call_traces]

        mock_ax.violinplot.assert_called_once_with(data, showextrema=False)
        mock_ax.boxplot.assert_called_once()

        mock_ax.scatter.assert_called_once_with(range(1, len(data)+1), means, color="black", marker="x", s=30, label="Mean", zorder=3)

    @patch("matplotlib.pyplot.savefig")
    def test_violin_and_boxplot_save(self, mock_save):
        save_path = "test_plot"
        Plotter.violin_and_boxplot(self.project_data, save_path=save_path)

        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        self.assertIn(save_path + ".pdf", args[0])