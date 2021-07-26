"""
For development installation of the package pyintlab.

some details where taken from <https://setuptools.readthedocs.io/en/latest/>
"""
import site
import sys

import setuptools  # type: ignore[import]

site.ENABLE_USER_SITE = "--user" in sys.argv[1:]
setuptools.setup()
