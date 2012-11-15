import ez_setup
ez_setup.use_setuptools()

import os
import sys
from setuptools import setup

version_py = os.path.join(os.path.dirname(__file__), 'ucscsession', 'version.py')
version = open(version_py).read().strip().split('=')[-1].replace('"','')

long_description = """
Info about ``ucscsession``.
"""

setup(
        name="ucscsession",
        version=version,
        install_requires=['requests', 'beautifulsoup4', 'mechanize'],
        packages=['ucscsession',
                  'ucscsession.test',
                  'ucscsession.test.data',
                  ],
        author="Ryan Dale",
        description='ucscsession description',
        long_description=long_description,
        url="none",
        package_data = {'ucscsession':["test/data/*"]},
        package_dir = {"ucscsession": "ucscsession"},
        #scripts = ['ucscsession/scripts/example_script.py'],
        author_email="dalerr@niddk.nih.gov",
        classifiers=['Development Status :: 4 - Beta'],
    )
