#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
   name = "nrepl-python-client",
   version = "0.0.1",
   packages = find_packages(),
   # metadata for upload to PyPI
   author = "Chas Emerick",
   author_email = "chas@cemerick.com",
   description = "A Python client for the nREPL Clojure networked-REPL server.",
   license = "BSD 3-clause",
   keywords = "clojure repl nrepl",
   url = "http://github.com/cemerick/nrepl-python-client",
   zip_safe = True,
   #test_suite = "test.testbencode"
   )

