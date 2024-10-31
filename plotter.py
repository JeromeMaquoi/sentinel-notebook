import matplotlib.pyplot as plt
import numpy as np

class Plotter:
    @staticmethod
    def violin_and_boxplot(data:list, labels=None, ylabel="Energy Consumption (J)", save_path=None, bottom=None, height=5, width=8):
        """
        Create a combined violin and box plot for the given data.
        
        Parameters:
        - data: List of lists, where each inner list contains the values for a particular category/document.
        - labels: List of labels for the x-axis corresponding to the data categories/documents.
        - ylabel: Label for the y-axis.
        - save_path: Path to save the plot as a file (optional).
        - bottom: Minimum y-axis limit.
        - height: Height of the plot.
        - width: Width of the plot.
        """

        def create_plot(ax):
            violins = ax.violinplot(
                data,
                showextrema=False
            )

            # Customize violin plot aesthetics
            for pc in violins["bodies"]:
                pc.set_facecolor('white')
                pc.set_edgecolor('black')
                pc.set_linewidth(0.6)
                pc.set_alpha(1)

            # Create the boxplot
            lineprops=dict(linewidth=0.5)
            medianprops=dict(color='black')
            ax.boxplot(
                data,
                whiskerprops=lineprops,
                boxprops=lineprops,
                medianprops=medianprops,
                widths=0.3
            )

            means = [np.mean(category) for category in data]
            ax.scatter(range(1, len(data) + 1), means, color='black', marker="x", s=30, label='Mean', zorder=3)

            # Customize plot style
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            if labels:
                ax.set_xticklabels(labels)
            ax.set_ylabel(ylabel)  # Update ylabel as per your data
            if bottom != None:
                ax.set_ylim(bottom=bottom)

        fig, ax = plt.subplots(figsize=(width,height))
        create_plot(ax)
        plt.tight_layout()
        plt.show()

        if save_path:
            fig_save, ax_save = plt.subplots(figsize=(3,4))
            create_plot(ax_save)

            plt.savefig("/home/jerome/Documents/Assistant/Recherche/joular-scripts/sentinel-notebook/plots/" + save_path + ".jpg", bbox_inches='tight', dpi=300)
            plt.close(fig_save)