import logging
import signal
import threading

wait_event = threading.Event()

def default_signal_handler(signalnum, frame):
    """ default handler for all signals
    """
    if signalnum == signal.SIGINT:
        logging.debug('Signal SIGINT received')
        wait_event.set()
        return
        
    if signalnum == signal.SIGTERM:
        logging.debug('Signal SIGTERM received')
        wait_event.set()
        return

def wait_for_sigterm():
    signal.signal(signal.SIGINT, default_signal_handler)
    signal.signal(signal.SIGTERM, default_signal_handler)

    print("Waiting for termination. Press <CTRL-C> to terminate.")
    while not wait_event.wait(1):
        pass