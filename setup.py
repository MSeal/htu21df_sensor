import os
import sys
from subprocess import call
from setuptools import setup

python_2 = sys.version_info[0] == 2
def read(fname):
    with open(fname, 'rU' if python_2 else 'r') as fhandle:
        return fhandle.read()

version = '0.1.4'
required = [req.strip() for req in read('requirements.txt').splitlines() if req.strip()]
setup(
    name='htu21df',
    version=version,
    author='Matthew Seal',
    author_email='mseal007@gmail.com',
    description='A simple program for controlling an htu21d-f sensor from a Raspberry Pi',
    install_requires=required,
    license='MIT',
    packages=['htu21'],
    test_suite='tests',
    zip_safe=False,
    url='https://github.com/MSeal/htu21df_sensor',
    download_url='https://github.com/MSeal/htu21df_sensor/tarball/v' + version,
    keywords=['sensors', 'raspberry_pi', 'adafruit', 'scripting'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python'
    ]
)
