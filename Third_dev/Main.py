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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self, data_io1, data_io2, data_io3, data_io4, n_samples, *args, **kwargs
    ):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("PLC Timing Charts")

        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.canvas = ChartCanvas(self)

        self.main_layout = QtWidgets.QGridLayout(self.main_widget)
        self.main_layout.addWidget(self.canvas, *(0, 0))
        # for _plot in :
        #
        # Need to automate init all charts with null value
        #

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
        # update_plots(self, data)
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(50)
        # self.timer.timeout.connect(update_plots)
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
        # self.update_plots()


def update_plots(self, data_io1, data_io2, data_io3, data_io4):
    while True:
        self.canvas.io_1.ydata = data_io1.recv()
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
        self.canvas.io_2.ydata = data_io2.recv()
        if self.canvas.io_2.plot_ref is None:
            self.canvas.io_2.plot_refs = self.canvas.io_2.plot(
                self.canvas.io_2.xdata,
                self.canvas.io_2.ydata,
                "r",
                drawstyle="steps-mid",
            )
            self.canvas.io_2.plot_ref = self.canvas.io_2.plot_refs[0]
        else:
            self.canvas.io_2.plot_ref.set_ydata(self.canvas.io_2.ydata)
        self.canvas.io_3.ydata = data_io3.recv()
        if self.canvas.io_3.plot_ref is None:
            self.canvas.io_3.plot_refs = self.canvas.io_3.plot(
                self.canvas.io_3.xdata,
                self.canvas.io_3.ydata,
                "c",
                drawstyle="steps-mid",
            )
            self.canvas.io_3.plot_ref = self.canvas.io_3.plot_refs[0]
        else:
            self.canvas.io_3.plot_ref.set_ydata(self.canvas.io_3.ydata)
        self.canvas.io_4.ydata = data_io4.recv()
        if self.canvas.io_4.plot_ref is None:
            self.canvas.io_4.plot_refs = self.canvas.io_4.plot(
                self.canvas.io_4.xdata,
                self.canvas.io_4.ydata,
                "m",
                drawstyle="steps-mid",
            )
            self.canvas.io_4.plot_ref = self.canvas.io_4.plot_refs[0]
        else:
            self.canvas.io_4.plot_ref.set_ydata(self.canvas.io_4.ydata)
        self.canvas.draw_idle()


# class io:
#     def __init__(self):
#         # ydata = None
#         typ = None
#         response = None
#         bit = None


def acquire_signal(data_io1, data_io2, data_io3, data_io4, n_samples):
    # io_1 = io()
    # io_2 = io()
    # io_3 = io()
    # io_4 = io()
    # io_1.ydata = 12
    io_1_ydata = [(0) for i in range(len(n_samples))]
    io_2_ydata = [(0) for i in range(len(n_samples))]
    io_3_ydata = [(0) for i in range(len(n_samples))]
    io_4_ydata = [(0) for i in range(len(n_samples))]
    try:
        with open("./plc.json") as f:
            plc = json.load(f)
            ip = plc["ipAddress"]
            io_1_type, io_1_bit = get_bit(plc["Ports"]["IOport1"])
            io_2_type, io_2_bit = get_bit(plc["Ports"]["IOport2"])
            io_3_type, io_3_bit = get_bit(plc["Ports"]["IOport3"])
            io_4_type, io_4_bit = get_bit(plc["Ports"]["IOport4"])
            plc_client = ModbusTcpClient(ip)
        while True:
            start = time.time()
            input_data = plc_client.read_discrete_inputs(1024, 32)
            output_data = plc_client.read_discrete_inputs(1280, 32)

            if io_1_type == "X":
                io_1_response = int(input_data.bits[io_1_bit] == True)
            elif io_1_type == "Y":
                io_1_response = int(output_data.bits[io_1_bit] == True)
            else:
                io_1_response = -2

            if io_2_type == "X":
                io_2_response = int(input_data.bits[io_2_bit] == True)
            elif io_2_type == "Y":
                io_2_response = int(output_data.bits[io_2_bit] == True)
            else:
                io_2_response = -2

            if io_3_type == "X":
                io_3_response = int(input_data.bits[io_3_bit] == True)
            elif io_3_type == "Y":
                io_3_response = int(output_data.bits[io_3_bit] == True)
            else:
                io_3_response = -2

            if io_4_type == "X":
                io_4_response = int(input_data.bits[io_4_bit] == True)
            elif io_4_type == "Y":
                io_4_response = int(output_data.bits[io_4_bit] == True)
            else:
                io_4_response = -2

            io_1_ydata = io_1_ydata[1:] + [io_1_response]
            io_2_ydata = io_2_ydata[1:] + [io_2_response]
            io_3_ydata = io_3_ydata[1:] + [io_3_response]
            io_4_ydata = io_4_ydata[1:] + [io_4_response]

            data_io1.send(io_1_ydata)
            data_io2.send(io_2_ydata)
            data_io3.send(io_3_ydata)
            data_io4.send(io_4_ydata)

            elapsed_time = time.time() - start
            remaining_time = 0.04 - elapsed_time
            if remaining_time > 0:
                time.sleep(remaining_time)
            else:
                msg = str(f"Current acquisition rate is: {elapsed_time}")
                logger([datetime.datetime.now().strftime("%H%M%S%f"), msg])
                print("Warning: Acquisition rate is above 50ms")

    except:
        # logger([3, 5564])
        print("Please check PLC connection")
        # print(io_1.ydata)


def logger(str):
    folder = "Logs"
    today = datetime.datetime.now()

    filename = (today.strftime("%d%m%Y")) + ".csv"
    if not os.path.exists(folder):
        os.makedirs(folder)

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
