import sys
import matplotlib
import numpy as np
import random
import threading
import multiprocessing
import time
import math

from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from matplotlib.figure import Figure

from pymodbus.client.sync import ModbusTcpClient

matplotlib.use("Qt5Agg")

# X0 = 0x400
# X1 = 0x401
# X2 = 0x402
# X3 = 0x403
# X4 = 0x404
# X5 = 0x405
# X6 = 0x406
# X7 = 0x407

# Y0 = 0x500
# Y1 = 0x501
# Y2 = 0x502
# Y3 = 0x503
# Y4 = 0x504
# Y5 = 0x505
# Y6 = 0x506
# Y7 = 0x507
# Y8 = 0x508

# M0 = 0x800
# M1 = 0x801
# M2 = 0x802
# M3 = 0x803
# M4 = 0x804
# M5 = 0x805
# M6 = 0x806
# M7 = 0x807
# M8 = 0x808
# M9 = 0x809
# M10 = 0x810
# M11 = 0x811
# M12 = 0x812
# M13 = 0x813
# M14 = 0x814
# M15 = 0x815
# M16 = 0x816
# M17 = 0x817
# M18 = 0x818
# M19 = 0x819
# M256 = 0x900


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
        self.tr_sensor = fig.add_subplot(413, sharex=self.fkth_sensor)
        self.tr_purger = fig.add_subplot(414, sharex=self.fkth_sensor)

        self.fkth_sensor.set_ylim(-0.1, 1.1)
        self.fkth_purger.set_ylim(-0.1, 1.1)
        self.tr_sensor.set_ylim(-0.1, 1.1)
        self.tr_purger.set_ylim(-0.1, 1.1)

        # self.fkth_sensor.axis("off")
        self.fkth_sensor.spines["bottom"].set_visible(False)
        self.fkth_purger.spines["top"].set_visible(False)
        self.fkth_sensor.spines["bottom"].set_visible(False)
        self.tr_sensor.spines["bottom"].set_visible(False)
        self.tr_sensor.spines["top"].set_visible(False)
        self.tr_purger.spines["top"].set_visible(False)

        self.fkth_sensor.get_xaxis().set_visible(False)
        self.fkth_purger.get_xaxis().set_visible(False)
        self.tr_sensor.get_xaxis().set_visible(False)
        self.tr_purger.get_xaxis().set_visible(False)

        self.fkth_sensor.set_yticks([0, 1])
        self.fkth_purger.set_yticks([0, 1])
        self.tr_sensor.set_yticks([0, 1])
        self.tr_purger.set_yticks([0, 1])

        self.fkth_sensor.set_ylabel(
            "FK/TH \nCounting Sensor", rotation="horizontal", ha="right"
        )
        self.fkth_purger.set_ylabel(
            "FK/TH \nPurging Action", rotation="horizontal", ha="right"
        )
        self.tr_sensor.set_ylabel(
            "TR \nCounting Sensor", rotation="horizontal", ha="right"
        )
        self.tr_purger.set_ylabel(
            "TR \nPurging Action", rotation="horizontal", ha="right"
        )
        # self.fkth_sensor.set_roatation(rotation=90)
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

        self.plc_client = ModbusTcpClient("10.24.0.2")
        self.left_in.fkth_sensor.add = 0x400
        self.left_in.fkth_purger.add = 0x401
        self.left_in.tr_sensor.add = 0x402
        self.left_in.tr_purger.add = 0x403

        self.timing_layout = QtWidgets.QGridLayout(self.main_widget)
        self.timing_layout.addWidget(self.left_in, *(0, 0))
        # self.timing_layout.addWidget(self.left_out, *(0, 1))
        # self.timing_layout.addWidget(self.right_in, *(1, 0))
        # self.timing_layout.addWidget(self.right_out, *(1, 1))

        n_samples = np.linspace(0, 499, 100)
        for _side in [self.left_in]:  # , self.left_out, self.right_in, self.right_out]:
            for _plot in [
                _side.fkth_sensor,
                _side.fkth_purger,
                _side.tr_sensor,
                _side.tr_purger,
            ]:
                _plot.xdata = [(n_samples[i]) for i in range(len(n_samples))]
                _plot.ydata = [(0) for i in range(len(n_samples))]
                _plot.plot_ref = None
        self.update_plot()
        self.showMaximized()

        # dataAcquire = threading.Thread(name="data loop", target=self.acquire_signal)
        # dataAcquire.start()
        # Setup a timer to trigger the redraw by calling update_plot.

        acquire = threading.Thread(target=self.acquire_signal, daemon=True)
        # plotting = threading.Thread(target=self.update_plot, daemon=True)

        acquire.start()
        # plotting.start()
        # acquire.join()
        # plotting.join()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(25)
        # self.timer.timeout.connect(self.acquire_signal)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def acquire_signal(self):
        while True:
            start = time.time()
            for _side in [
                self.left_in
            ]:  # , self.left_out, self.right_in, self.right_out]:
                for _plot in [
                    _side.fkth_sensor,
                    _side.fkth_purger,
                    _side.tr_sensor,
                    _side.tr_purger,
                ]:
                    _plot.response = int(
                        (self.plc_client.read_discrete_inputs(_plot.add)).bits[0]
                        == True
                    )
                    _plot.ydata = _plot.ydata[1:] + [_plot.response]
            elapsed_time = time.time() - start
            print(elapsed_time)

    def update_plot(self):

        # Drop off the first y element, append a new one.
        for _side in [self.left_in]:  # , self.left_out, self.right_in, self.right_out]:
            # for _plot in [
            #     _side.fkth_sensor,
            #     _side.fkth_purger,
            #     _side.tr_sensor,
            #     _side.tr_purger,
            # ]:
            # _plot.response = int(
            #     (self.plc_client.read_discrete_inputs(_plot.add)).bits[0] == True
            # )

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

            if _side.tr_sensor.plot_ref is None:
                _side.tr_sensor.plot_refs = _side.tr_sensor.plot(
                    _side.tr_sensor.xdata,
                    _side.tr_sensor.ydata,
                    "c",
                    drawstyle="steps-mid",
                )
                _side.tr_sensor.plot_ref = _side.tr_sensor.plot_refs[0]
            else:

                _side.tr_sensor.plot_ref.set_ydata(_side.tr_sensor.ydata)

            if _side.tr_purger.plot_ref is None:
                _side.tr_purger.plot_refs = _side.tr_purger.plot(
                    _side.tr_purger.xdata,
                    _side.tr_purger.ydata,
                    "m",
                    drawstyle="steps-mid",
                )
                _side.tr_purger.plot_ref = _side.tr_purger.plot_refs[0]
            else:

                _side.tr_purger.plot_ref.set_ydata(_side.tr_purger.ydata)
            # Trigger the canvas to update and redraw.
            _side.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    app.exec_()