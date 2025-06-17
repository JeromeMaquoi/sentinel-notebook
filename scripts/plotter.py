import matplotlib.pyplot as plt
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

class Plotter:
    @staticmethod
    def violin_and_boxplot(project_data, ylabel="Energy Consumption (J)", file_name=None, bottom=None, height=5, width=8):
        """
        Create a combined violin and box plot for the given data.
        
        Parameters:
        - project_data: ProjectData to be plotted
        - means: List of means of each element of data
        - labels: List of labels for the x-axis corresponding to the data categories/documents.
        - ylabel: Label for the y-axis.
        - save_path: Path to save the plot as a file (optional).
        - bottom: Minimum y-axis limit.
        - height: Height of the plot.
        - width: Width of the plot.
        """

        def create_plot(ax, data:list, means:list, labels=None):
            violins = ax.violinplot(
                data,
                showextrema=False
            )

            for pc in violins["bodies"]:
                pc.set_facecolor('white')
                pc.set_edgecolor('black')
                pc.set_linewidth(0.6)
                pc.set_alpha(1)

            lineprops=dict(linewidth=0.5)
            medianprops=dict(color='black')
            ax.boxplot(
                data,
                whiskerprops=lineprops,
                boxprops=lineprops,
                medianprops=medianprops,
                widths=0.3
            )

            ax.scatter(range(1, len(data) + 1), means, color='black', marker="x", s=30, label='Mean', zorder=3)

            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            if labels:
                ax.set_xticklabels(labels)
            ax.set_ylabel(ylabel)
            if bottom != None:
                ax.set_ylim(bottom=bottom)

        _, ax = plt.subplots(figsize=(width,height))
        data = [trace.values for trace in project_data.call_traces]
        means = [trace.mean for trace in project_data.call_traces]
        labels = [trace.label for trace in project_data.call_traces]
        create_plot(ax, data=data, means=means, labels=labels)
        plt.tight_layout()
        plt.show()

        if file_name:
            fig_save, ax_save = plt.subplots(figsize=(3,3))
            create_plot(ax_save, data=data, means=means, labels=labels)

            plt.savefig("../plots/" + file_name + ".pdf", bbox_inches='tight', dpi=300)
            plt.close(fig_save)
            print(f"File 'plots/{file_name}.pdf' saved\n\n")