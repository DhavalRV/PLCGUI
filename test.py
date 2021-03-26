import sys
import matplotlib
import numpy as np
import random
import threading
import time
import math

from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from matplotlib.figure import Figure
from pymodbus.client.sync import ModbusTcpClient

matplotlib.use("Qt5Agg")

li_fkth_sensor = 0x400


class MplCanvas(FigureCanvasQTAgg):
    """
    Charts to show PLC Input/Outputs for one side of the line

    ------
    One side of the line has 2 inputs and 2 outputs
        Inputs: Counting Sensor *2
        Outputs: Purger *2
    """

    def __init__(self, parent=None, width=5, height=9, dpi=100):
        self.addedData = []
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.fkth_sensor = fig.add_subplot(411)
        self.fkth_purger = fig.add_subplot(412, sharex=self.fkth_sensor)
        self.tac_sensor = fig.add_subplot(413, sharex=self.fkth_sensor)
        self.tac_purger = fig.add_subplot(414, sharex=self.fkth_sensor)

        self.fkth_sensor.set_ylim(-0.1, 1.1)
        self.fkth_purger.set_ylim(-0.1, 1.1)
        self.tac_sensor.set_ylim(-0.1, 1.1)
        self.tac_purger.set_ylim(-0.1, 1.1)

        # self.fkth_sensor.axis("off")
        self.fkth_sensor.spines["bottom"].set_visible(False)
        self.fkth_purger.spines["top"].set_visible(False)
        self.fkth_sensor.spines["bottom"].set_visible(False)
        self.tac_sensor.spines["bottom"].set_visible(False)
        self.tac_sensor.spines["top"].set_visible(False)
        self.tac_purger.spines["top"].set_visible(False)

        self.fkth_sensor.get_yaxis().set_visible(False)
        self.fkth_purger.get_yaxis().set_visible(False)
        self.tac_sensor.get_yaxis().set_visible(False)
        self.tac_purger.get_yaxis().set_visible(False)

        # self.fkth_sensor.add = 0x0

        fig.subplots_adjust(hspace=0)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("PLC Timing Charts")

        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.left_in = MplCanvas(self)
        # self.left_out = MplCanvas(self)
        # self.right_in = MplCanvas(self)
        # self.right_out = MplCanvas(self)

        self.plc_client = ModbusTcpClient("10.13.0.2")
        self.left_in.fkth_sensor.add = 0x400
        self.left_in.fkth_purger.add = 0x401
        self.left_in.tac_sensor.add = 0x402
        self.left_in.tac_purger.add = 0x403

        self.timing_layout = QtWidgets.QGridLayout(self.main_widget)
        self.timing_layout.addWidget(self.left_in, *(0, 0))
        # self.timing_layout.addWidget(self.left_out, *(0, 1))
        # self.timing_layout.addWidget(self.right_in, *(1, 0))
        # self.timing_layout.addWidget(self.right_out, *(1, 1))

        n_samples = np.linspace(0, 99, 100)
        for _side in [self.left_in]:  # , self.left_out, self.right_in, self.right_out]:
            for _plot in [
                _side.fkth_sensor,
                _side.fkth_purger,
                _side.tac_sensor,
                _side.tac_purger,
            ]:
                _plot.xdata = [(n_samples[i]) for i in range(len(n_samples))]
                _plot.ydata = [(0) for i in range(len(n_samples))]
                _plot.plot_ref = None
        self.update_plot()
        self.showMaximized()

        # dataAcquire = threading.Thread()
        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):

        # Drop off the first y element, append a new one.
        for _side in [self.left_in]:  # , self.left_out, self.right_in, self.right_out]:
            for _plot in [
                _side.fkth_sensor,
                _side.fkth_purger,
                _side.tac_sensor,
                _side.tac_purger,
            ]:
                _plot.response = int(
                    (self.plc_client.read_discrete_inputs(_plot.add)).bits[0] == True
                )
                _plot.ydata = _plot.ydata[1:] + [_plot.response]

            # Note: we no longer need to clear the axis.
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            # Then once we have a reference, we can use it to update the data for that line.
            if _side.fkth_sensor.plot_ref is None:
                _side.fkth_sensor.plot_refs = _side.fkth_sensor.plot(
                    _side.fkth_sensor.xdata,
                    _side.fkth_sensor.ydata,
                    "b",
                    drawstyle="steps-mid",
                )
                _side.fkth_sensor.plot_ref = _side.fkth_sensor.plot_refs[0]
            else:

                _side.fkth_sensor.plot_ref.set_ydata(_side.fkth_sensor.ydata)

            if _side.fkth_purger.plot_ref is None:
                _side.fkth_purger.plot_refs = _side.fkth_purger.plot(
                    _side.fkth_purger.xdata,
                    _side.fkth_purger.ydata,
                    "r",
                    drawstyle="steps-mid",
                )
                _side.fkth_purger.plot_ref = _side.fkth_purger.plot_refs[0]
            else:

                _side.fkth_purger.plot_ref.set_ydata(_side.fkth_purger.ydata)

            if _side.tac_sensor.plot_ref is None:
                _side.tac_sensor.plot_refs = _side.tac_sensor.plot(
                    _side.tac_sensor.xdata,
                    _side.tac_sensor.ydata,
                    "c",
                    drawstyle="steps-mid",
                )
                _side.tac_sensor.plot_ref = _side.tac_sensor.plot_refs[0]
            else:

                _side.tac_sensor.plot_ref.set_ydata(_side.tac_sensor.ydata)

            if _side.tac_purger.plot_ref is None:
                _side.tac_purger.plot_refs = _side.tac_purger.plot(
                    _side.tac_purger.xdata,
                    _side.tac_purger.ydata,
                    "m",
                    drawstyle="steps-mid",
                )
                _side.tac_purger.plot_ref = _side.tac_purger.plot_refs[0]
            else:

                _side.tac_purger.plot_ref.set_ydata(_side.tac_purger.ydata)
            # Trigger the canvas to update and redraw.
            _side.draw()


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()