import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

matplotlib.use("Qt5Agg")


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, ports, parent=None):
        """
        Canvas containing individual charts for each port selected. Please use a maximum of 4 charts

        ------

        Parameters:
        --------
            ports = PLC Ports selected to be used for timing charts

        """

        fig = Figure(figsize=(5, 9), dpi=100)
        for num in range(len(ports)):
            print(ports[num])
            if num == 0:
            else:
                pass
                # self.num = fig.add_subplot(nums,1,num, sharex=self.)
        # self.fkth_sensor = fig.add_subplot(411)
        # self.fkth_purger = fig.add_subplot(412, sharex=self.fkth_sensor)
        # self.tr_sensor = fig.add_subplot(413, sharex=self.fkth_sensor)
        # self.tr_purger = fig.add_subplot(414, sharex=self.fkth_sensor)

        # self.fkth_sensor.set_ylim(-0.1, 1.1)
        # self.fkth_purger.set_ylim(-0.1, 1.1)
        # self.tr_sensor.set_ylim(-0.1, 1.1)
        # self.tr_purger.set_ylim(-0.1, 1.1)
        # # self.fkth_sensor.axis("off")
        # self.fkth_sensor.spines["bottom"].set_visible(False)
        # self.fkth_purger.spines["top"].set_visible(False)
        # self.fkth_sensor.spines["bottom"].set_visible(False)
        # self.tr_sensor.spines["bottom"].set_visible(False)
        # self.tr_sensor.spines["top"].set_visible(False)
        # self.tr_purger.spines["top"].set_visible(False)

        # self.fkth_sensor.get_xaxis().set_visible(False)
        # self.fkth_purger.get_xaxis().set_visible(False)
        # self.tr_sensor.get_xaxis().set_visible(False)
        # self.tr_purger.get_xaxis().set_visible(False)

        # self.fkth_sensor.set_yticks([0, 1])
        # self.fkth_purger.set_yticks([0, 1])
        # self.tr_sensor.set_yticks([0, 1])
        # self.tr_purger.set_yticks([0, 1])

        # self.fkth_sensor.set_ylabel("X0", rotation="horizontal", ha="right")
        # self.fkth_purger.set_ylabel("X1", rotation="horizontal", ha="right")
        # self.tr_sensor.set_ylabel("X2", rotation="horizontal", ha="right")
        # self.tr_purger.set_ylabel("X3", rotation="horizontal", ha="right")
        # # self.fkth_sensor.set_roatation(rotation=90)
        # # self.fkth_sensor.add = 0x0

        # fig.subplots_adjust(hspace=0)
        # super(MplCanvas, self).__init__(fig)


if __name__ == "__main__":
    canvas = MplCanvas(ports=["X0", "X1", "X2"])
