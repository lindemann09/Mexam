import sys

from . import __version__
from .cli import command_line_interface

def run():
    if sys.version_info[0] != 3 or sys.version_info[1] < 10:

        raise RuntimeError("{} {} ".format("Mexam", __version__) +
                           "is not compatible with Python {0}.{1}.".format(
            sys.version_info[0],
            sys.version_info[1]) +
            "\n\nPlease use Python 3.10 or higher.")

    command_line_interface()

if __name__ == "__main__":
    run()
