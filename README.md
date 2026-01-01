# thermopro-tp25-ble

[![PyPI](https://img.shields.io/pypi/v/thermopro-tp25-ble.svg)](https://pypi.org/project/thermopro-tp25-ble/)
[![Tests](https://github.com/kwood1992/thermopro-tp25-ble/actions/workflows/test.yml/badge.svg)](https://github.com/kwood1992/thermopro-tp25-ble/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/kwood1992/thermopro-tp25-ble?include_prereleases&label=changelog)](https://github.com/kwood1992/thermopro-tp25-ble/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/kwood1992/thermopro-tp25-ble/blob/main/LICENSE)

Thermopro TP25 BLE Library

Shoutout to https://martys.blog/posts/thermopro-3-raw-data for useful information on decoding probe temperature readings!

## Known Issues
* Battery level is nowhere near right.
    * If someone has this thermometer, lab bench power supply and grabs the device raw data that'll be most helpful

## Future Releases
* Set the probes type (e.g.: ambient or food internal temp)
* Set the ambient low and high thresholds
* Set the food internal temp goal
* Silence the hub alarm

## Installation

Install this library using `pip`:
```bash
pip install thermopro-tp25-ble
```
## Usage

Usage instructions go here.

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:
```bash
cd thermopro-tp25-ble
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
python -m pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
