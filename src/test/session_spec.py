"""Integration tests for the Session class."""

import sure

from mamba import before, description, it

from pycursesui import Session

__all__ = []
assert sure  # prevent linter errors


########################################################################################################################

with description("Session:", "integration") as self:

    with before.each:
        self.session = Session()

    with it("can enter an exit a session without errors"):
        def _func():
            with self.session as s:
                print(f'{s}')

        _func.shouldnt.throw()
