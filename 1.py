###################################################################
#                                                                 #
#                     PLOTTING A LIVE GRAPH                       #
#                  ----------------------------                   #
#            EMBED A MATPLOTLIB ANIMATION INSIDE YOUR             #
#            OWN GUI!                                             #
#                                                                 #
###################################################################


import multiprocessing
import threading
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D
from matplotlib.animation import TimedAnimation
from matplotlib.figure import Figure
import sys
import os
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import numpy as np
import random as rd
import matplotlib

matplotlib.use("Qt5Agg")


def setCustomSize(x, width, height):
    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(x.sizePolicy().hasHeightForWidth())
    x.setSizePolicy(sizePolicy)
    x.setMinimumSize(QtCore.QSize(width, height))
    x.setMaximumSize(QtCore.QSize(width, height))


""""""


class CustomMainWindow(QtWidgets.QMainWindow):
    def __init__(self):

        super(CustomMainWindow, self).__init__()

        # Define the geometry of the main window
        self.setGeometry(100, 100, 1200, 500)
        self.setWindowTitle("PLC Timing Diagram")

        # Create FRAME_A
        self.FRAME_A = QtWidgets.QFrame(self)
        self.FRAME_A.setStyleSheet(
            "QWidget { background-color: %s }" % QtGui.QColor(210, 210, 235, 255).name()
        )
        self.LAYOUT_A = QtWidgets.QGridLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)

        # Place the matplotlib figure
        self.myFig = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.myFig, *(0, 1))

        # Add the callbackfunc to ..
        myDataLoop = multiprocessing.Process(
            name="myDataLoop",
            target=dataSendLoop,
            daemon=True,
            args=(self.addData_callbackFunc,),
        )
        myDataLoop.start()

        self.show()

    """"""

    def addData_callbackFunc(self, value):
        # print("Add data: " + str(value))
        self.myFig.addData(value)


""" End Class """


class CustomFigCanvas(FigureCanvas, TimedAnimation):
    def __init__(self):

        self.addedData = []

        # The data
        self.xlim = 200
        self.n = np.linspace(-self.xlim + 1, 0, self.xlim)
        self.y = self.n * 0.0
        self.yy = self.n * 0.0

        # The window
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212, sharex=self.ax1)
        # self.ax1.get_shared_x_axes().join(self.ax1, self.ax2)

        # self.ax1 settings
        self.ax1.set_xlabel("time")
        self.ax1.get_yaxis().set_visible(False)
        # self.ax1.set_ylabel("")
        self.line1 = Line2D([], [], color="blue")
        self.line1_tail = Line2D([], [], color="blue", linewidth=2)
        self.line1_head = Line2D([], [], color="blue", marker=9, markeredgecolor="b")

        self.line2 = Line2D([], [], color="blue")
        self.line2_tail = Line2D([], [], color="red", linewidth=2)
        self.line2_head = Line2D([], [], color="red", marker=9, markeredgecolor="r")

        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)

        self.ax2.add_line(self.line2)
        self.ax2.add_line(self.line2_tail)
        self.ax2.add_line(self.line2_head)

        # self.ax2.set_xlim(-self.xlim + 1, 0)
        # self.ax2.set_ylim(-0.25, 1.25)
        self.ax1.set_xlim(-self.xlim + 1, 0)
        self.ax1.set_ylim(-0.25, 1.25)

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=50, blit=True)

    def new_frame_seq(self):
        return iter(range(self.n.size))

    # def _init_draw(self):
    #     lines1 = [self.line1, self.line1_tail, self.line1_head]
    #     lines2 = [self.line2, self.line2_tail, self.line2_head]
    #     for l in lines1:
    #         l.set_data([], [])
    #     for l in lines2:
    #         l.set_data([], [])

    def addData(self, value):
        self.addedData.append(value)

    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass

    def _draw_frame(self, framedata):
        margin = 2
        while len(self.addedData) > 0:
            self.y = np.roll(self.y, -1)
            self.y[-1] = self.addedData[0]
            del self.addedData[0]

        self.line1.set_data(
            self.n[0 : self.n.size - margin], self.y[0 : self.n.size - margin]
        )
        self.line1_tail.set_data(
            np.append(self.n[-10 : -1 - margin], self.n[-1 - margin]),
            np.append(self.y[-10 : -1 - margin], self.y[-1 - margin]),
        )
        self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])
        # self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]

        # while len(self.addedData) > 0:
        #     self.yy = np.roll(self.yy, -1)
        #     self.yy[-1] = self.addedData[0]
        #     del self.addedData[0]
        self.line2.set_data(
            self.n[0 : self.n.size - margin], self.yy[0 : self.n.size - margin]
        )
        self.line2_tail.set_data(
            np.append(self.n[-10 : -1 - margin], self.n[-1 - margin]),
            np.append(self.yy[-10 : -1 - margin], self.yy[-1 - margin]),
        )
        self.line2_head.set_data(self.n[-1 - margin], self.yy[-1 - margin])
        self._drawn_artists = [
            self.line1,
            self.line1_tail,
            self.line1_head,
            self.line2,
            self.line2_tail,
            self.line2_head,
        ]


""" End Class """


# You need to setup a signal slot mechanism, to
# send data to your GUI in a thread-safe way.
# Believe me, if you don't do this right, things
# go very very wrong..
class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal(float)


""" End Class """


def dataSendLoop(addData_callbackFunc):
    # Setup the signal-slot mechanism.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)

    # Simulate some data
    n = np.linspace(0, 499, 500)
    y = {}
    # y = np.ones(n.shape)
    i = 0

    while True:
        y[i] = 1 - round(np.random.random_sample() ** 5)
        if i > 499:
            i = 0
        time.sleep(0.1)
        mySrc.data_signal.emit(y[i])  # <- Here you emit a signal!
        i += 1
    ###


###

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Plastique"))
    myGUI = CustomMainWindow()

    sys.exit(app.exec_())