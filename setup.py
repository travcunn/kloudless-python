#!/usr/bin/env python

from setuptools import setup, find_packages
import re
import os
from os.path import join as opj

curdir = os.path.dirname(os.path.realpath(__file__))

def read(fname):
    contents = ''
    with open(fname) as f:
        contents = f.read()
    return contents

package_name = 'kloudless'

def version():
    text = read(opj(curdir, package_name, 'version.py'))
    matches = re.findall("('|\")(\S+)('|\")", text)
    return matches[0][1]

install_requires=[
    'requests>=1.0',
    'python-dateutil',
    ]

test_requires = [
    'selenium>=2.48.0',
    'pytz>=2013d',
]

if __name__ == '__main__':
    setup(
        name=package_name,
        packages=[package_name],
        include_package_data=True,
        author='Kloudless',
        author_email='hello@kloudless.com',
        version=version(),
        description = "Python library for the Kloudless API",
        long_description=read(opj(curdir, 'README.md')),
        url='https://kloudless.com/',
        install_requires=install_requires,
        license='MIT',
        classifiers=[
            'Programming Language :: Python',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            "License :: OSI Approved :: MIT License",
            "Development Status :: 4 - Beta",
            ],
        package_data={'': ['LICENSE']},
        zip_safe=False,
        tests_require = test_requires,
        )
