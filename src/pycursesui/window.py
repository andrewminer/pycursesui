"""Define the Window class."""

from pycursesui import AttributeMask

########################################################################################################################

ENCODING = "ascii"


########################################################################################################################

class Window(object):
    """Window provides a wrapper around a raw curses window."""

    def __init__(self, raw):
        """Create a new Window wrapper."""
        self._raw = None
        self.raw = raw

    # Properties ###################################################################################

    @property
    def raw(self):
        """Get the raw curses window wrapped by this object."""
        return self._raw

    @raw.setter
    def raw(self, value):
        if self._raw is not None:
            raise ValueError("cannot change raw once initialized")
        if value is None:
            raise ValueError("a value must be provided for raw")

        self._raw = value

    # Public Methods ###############################################################################

    def read(self, x: int, y: int, length: int=1) -> str:
        """Read a string from the screen at the given location."""
        return self.raw.instr(y, x, length).decode(ENCODING)

    def write(self, value: str, x: int, y: int, length: int=-1, attributes: AttributeMask=None):
        """
        Write a portion of a string onto the window at a certain location.

        Arguments:
            value: the string to be written
            x: the x-coordinate of where the first character should be placed
            y: the y-coordinate of where the first character should be placed
            length: the maximum number of characters to write
            attributes: an Attributes object giving the attributes to be applied
        """
        attributes = attributes if attributes is not None else AttributeMask()
        if (length >= 0) and (len(value) > length):
            value = value[0:length]

        self.raw.addstr(y, x, value, attributes.value)
        self.raw.refresh()

        return self
