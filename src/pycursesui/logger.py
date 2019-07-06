"""Define the Logger class."""

import sys
import traceback

from enum import Enum
from io import IOBase, FileIO, TextIOWrapper

from pycursesui import time

__all__ = ["LogLevel", "Logger"]


########################################################################################################################

INDENT_TEXT = "    "
TIME_WIDTH = 6


class LogLevel(Enum):
    """LogLevel describes how urgent a specific log message is."""

    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4


########################################################################################################################

class LogChannel(object):

    def __init__(self, name, stream, level=LogLevel.INFO, eraseable=False, global_start_time=None):
        self.eraseable = eraseable
        self.global_start_time = global_start_time or time.now()
        self.indent_count = 0
        self.level = level
        self.name = name
        self.stream = stream

        self._eraseable_text = None
        self._last_time = time.now()

    # Public Methods ###############################################################################

    def append_eraseable(self, text):
        if not self.eraseable:
            return

        self._eraseable_text = text
        print(text, file=self.stream, end="", flush=True)

    def close(self):
        print("\n", file=self.stream)
        self.stream.flush()

        if not ((self.stream is sys.stdout) or (self.stream is sys.stderr)):
            self.stream.close()

    def erase(self):
        if (not self.eraseable) or (self._eraseable_text is None):
            return

        c = len(self._eraseable_text)
        text = ("\b" * c) + (" " * c) + ("\b" * c)
        print(text,  file=self.stream, end="", flush=True)
        self._eraseable_text = None

    def write(self, level, entry, append=False):
        if not self._is_writable_level(level):
            return

        self.erase()
        text = entry() if callable(entry) else str(entry)
        for message in text.splitlines():
            self._write_message(level, message, append=append)
            append = False

        return self

    # Private Methods ##############################################################################

    def _is_writable_level(self, level):
        if not isinstance(level, LogLevel):
            raise TypeError(f"level should be a LogLevel but was a {type(level)}")
        return level.value >= self.level.value

    def _write_message(self, level, message, append=False):
        if not append:
            now = time.now()
            cumulative_time = time.humanize(now - self.global_start_time).rjust(TIME_WIDTH)
            delta_time = time.humanize(now - self._last_time).rjust(TIME_WIDTH)
            self._last_time = now

            level = level.name.rjust(5)
            indent = INDENT_TEXT * self.indent_count
            prefix = f"\n[{cumulative_time} (+{delta_time}) {level}]{indent} "
        else:
            prefix = ""

        print(f"{prefix}{message}", file=self.stream, end="", flush=True)


########################################################################################################################

class Logger(object):
    """Logger provides a simple interface for writing filtered status information to a variety of sources."""

    def __init__(self):
        """Create a new logger."""
        self._channels = {}
        self._global_start_time = time.now()
        self._indent_count = 0

    # Channel Methods ##############################################################################

    def add_channel(self, name, stream, level=LogLevel.INFO, eraseable=False):
        """Add a new channel to this logger."""
        if not isinstance(name, str):
            raise TypeError(f"name must be a str, but was a {type(name)}")
        if not isinstance(stream, IOBase):
            raise TypeError(f"stream must be an IOBase, but was a {type(stream)}")
        if not isinstance(level, LogLevel):
            raise TypeError("level must be a LogLevel, but was a {type(level)}")
        if self.has_channel(name):
            raise ValueError("{name} is already registered as a channel on this logger")

        self._channels[name] = LogChannel(name, stream, level, eraseable, self._global_start_time)
        return self

    def add_console_channel(self, level=LogLevel.INFO):
        """Add a channel called "console" to write data to stdout."""
        self.add_channel("console", sys.stdout, level, eraseable=True)
        return self

    def add_file_channel(self, name, file_name, level=LogLevel.INFO):
        """Add a channel with a given name to write to a file."""
        self.add_channel(name, TextIOWrapper(FileIO(file_name, "w")), level)
        return self

    def clear_channels(self):
        """Remove all registered channels."""
        for channel_name in self.list_channels():
            self.remove_channel(channel_name)
        return self

    def has_channel(self, name):
        """Determine whether this logger has a certain channel."""
        return name in self._channels

    def list_channels(self):
        """List the names of all registered channels."""
        return list(self._channels.keys())

    def remove_channel(self, name):
        """Remove a certain channel from this logger."""
        if self.has_channel(name):
            self._channels[name].close()
            del self._channels[name]
        return self

    def set_channel_level(self, name, level):
        """Change the log level of a certain channel."""
        if not isinstance(level, LogLevel):
            raise TypeError(f"level must be a LogLevel, but was a {type(level)}")
        if not self.has_channel(name):
            raise ValueError(f"{name} is not a channel on this logger")

        self._channels[name].level = level
        return self

    # Logging Methods ##############################################################################

    def trace(self, entry, append=False):
        """Write a entry at TRACE level."""
        return self.write(LogLevel.TRACE, entry, append)

    def debug(self, entry, append=False):
        """Write a entry at DEBUG level."""
        return self.write(LogLevel.DEBUG, entry, append)

    def info(self, entry, append=False):
        """Write a entry at INFO level."""
        return self.write(LogLevel.INFO, entry, append)

    def warn(self, entry, append=False):
        """Write a entry at the WARN level."""
        return self.write(LogLevel.WARN, entry, append)

    def error(self, entry=None, error=None, append=False):
        """Write a entry at the ERROR level."""
        if (entry is None) and (error is None):
            return

        def _build_message():
            message = ""
            if entry is not None:
                message += entry() if callable(entry) else str(entry)
            if error is not None:
                needs_delimiter = False
                for line in traceback.format_exception(type(error), error, error.__traceback__):
                    line = line.rstrip()
                    if line != "":
                        if needs_delimiter:
                            message += "\n"
                        needs_delimiter = True
                        message += f"{INDENT_TEXT}{line}"
            return message

        return self.write(LogLevel.ERROR, _build_message, append)

    # Public Methods ###############################################################################

    def append_eraseable(self, text):
        """Append a chunk of eraseable text."""
        for channel in self._channels.values():
            channel.append_eraseable(text)

    def close(self):
        """Close all channels and remove them from this logger."""
        return self.clear_channels()

    def erase(self):
        """Erase the last chunk of eraseable text written to this logger."""
        for channel in self._channels.values():
            channel.erase()

    def indent(self):
        """Indent the log by one level."""
        self._indent_count += 1
        for channel in self._channels.values():
            channel.indent_count = self._indent_count
        return self

    def indented(self):
        """Use this logger in a `with` statement."""
        logger = self

        class LoggerIndentContext(object):
            def __enter__(self):
                logger.indent()
                return logger

            def __exit__(self, type, value, trace):
                logger.outdent()
                return False

        return LoggerIndentContext()

    def outdent(self):
        """Outdent the log by one level."""
        self._indent_count = max(0, self._indent_count - 1)
        for channel in self._channels.values():
            channel.indent_count = self._indent_count
        return self

    def set_level(self, level):
        """Change the level for all channels at once."""
        if not isinstance(level, LogLevel):
            raise TypeError(f"level must be a LogLevel, but was a {type(level)}")
        for channel_name in self.list_channels():
            self.set_channel_level(channel_name, level)
        return self

    def write(self, level, entry, append=False):
        """Write a message to each channel registered with this logger."""
        if not isinstance(level, LogLevel):
            raise TypeError(f"level must be a LogLevel, but was a {type(level)}")
        append = bool(append)

        for channel in self._channels.values():
            channel.write(level, entry, append=append)
        return self
