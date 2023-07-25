#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

setup(
    name='mtkclient',
    version='1.6.0',
    packages=find_packages(),
    long_description=open("README.md").read(),
    scripts=['mtk','stage2'],
    data_files = ['LICENSE','README.md'],
    long_description_content_type="text/markdown",
    url='https://github.com/bkerler/mtkclient',
    project_urls={
        "Bug Tracker": "https://github.com/bkerler/mtkclient/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ],
    license='GPLv3 License',
    install_requires=[
    'colorama',
    'usb',
    'pyusb',
    'pyserial',
    'pycryptodome',
    'PySide6',
    'mock'
    ],
    author='B. Kerler',
    author_email='info@revskills.de',
    description='Mediatek reverse engineering and flashing tools',
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False
)
