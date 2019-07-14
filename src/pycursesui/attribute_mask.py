"""Define the AttributeMask class."""

import curses


########################################################################################################################

class AttributeMask(object):
    """AttributeMask defines the attributes associated with a certain part of the screen."""

    def __init__(self, value: int=curses.A_NORMAL):
        """Create a new Attribute."""
        self._value = curses.A_NORMAL
        self.value = value

    # Properties ###################################################################################

    @property
    def value(self) -> int:
        """Get the actual numeric value underlying the mask."""
        return self._value

    @value.setter
    def value(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"value must be an int, but was a {type(value)}")

        self._value = value

    # Flag Properties ##############################################################################

    @property
    def blink(self) -> bool:
        """Get whether the text is blinking."""
        return self._read(curses.A_BLINK)

    @blink.setter
    def blink(self, value: bool):
        self._assign(curses.A_BLINK, value)

    @property
    def bold(self) -> bool:
        """Get whether the text is bolded."""
        return self._read(curses.A_BOLD)

    @bold.setter
    def bold(self, value: bool):
        self._assign(curses.A_BOLD, value)

    @property
    def dim(self) -> bool:
        """Get whether the text is dimmed."""
        return self._read(curses.A_DIM)

    @dim.setter
    def dim(self, value: bool):
        self._assign(curses.A_DIM, value)

    @property
    def standout(self) -> bool:
        """Get whether the text is standout."""
        return self._read(curses.A_STANDOUT)

    @standout.setter
    def standout(self, value: bool):
        self._assign(curses.A_STANDOUT, value)

    @property
    def underline(self) -> bool:
        """Get whether the text is underline."""
        return self._read(curses.A_UNDERLINE)

    @underline.setter
    def underline(self, value: bool):
        self._assign(curses.A_UNDERLINE, value)

    # Private ######################################################################################

    def _assign(self, flag: int, value: bool):
        if value:
            self._set(flag)
        else:
            self._clear(flag)

    def _clear(self, flag: int):
        self.value = self.value & (~ flag)

    def _read(self, flag: int) -> bool:
        return self.value & flag != 0

    def _set(self, flag: int):
        self.value = self.value | flag
