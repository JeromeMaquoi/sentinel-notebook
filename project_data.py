from plotter import Plotter
import csv
from call_trace import CallTrace

class ProjectData:
    def __init__(self, project_name:str, call_traces):
        self.project_name = project_name
        self.call_traces = call_traces
    
    def plot_quantiles(self, highest:bool, save:bool):
        label_plot = f'{"Highest" if highest else "Lowest"} CT {self.project_name}' if save else None

        Plotter.violin_and_boxplot(
            project_data=self,
            ylabel="Energy Consumption (J)",
            file_name=label_plot,
            bottom=0
        )
    

    @staticmethod
    def import_for_project_from_csv(file_path: str, project_name: str):
        """
        Import project data from a CSV file for a specific project.
        
        Parameters:
        - file_path: Path to the CSV file.
        - project_name: Name of the project to import data for.
        """
        print(f"Importing data for project '{project_name}' from {file_path}...")

        # List to store the call traces for the specified project
        call_traces = []

        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                if row["Project Name"] == project_name:
                    label = row["Label"]
                    values = list(map(float, row["Values"].split(";")))

                    # Create a CallTrace object and add it to the list
                    call_trace = CallTrace(label=label, values=values)
                    call_traces.append(call_trace)

        if call_traces:
            # Return a ProjectData object with the collected call traces
            return ProjectData(project_name=project_name, call_traces=call_traces)
        else:
            print(f"No data found for project '{project_name}'.")
            return None