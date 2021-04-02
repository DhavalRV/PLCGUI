import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import json

matplotlib.use("Qt5Agg")


class ChartCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        """
        Canvas containing individual charts for each port selected. Please use a maximum of 4 charts

        ------

        Parameters:
        --------
            ports = PLC Ports selected to be used for timing charts

        """

        fig = Figure(figsize=(5, 9), dpi=100)

        with open("./plc.json") as f:
            plc = json.load(f)
            io_1 = plc["Ports"]["IOport1"]
            io_2 = plc["Ports"]["IOport2"]
            io_3 = plc["Ports"]["IOport3"]
            io_4 = plc["Ports"]["IOport4"]
            title = plc["Title"]

        fig.suptitle(title)

        self.io_1 = fig.add_subplot(411)
        self.io_1.set_ylim(-0.1, 1.1)
        self.io_1.set_yticks([0, 1])
        self.io_1.set_ylabel(io_1, rotation="horizontal", ha="right")
        self.io_1.grid(color="white", linestyle="--", linewidth=0.5, axis="y")
        self.io_1.set_facecolor("grey")
        self.io_1.spines["bottom"].set_visible(False)

        self.io_2 = fig.add_subplot(412, sharex=self.io_1)
        self.io_2.set_ylim(-0.1, 1.1)
        self.io_2.set_yticks([0, 1])
        self.io_2.set_ylabel(io_2, rotation="horizontal", ha="right")
        self.io_2.grid(color="white", linestyle="--", linewidth=0.5, axis="y")
        self.io_2.set_facecolor("grey")
        self.io_2.spines["top"].set_visible(False)
        self.io_2.spines["bottom"].set_visible(False)

        self.io_3 = fig.add_subplot(413, sharex=self.io_1)
        self.io_3.set_ylim(-0.1, 1.1)
        self.io_3.set_yticks([0, 1])
        self.io_3.set_ylabel(io_3, rotation="horizontal", ha="right")
        self.io_3.grid(color="white", linestyle="--", linewidth=0.5, axis="y")
        self.io_3.set_facecolor("grey")
        self.io_3.spines["top"].set_visible(False)
        self.io_3.spines["bottom"].set_visible(False)

        self.io_4 = fig.add_subplot(414, sharex=self.io_1)
        self.io_4.set_ylim(-0.1, 1.1)
        self.io_4.set_yticks([0, 1])
        self.io_4.set_ylabel(io_4, rotation="horizontal", ha="right")
        self.io_4.grid(color="white", linestyle="--", linewidth=0.5, axis="y")
        self.io_4.set_facecolor("grey")
        self.io_4.spines["top"].set_visible(False)

        fig.subplots_adjust(hspace=0)
        super(ChartCanvas, self).__init__(fig)


if __name__ == "__main__":
    canvas = ChartCanvas()
