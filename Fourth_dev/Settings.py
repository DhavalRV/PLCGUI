from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLineEdit,
    QApplication,
    QLabel,
    QSpinBox,
)
import sys
import os
import json


class StringBox(QSpinBox):
    def __init__(self, strings, parent=None):
        super(StringBox, self).__init__(parent)
        self.setStrings(strings)

    def strings(self):
        return self._strings

    def setStrings(self, strings):
        self._strings = tuple(strings)
        self._values = dict(zip(strings, range(len(strings))))
        self.setRange(0, len(strings) - 1)
        self.resize(40, 20)

    def textFromValue(self, value):
        return self._strings[value]

    def valueFromText(self, text):
        return self._values[text]


class IOPort(QWidget):
    def __init__(self, name, init, parent=None):
        super().__init__(parent)
        self.UI(name, init)

    def UI(self, name, init_ioport):
        init_io = init_ioport[0]
        init_port = self.convert_to_decimal(int(init_ioport.split(init_io)[1]))

        self.ioport_combo = QHBoxLayout(self)
        self.label = QLabel(name)
        self.label.setMinimumSize(54, 20)

        self.io_spinbox = StringBox(strings=["X", "Y", "M"])
        self.io_spinbox.setValue(self.io_spinbox.valueFromText(text=init_io))
        self.io_spinbox.setMinimumSize(33, 20)

        self.port_spinbox = QSpinBox()
        self.port_spinbox.setDisplayIntegerBase(8)
        self.port_spinbox.setValue(init_port)
        self.port_spinbox.setMinimumSize(43, 20)
        self.port_spinbox.setMaximum(1750)

        self.ioport_combo.addWidget(self.label)
        self.ioport_combo.addWidget(self.io_spinbox)
        self.ioport_combo.addWidget(self.port_spinbox)
        self.ioport_combo.setSpacing(0)

        self.io_spinbox.setStyleSheet(
            "background-color: #6d6d6d; outline-color:#ffffff"
        )
        self.port_spinbox.setStyleSheet(
            "background-color: #6d6d6d; outline-color:#ffffff"
        )

    def convert_to_octal(self, decimal_number):
        octalNum = 0
        countval = 1
        dNo = decimal_number

        while decimal_number != 0:

            # decimals remainder is calculated
            remainder = decimal_number % 8

            # storing the octalvalue
            octalNum += remainder * countval

            # storing exponential value
            countval = countval * 10
            decimal_number //= 8
        return str(octalNum)

    def convert_to_decimal(self, octal_number):
        decimal_value = 0
        base = 1

        while octal_number:
            last_digit = octal_number % 10
            octal_number = int(octal_number / 10)
            decimal_value += last_digit * base
            base = base * 8
        return decimal_value

    def ret_value(self):
        port = self.convert_to_octal(self.port_spinbox.value())
        io = self.io_spinbox.textFromValue(self.io_spinbox.value())
        # print(io + port)
        return io + port


class SettingWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()

    # def initUI(self):

    #     # Add button
    #     self.btn = QPushButton("Settings", self)
    #     self.btn.move(30, 20)
    #     self.btn.clicked.connect(self.SettingsDiag)

    #     # Add label

    #     self.setGeometry(300, 300, 290, 150)
    #     self.setWindowTitle("Main Window")
    #     self.show()

    def SettingsDiag(self):

        with open("./plc.json") as f:
            plc = json.load(f)
            title = plc["Title"]
            ip = plc["ipAddress"]
            io_1 = plc["Ports"]["IOport1"]
            io_2 = plc["Ports"]["IOport2"]
            io_3 = plc["Ports"]["IOport3"]
            io_4 = plc["Ports"]["IOport4"]
            clear = plc["clear_flags"]

        self.dialog = QDialog()
        self.dialog.setWindowTitle("Settings")
        self.dialog.resize(310, 230)

        self.title_label = QLabel("Title :", self.dialog)
        self.title_label.setGeometry(10, 10, 85, 20)
        self.ip_label = QLabel("PLC IP Address :", self.dialog)
        self.ip_label.setGeometry(10, 40, 85, 20)

        self.title_edit = QLineEdit(self.dialog)
        self.title_edit.setGeometry(110, 10, 190, 20)
        self.title_edit.setText(title)

        self.ip_edit = QLineEdit(self.dialog)
        self.ip_edit.setGeometry(110, 40, 190, 20)
        self.ip_edit.setInputMask("000.000.000.000")
        self.ip_edit.setMaxLength(15)
        self.ip_edit.setText(ip)

        self.port1_control = IOPort("I/O Port 1 :", parent=self.dialog, init=io_1)
        self.port1_control.move(0, 80)
        self.port2_control = IOPort("I/O Port 2 :", parent=self.dialog, init=io_2)
        self.port2_control.move(160, 80)
        self.port3_control = IOPort("I/O Port 3 :", parent=self.dialog, init=io_3)
        self.port3_control.move(0, 120)
        self.port4_control = IOPort("I/O Port 4 :", parent=self.dialog, init=io_4)
        self.port4_control.move(160, 120)
        self.clear_flags = QCheckBox(
            "Check to reset memory states after trigger", self.dialog
        )
        self.clear_flags.setGeometry(10, 160, 300, 20)
        self.clear_flags.setChecked(bool(clear))

        self.okbtn = QPushButton("Apply", self.dialog)
        self.okbtn.setGeometry(140, 200, 75, 20)
        self.closebtn = QPushButton("Cancel", self.dialog)
        self.closebtn.setGeometry(225, 200, 75, 20)
        # self.btns.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.closebtn.clicked.connect(self.dialog.close)
        self.okbtn.clicked.connect(self.restart_program)
        # self.btns.move(100, 160)

        self.dialog.setStyleSheet(
            "background-color: #1b1b1b; color:#ffffff; selection-background-color:#1b1b1b"
        )
        self.title_edit.setStyleSheet(
            "background-color: #6d6d6d; outline-color:#ffffff"
        )
        self.ip_edit.setStyleSheet("background-color: #6d6d6d; outline-color:#ffffff")

        self.okbtn.setStyleSheet("background-color: #424242; outline-color:#ffffff")
        self.closebtn.setStyleSheet("background-color: #424242; outline-color:#ffffff")

        self.dialog.exec_()

    def restart_program(self):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""

        data = {}
        Ports = {}
        data["Title"] = self.title_edit.text()
        data["ipAddress"] = self.ip_edit.text()
        Ports["IOport1"] = self.port1_control.ret_value()
        Ports["IOport2"] = self.port2_control.ret_value()
        Ports["IOport3"] = self.port3_control.ret_value()
        Ports["IOport4"] = self.port4_control.ret_value()
        data["Ports"] = Ports
        data["clear_flags"] = self.clear_flags.isChecked()

        with open("./plc.json", "w") as f:
            json.dump(data, f, indent=4)
        python = sys.executable
        os.execl(python, python, *sys.argv)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SettingWindow()
    sys.exit(app.exec_())