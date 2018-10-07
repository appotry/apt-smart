# Automated, robust apt-get mirror selection for Debian and Ubuntu.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: June 22, 2018
# URL: https://apt-mirror-updater.readthedocs.io

"""
Reliable `end of life`_ (EOL) detection for Debian and Ubuntu releases.

Debian and Ubuntu releases have an EOL date that marks the end of support for
each release. At that date the release stops receiving further (security)
updates and some time after package mirrors stop serving the release.

The distro-info-data_ package contains CSV files with metadata about Debian and
Ubuntu releases. The :func:`gather_eol_dates()` function extracts the EOL dates
of documented Debian and Ubuntu releases from these CSV files. This enables
`apt-mirror-updater` to determine whether a given release is expected to be
available on mirrors.

To make it possible to run `apt-mirror-updater` without direct access to the
CSV files, a copy of the relevant information has been embedded in the source
code as :data:`KNOWN_EOL_DATES`.

.. _end of life: https://en.wikipedia.org/wiki/End-of-life_(product)
.. _distro-info-data: https://packages.debian.org/distro-info-data
"""

# Standard library modules.
import csv
import os
import time

# External dependencies.
from humanfriendly import parse_date
from six import StringIO

DISTRO_INFO_DIRECTORY = '/usr/share/distro-info'
"""The pathname of a directory with CSV files containing end-of-life dates (a string)."""

# [[[cog
#
# import cog
#
# from apt_mirror_updater.eol import gather_eol_dates
# from executor.contexts import LocalContext
#
# known_dates = gather_eol_dates(LocalContext())
# cog.out("\nKNOWN_EOL_DATES = {\n")
# for distributor_id, releases in sorted(known_dates.items()):
#     cog.out(" " * 4 + "%r: {\n" % str(distributor_id))
#     for codename, eol_date in sorted(releases.items()):
#         cog.out(" " * 8 + "%r: %r,\n" % (codename, eol_date))
#     cog.out(" " * 4 + "},\n")
# cog.out("}\n\n")
#
# ]]]

KNOWN_EOL_DATES = {
    'debian': {
        'bo': 920934000,
        'buzz': 865461600,
        'etch': 1266188400,
        'hamm': 952556400,
        'jessie': 1528236000,
        'lenny': 1328482800,
        'potato': 1059516000,
        'rex': 896997600,
        'sarge': 1206831600,
        'slink': 972860400,
        'squeeze': 1401487200,
        'wheezy': 1461621600,
        'woody': 1151618400,
    },
    'ubuntu': {
        'artful': 1531951200,
        'bionic': 1682460000,
        'breezy': 1176415200,
        'cosmic': 1563400800,
        'dapper': 1306879200,
        'edgy': 1209074400,
        'feisty': 1224367200,
        'gutsy': 1240005600,
        'hardy': 1368050400,
        'hoary': 1162249200,
        'intrepid': 1272578400,
        'jaunty': 1287784800,
        'karmic': 1304028000,
        'lucid': 1430258400,
        'maverick': 1334008800,
        'natty': 1351375200,
        'oneiric': 1368050400,
        'precise': 1493157600,
        'quantal': 1400191200,
        'raring': 1390777200,
        'saucy': 1405548000,
        'trusty': 1555452000,
        'utopic': 1437602400,
        'vivid': 1453503600,
        'warty': 1146348000,
        'wily': 1469138400,
        'xenial': 1618956000,
        'yakkety': 1500501600,
        'zesty': 1515798000,
    },
}

# [[[end]]]

"""
A dictionary with known Debian and Ubuntu `end of life`_ (EOL) dates.

This dictionary was generated by :func:`gather_eol_dates()` during development
of the :func:`apt_mirror_updater.eol` module based on the CSV files in the
distro-info-data_ package on an Ubuntu 18.04 system.
"""


def gather_eol_dates(context, directory=DISTRO_INFO_DIRECTORY):
    """
    Gather release `end of life`_ dates from distro-info-data_ CSV files.

    :param context: An execution context created by :mod:`executor.contexts`.
    :param directory: The pathname of a directory with CSV files containing
                      end-of-life dates (a string, defaults to
                      :data:`DISTRO_INFO_DIRECTORY`).
    :returns: A dictionary like :data:`KNOWN_EOL_DATES`.
    """
    known_dates = {}
    if context.is_directory(directory):
        for entry in context.list_entries(directory):
            filename = os.path.join(directory, entry)
            basename, extension = os.path.splitext(entry)
            if extension.lower() == '.csv':
                distributor_id = basename.lower()
                known_dates[distributor_id] = {}
                contents = context.read_file(filename)
                file_like_obj = StringIO(contents.decode('ascii'))
                for row in csv.DictReader(file_like_obj):
                    series = row.get('series')
                    eol = row.get('eol-server') or row.get('eol')
                    if series and eol:
                        eol = time.mktime(parse_date(eol) + (-1, -1, -1))
                        known_dates[distributor_id][series] = int(eol)
    return known_dates