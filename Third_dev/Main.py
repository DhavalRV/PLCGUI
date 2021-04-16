import math
import random
import sys
import threading
import time
import datetime
import multiprocessing
import threading

import numpy as np
import json
import os
from csv import writer

from pymodbus.client.sync import ModbusTcpClient
from PyQt5 import QtCore, QtWidgets

from Canvas import ChartCanvas
from PLCAddresses import get_bit
from Settings import SettingWindow


class IO:
    def __init__(self):
        self.ydata = []
        self.typ = None
        self.response = None
        self.bit = None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self, data_io1, data_io2, data_io3, data_io4, n_samples, *args, **kwargs
    ):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("PLC Timing Charts")
        self.setStyleSheet("background-color: #1b1b1b")

        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.canvas = ChartCanvas(self)

        self.main_layout = QtWidgets.QGridLayout(self.main_widget)
        self.main_layout.addWidget(self.canvas, 1, 0)

        self.setting = SettingWindow(self)
        self.btn = QtWidgets.QPushButton("Settings")
        self.btn.setMinimumWidth(130)
        self.btn.setStyleSheet("background-color: #424242;color:#ffffff")
        self.main_layout.addWidget(self.btn, 0, 0, alignment=QtCore.Qt.AlignRight)
        # self.btn.move(100, 100)
        self.btn.clicked.connect(self.setting.SettingsDiag)

        # Need to adjust xdata
        self.canvas.io_1.xdata = [(i) for i in range(len(n_samples))]
        self.canvas.io_2.xdata = [(i) for i in range(len(n_samples))]
        self.canvas.io_3.xdata = [(i) for i in range(len(n_samples))]
        self.canvas.io_4.xdata = [(i) for i in range(len(n_samples))]
        self.canvas.io_1.plot_ref = None
        self.canvas.io_2.plot_ref = None
        self.canvas.io_3.plot_ref = None
        self.canvas.io_4.plot_ref = None

        self.showMaximized()
        plot = threading.Thread(
            target=update_plots,
            args=(
                self,
                data_io1,
                data_io2,
                data_io3,
                data_io4,
            ),
            daemon=True,
        )
        plot.start()


def update_plots(self, data_io1, data_io2, data_io3, data_io4):
    while True:
        start = time.time()
        self.canvas.io_1.ydata = data_io1.recv()
        self.canvas.io_2.ydata = data_io2.recv()
        self.canvas.io_3.ydata = data_io3.recv()
        self.canvas.io_4.ydata = data_io4.recv()

        for _io_plot in [
            self.canvas.io_1,
            self.canvas.io_2,
            self.canvas.io_3,
            self.canvas.io_4,
        ]:
            if _io_plot.plot_ref is None:
                _io_plot.plot_refs = _io_plot.plot(
                    _io_plot.xdata,
                    _io_plot.ydata,
                    _io_plot.color,
                    drawstyle="steps-mid",
                )
                _io_plot.plot_ref = _io_plot.plot_refs[0]
            else:
                _io_plot.plot_ref.set_ydata(_io_plot.ydata)
        self.canvas.draw_idle()
        elapsed_time = time.time() - start
        # print(elapsed_time)


def acquire_signal(data_io1, data_io2, data_io3, data_io4, n_samples):
    io_1 = IO()
    io_2 = IO()
    io_3 = IO()
    io_4 = IO()

    io_1.ydata = [(0) for i in range(len(n_samples))]
    io_2.ydata = [(0) for i in range(len(n_samples))]
    io_3.ydata = [(0) for i in range(len(n_samples))]
    io_4.ydata = [(0) for i in range(len(n_samples))]

    try:
        with open("./plc.json") as f:
            plc = json.load(f)
            ip = plc["ipAddress"]
            io_1.typ, io_1.bit = get_bit(plc["Ports"]["IOport1"])
            io_2.typ, io_2.bit = get_bit(plc["Ports"]["IOport2"])
            io_3.typ, io_3.bit = get_bit(plc["Ports"]["IOport3"])
            io_4.typ, io_4.bit = get_bit(plc["Ports"]["IOport4"])
            plc_client = ModbusTcpClient(ip)
        while True:
            start = time.time()
            input_data = plc_client.read_discrete_inputs(1024, 32)
            output_data = plc_client.read_discrete_inputs(1280, 32)

            for _io in [io_1, io_2, io_3, io_4]:
                if _io.typ == "X":
                    _io.response = int(input_data.bits[_io.bit] == True)
                elif _io.typ == "Y":
                    _io.response = int(output_data.bits[_io.bit] == True)
                else:
                    io_1.response = -2

                _io.ydata = _io.ydata[1:] + [_io.response]

            data_io1.send(io_1.ydata)
            data_io2.send(io_2.ydata)
            data_io3.send(io_3.ydata)
            data_io4.send(io_4.ydata)

            elapsed_time = time.time() - start
            remaining_time = 0.05 - elapsed_time
            if remaining_time > 0:
                time.sleep(remaining_time)
            else:
                print("Warning: Acquisition rate is above 50ms")
            msg = str(f"Current acquisition rate is: {elapsed_time}seconds")
            logger([datetime.datetime.now().strftime("%H:%M:%S.%f"), msg, None])

    except:
        reason = f"Unable to connect to PLC. Please confirm if PLC address is {ip}"
        logger([datetime.datetime.now().strftime("%H:%M:%S.%f"), "inf", reason])
        print(reason)


def logger(str):
    folder = "Logs"
    today = datetime.datetime.now()
    filename = (today.strftime("%d%m%Y")) + ".csv"

    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.isfile(os.path.join(folder, filename)):
        with open(os.path.join(folder, filename), "a+", newline="") as file:
            csv_writer = writer(file)
            csv_writer.writerow(["Time", "Acqusition rate", "Error"])
    with open(os.path.join(folder, filename), "a+", newline="") as file:
        csv_writer = writer(file)
        csv_writer.writerow(str)


if __name__ == "__main__":

    multiprocessing.freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    parent_io1, child_io1 = multiprocessing.Pipe()
    parent_io2, child_io2 = multiprocessing.Pipe()
    parent_io3, child_io3 = multiprocessing.Pipe()
    parent_io4, child_io4 = multiprocessing.Pipe()
    n_samples = np.linspace(0, 299, 150)

    w = MainWindow(child_io1, child_io2, child_io3, child_io4, n_samples)

    acquire = multiprocessing.Process(
        name="Data Acquisition",
        target=acquire_signal,
        args=(parent_io1, parent_io2, parent_io3, parent_io4, n_samples),
        daemon=True,
    )
    acquire.start()

    app.exec_()
