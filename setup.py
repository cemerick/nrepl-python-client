'''
    nrepl-python-client
    -------------------

    A Python client for the nREPL Clojure networked-REPL server.

    Links
    `````
    * `development version <https://github.com/cemerick/nrepl-python-client>`_
'''

from setuptools import setup, find_packages

description = "A Python client for the nREPL Clojure networked-REPL server."
classifiers = ['Development Status :: 4 - Beta',
               'Environment :: Console',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: MIT License',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Topic :: Software Development :: Interpreters',
               'Topic :: Software Development :: Libraries :: Python Modules',
               'Topic :: Utilities']

setup(name="nrepl-python-client",
      version="0.0.3",
      packages=find_packages(),
      # metadata for upload to PyPI
      author="Chas Emerick",
      author_email="chas@cemerick.com",
      description=description,
      long_description=__doc__,
      test_suite='test',
      license="MIT License",
      keywords="clojure repl nrepl",
      url="https://github.com/cemerick/nrepl-python-client",
      zip_safe=True,
      platforms='any',
      classifiers=classifiers)
