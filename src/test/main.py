"""Run a sample application for pycursesui."""

import time

from pycursesui import Logger, Session

########################################################################################################################

logger = Logger()
logger.add_file_channel("main", "session.log")

with Session(logger) as session:
    session.screen.border()
    session.screen.refresh()
    time.sleep(3)
