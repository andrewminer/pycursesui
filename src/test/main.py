"""Run a sample application for pycursesui."""

import time

from pycursesui import Logger, Session

########################################################################################################################

logger = Logger().add_file_channel("main", "session.log")

with Session(logger) as session:
    session.window.write("alpha", 10, 10)
    time.sleep(1)
    session.window.write("bravo", 10, 11)
    time.sleep(1)
    session.window.write("charlie", 10, 12)
    time.sleep(3)
