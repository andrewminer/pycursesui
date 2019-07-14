"""Unit tests for the AttributeMask class."""

import curses
import sure

from mamba import before, description, it

from pycursesui import AttributeMask

__all__ = []
assert sure  # prevent linter errors


########################################################################################################################

with description("AttributeMask:", "unit") as self:

    with description("starting with a normal mask"):

        with before.each:
            self.mask = AttributeMask()

        with it("has all its flags turned off"):
            self.mask.blink.should.be.false
            self.mask.bold.should.be.false
            self.mask.underline.should.be.false

        with description("after activating one of the flags"):

            with before.each:
                self.mask.bold = True

            with it("only has the bold flag turned on"):
                self.mask.blink.should.be.false
                self.mask.bold.should.be.true
                self.mask.underline.should.be.false

            with it("has the expected value"):
                self.mask.value.should.equal(curses.A_NORMAL | curses.A_BOLD)

            with description("after switching the flag for another"):

                with before.each:
                    self.mask.bold = False
                    self.mask.underline = True

                with it("reports the flags having switched"):
                    self.mask.blink.should.be.false
                    self.mask.bold.should.be.false
                    self.mask.underline.should.be.true

                with it("reports the correct value"):
                    self.mask.value.should.equal(curses.A_NORMAL | curses.A_UNDERLINE)
