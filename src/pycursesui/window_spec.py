"""Unit tests for the Window class."""

import sure

from io import StringIO
from mamba import after, before, description, it

from pycursesui import Logger, Session
from pycursesui.logger import LogLevel

__all__ = []
assert sure  # prevent linter errors


########################################################################################################################

with description("Window:", "unit") as self:

    with before.each:
        self.session = None
        try:
            self.stdout = StringIO()
            self.logger = Logger().add_channel("debug", self.stdout, LogLevel.DEBUG)
            self.session = Session(self.logger).start()
            if self.session is not None:
                self.window = self.session.window
        except Exception as e:
            print(f"log:\n>>>\n{self.stdout.getvalue()}\n<<<\n")
            raise e

    with after.each:
        if self.session is not None:
            self.session.stop()

    with description("using the default window from a new session"):

        with it("doesn't contain any text in the test region"):
            self.window.read(0, 0, 10).should.equal("          ")

        with description("after writing a string into the test region"):

            with before.each:
                self.window.write("alpha", 0, 0)

            with it("now contains the written text"):
                self.window.read(0, 0, 10).should.equal("alpha     ")

        with description("after multiple overlapping writes"):

            with before.each:
                self.window.write("alpha", 0, 0).write("bravo", 3, 0)

            with it("should have replaced the last portion of the first word"):
                self.window.read(0, 0, 10).should.equal("alpbravo  ")
