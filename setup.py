# -*- coding: utf-8 -*-
"""
Written by Maksym Neyra-Nesterenko

* Data Exploration and Integration Lab (DEIL)
* Center for Special Business Projects (CSBP)
* Statistics Canada
"""
from setuptools import setup, find_packages
from glob import glob

with open("README.md", 'r') as readme:
    long_desc = readme.read()

setup(
    name='opentabulate',
    version='2.0.0',
    description='Tabulates structured data into a mergeable CSV format',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='https://github.com/CSBP-CPSE/OpenTabulate',
    author='Maksym Neyra-Nesterenko',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing :: General',
        'Topic :: Utilities',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    project_urls={
        'Documentation': 'https://opentabulate.readthedocs.io/en/stable/',
        'Source code': 'https://github.com/CSBP-CPSE/OpenTabulate/tree/master/opentabulate',
        'Bug tracker': 'https://github.com/CSBP-CPSE/OpenTabulate/issues',
        'License': 'https://github.com/CSBP-CPSE/OpenTabulate/tree/master/LICENSE.md'
    },
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.5',
    include_package_data=True,
    package_data={
        'opentabulate' : ['share/opentabulate.example.conf']
    },
    entry_points={
        'console_scripts': ['opentab=opentabulate.opentab:main']
    }
)
