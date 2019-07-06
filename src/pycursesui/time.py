"""Define functions for dealing with time."""

import math
import time

__all__ = [
    "humanize",
    "now",
    "sleep",
]


# Public Methods #######################################################################################################

def humanize(seconds):
    """Convert a quantity of seconds into a human-friendly display."""
    if seconds is None:
        return None
    elif seconds < 1:
        return "%dms" % (math.trunc(seconds * 1000))
    elif seconds > 60:
        minutes = seconds / 60
        return "%0.1fm" % (minutes)
    else:
        return "%0.1fs" % (seconds)


def now():
    """Return the current time as a number of seconds since the epoch start."""
    return time.perf_counter()


def sleep(duration):
    """Cause the current thread to pause for the given number of seconds."""
    return time.sleep(duration)
