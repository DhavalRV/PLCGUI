import multiprocessing
import time


def print_1():
    while True:
        print(True)
        time.sleep(0.2)


def print_0():
    while True:
        print(1)
        time.sleep(0.2)


if __name__ == "__main__":
    a = multiprocessing.Process(target=print_1)
    b = multiprocessing.Process(target=print_0, daemon=True)
    b.start()
    a.start()

    a.join()
    b.join()