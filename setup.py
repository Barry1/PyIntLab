"""For development installation of the package pyintlab.

Some details where taken from <https://setuptools.readthedocs.io/en/latest/>
"""

import site
import sys

import setuptools

site.ENABLE_USER_SITE = "--user" in sys.argv[1:]  # noqa: V101
setuptools.setup()
