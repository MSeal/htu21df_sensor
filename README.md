[![Build Status](https://travis-ci.org/MSeal/htu21df_sensor.svg?branch=master)](https://travis-ci.org/MSeal/htu21df_sensor)

# htu21df Sensor Library
A lightweight library for talking to an htu21df sensor over i2c. Supports python 2 or 3.

## Installation
Use pip:

	pip install htu21df

Or from any download, install with setup:

    python setup.py install

## How to Use
It's very straight forward.

	from htu21 import HTU21
    htu = HTU21()
    print(htu.read_temperature())
    print(htu.read_humidity())

Running the htu file directly will print the above results.

	python -m htu21.htu21

## Why?
It turns out that the expected interface with the htu21df sensor is a little off the standard i2c library interfaces. To get it to work on a raspberry pi took a lot of headbanging and soul searching. So instead of having others repeat the pain, I made this library which makes (semi) direct calls to the i2c io which match the sensor perfectly. I also added in a bunch of internal patches for python2 vs python3 so both can work without rewriting all the byte-level interfaces.

## Author
Author(s): Matthew Seal

## License
MIT
