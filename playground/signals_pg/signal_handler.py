# code refernce:https://docs.python.org/3/library/signal.html
import signal
import os


def handler(signum, frame):
    print('Signal handler called with signal', signum)
    print(frame)


def main():
    # Set the signal handler and a 5-second alarm
    signal.signal(signal.SIGUSR1, handler)
    signal.raise_signal(signal.SIGUSR1)


if __name__ == '__main__':
    main()
