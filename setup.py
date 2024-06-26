#!/usr/bin/python
# -*- coding: utf8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='classdict',
    version='1.15',
    author='WaterLoran',
    author_email='1696746432@qq.com',
    url='https://github.com/WaterLoran/classdict',
    download_url="http://pypi.python.org/pypi/classdict/",
    description="Access dict values as attributes (works recursively).",
    long_description=open(os.path.join(here, 'README.rst')).read() + '\n\n' +
                     open(os.path.join(here, 'CHANGES')).read(),
    license='LGPL-3.0',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords=['Tools'],
    classifiers=['Topic :: Utilities', 
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Intended Audience :: Developers',
                 'Development Status :: 5 - Production/Stable',
                 'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                 'Programming Language :: Python :: 2.5',
                 'Programming Language :: Python :: 3.6'],
)
