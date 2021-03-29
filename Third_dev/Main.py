import math
import random
import sys
import threading
import time
import multiprocessing
import threading

import numpy as np

from pymodbus.client.sync import ModbusTcpClient
from PyQt5 import QtCore, QtWidgets

from Canvas import ChartCanvas


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, data, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("PLC Timing Charts")

        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.canvas = ChartCanvas(self)

        self.main_layout = QtWidgets.QGridLayout(self.main_widget)
        self.main_layout.addWidget(self.canvas, *(0, 0))
        n_samples = np.linspace(0, 249, 250)

        # for _plot in :
        #
        # Need to automate init all charts with null value
        #

        # Need to adjust xdata
        self.canvas.io_1.xdata = [(i) for i in range(len(n_samples))]
        self.canvas.io_1.ydata = [(0) for i in range(len(n_samples))]
        self.canvas.io_1.plot_ref = None

        self.showMaximized()
        plot = threading.Thread(
            target=update_plots,
            args=(
                self,
                data,
            ),
            daemon=True,
        )
        plot.start()
        # self.update_plots()


def update_plots(self, data):
    while True:
        self.canvas.io_1.response = data.recv()
        self.canvas.io_1.ydata = self.canvas.io_1.ydata[1:] + [
            self.canvas.io_1.response
        ]
        if self.canvas.io_1.plot_ref is None:
            self.canvas.io_1.plot_refs = self.canvas.io_1.plot(
                self.canvas.io_1.xdata,
                self.canvas.io_1.ydata,
                "b",
                drawstyle="steps-mid",
            )
            self.canvas.io_1.plot_ref = self.canvas.io_1.plot_refs[0]
        else:
            self.canvas.io_1.plot_ref.set_ydata(self.canvas.io_1.ydata)
        self.canvas.draw()


def acquire_signal(data):
    while True:
        start = time.time()
        plc_client = ModbusTcpClient("10.24.0.2")
        io_1_add = 0x400
        io_1_response = int((plc_client.read_discrete_inputs(io_1_add)).bits[0] == True)
        data.send(io_1_response)

        elapsed_time = time.time() - start
        # print(io_1_response)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    parent_data, child_data = multiprocessing.Pipe()
    a = 1
    w = MainWindow(child_data)

    acquire = multiprocessing.Process(
        target=acquire_signal, args=(parent_data,), daemon=True
    )
    acquire.start()

    app.exec_()
