# Licensed under a 3-clause BSD style license - see LICENSE.rst

import os

from ._version import __version__

__all__ = [
    "IERS_A_FILE",
    "IERS_A_URL",
    "IERS_A_URL_MIRROR",
    "IERS_A_README",
    "IERS_B_FILE",
    "IERS_B_URL",
    "IERS_B_README",
    "IERS_LEAP_SECOND_FILE",
    "IERS_LEAP_SECOND_URL",
    "IETF_LEAP_SECOND_URL"
]

DATA = os.path.join(os.path.dirname(__file__), "data")

# IERS-A default file name, URL, and ReadMe with content description
IERS_A_FILE = os.path.join(DATA, "finals2000A.all")
IERS_A_URL = "https://datacenter.iers.org/data/9/finals2000A.all"
IERS_A_URL_MIRROR = "https://maia.usno.navy.mil/ser7/finals2000A.all"
IERS_A_README = os.path.join(DATA, "ReadMe.finals2000A")

# IERS-B default file name, URL, and ReadMe with content description
IERS_B_FILE = os.path.join(DATA, "eopc04.1962-now")
IERS_B_URL = "https://hpiers.obspm.fr/iers/eop/eopc04/eopc04.1962-now"
IERS_B_README = os.path.join(DATA, "ReadMe.eopc04")

# LEAP SECONDS default file name, URL, and alternative format/URL
IERS_LEAP_SECOND_FILE = os.path.join(DATA, "Leap_Second.dat")
IERS_LEAP_SECOND_URL = "https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat"
IETF_LEAP_SECOND_URL = "https://www.ietf.org/timezones/data/leap-seconds.list"

# TODO: should we include the 'IAU2000' pre-2023-style file?
IERS_B_IAU2000_README = os.path.join(DATA, "ReadMe.eopc04_IAU2000")

# TODO: rename IETF_LEAP_SECOND_URL to IERS_LEAP_SECOND_URL_MIRROR?
