import threading
import time


def print_1():
    while True:
        print(True)
        time.sleep(0.2)


def print_0():
    while True:
        print(1)
        time.sleep(0.2)


a = threading.Thread(target=print_1)
a.start()
b = threading.Thread(target=print_0, daemon=True)
b.start()