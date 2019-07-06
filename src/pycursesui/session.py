"""Define the Session class."""

import curses

from pycursesui import Logger

__all__ = ["Session"]


########################################################################################################################

class Session(object):
    """Session sets up everything needed to begin working with curses."""

    def __init__(self, logger=None):
        """Create a new Session."""
        self._screen = None
        self.logger = logger

    # Properties ###################################################################################

    @property
    def is_running(self) -> bool:
        """Get whether the session is currently active."""
        return (self.screen is not None)

    @property
    def logger(self) -> Logger:
        """Get the logger used by this session."""
        return self._logger

    @logger.setter
    def logger(self, value: Logger):
        if value is None:
            value = Logger()
        self._logger = value

    @property
    def screen(self):
        """Get the screen associated with this session (if any)."""
        return self._screen

    # Magic Methods ################################################################################

    def __enter__(self):
        """Enter a session."""
        self.logger.info("Starting curses session")
        try:
            self._screen = curses.initscr()
        except Exception as e:
            self.logger.error("Could not initialize a curses screen", e)
            curses.endwin()
            raise e

        try:
            curses.noecho()
        except Exception as e:
            self.logger.error("Could not set up no ech mode", e)
            curses.echo()
            curses.endwin()
            raise e

        try:
            curses.cbreak()
        except Exception as e:
            self.logger.error("Could not set up character break mode", e)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            raise e

        try:
            self.screen.keypad(True)
        except Exception as e:
            self.logger.error("Could not set up keypad", e)
            self.screen.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            raise e

        return self

    def __exit__(self, type, value, traceback):
        """Exit a session."""
        self.logger.info("Shutting down curses session")
        try:
            self.screen.keypad(False)
        except Exception as e:
            self.logger.error("Could not reset keypad", e)

        try:
            curses.nocbreak()
        except Exception as e:
            self.logger.error("Could not reset character break mode", e)

        try:
            curses.echo()
        except Exception as e:
            self.logger.error("Could not reset echo mode", e)

        try:
            curses.endwin()
        except Exception as e:
            self.logger.error("Could not shut down curses session", e)

        self._screen = None

        return False
