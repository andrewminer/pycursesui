"""Define the Session class."""

import curses

from pycursesui import Logger, Window
from typing import Callable, Tuple

__all__ = ["Session"]


########################################################################################################################

class Session(object):
    """Session sets up everything needed to begin working with curses."""

    def __init__(self, logger=None):
        """Create a new Session."""
        self._window = None
        self.logger = logger

    # Properties ###################################################################################

    @property
    def is_running(self) -> bool:
        """Get whether the session is currently active."""
        return (self.window is not None)

    @property
    def logger(self) -> Logger:
        """Get the logger used by this session."""
        return self._logger

    @logger.setter
    def logger(self, value: Logger):
        value = value if value is not None else Logger()
        self._logger = value

    @property
    def window(self) -> Window:
        """Get the window associated with this session (if any)."""
        return self._window

    # Public Methods ###############################################################################

    def start(self) -> "Session":
        """
        Start a new session.

        This will take over the current TTY and begin a curses session. The main window will be available from this
        object's `window` property. The `stop` method *must* be called to restore the TTY back to its original
        condition.
        """
        self.logger.info("Starting curses session")

        raw_window, error = self._attempt(lambda: curses.initscr())
        if raw_window:
            self._window = Window(raw_window)
        if error:
            self.logger.error("could not initialize a curses window", error)
            self._attempt(lambda: curses.endwin())
            return None

        _, error = self._attempt(lambda: curses.start_color())
        if error:
            self.logger.error("could not start color session", error)
            self._attempt(lambda: curses.endwin())

        _, error = self._attempt(lambda: curses.noecho())
        if error:
            self.logger.error("Could not set up no echo mode", error)
            self._attempt(lambda: curses.echo())
            self._attempt(lambda: curses.endwin())

        _, error = self._attempt(lambda: curses.cbreak())
        if error:
            self.logger.error("Could not set up chracter break mode", error)
            self._attempt(lambda: curses.cnobreak())
            self._attempt(lambda: curses.echo())
            self._attempt(lambda: curses.endwin())

        _, error = self._attempt(lambda: raw_window.keypad(True))
        if error:
            self.logger.error("Could not set up keypad", error)
            self._attempt(lambda: raw_window.keypad(False))
            self._attempt(lambda: curses.cnobreak())
            self._attempt(lambda: curses.echo())
            self._attempt(lambda: curses.endwin())

        return self

    def stop(self) -> "Session":
        """Stop the current session."""
        self.logger.info("Shutting down curses session")
        self._attempt(lambda: self.window.raw.keypad(False))
        self._attempt(lambda: curses.nocbreak())
        self._attempt(lambda: curses.echo())
        self._attempt(lambda: curses.endwin())

        self._window = None
        return self

    # Magic Methods ################################################################################

    def __enter__(self) -> "Session":
        """Enter a session."""
        return self.start()

    def __exit__(self, type, value, traceback):
        """Exit a session."""
        self.stop()
        return False

    # Private Methods ##############################################################################

    def _attempt(self, task: Callable) -> Tuple[object, Exception]:
        result, error = None, None
        try:
            result = task()
        except Exception as e:
            error = e

        return result, error
