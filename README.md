
# ha-franklin

[![License](https://img.shields.io/github/license/unixorn/ha-franklin.svg)](https://opensource.org/license/apache-2-0/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub last commit (branch)](https://img.shields.io/github/last-commit/unixorn/ha-franklin/main.svg)](https://github.com/unixorn/ha-franklin)
[![Downloads](https://static.pepy.tech/badge/ha-franklin)](https://pepy.tech/project/ha-franklin)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

  - [Background](#background)
- [Usage](#usage)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Background

I wanted a non-toy test example of using [ha-mqtt-discoverable](https://github.com/unixorn/ha-mqtt-discoverable/tree/v0.8.1).

`ha-franklin` will monitor a CUPSD print queue, and present a binary sensor to Home Assistant over MQTT showing whether the printer is printing.

I use this to turn the smart switch for the HP4050N in the basement on and off so that by the time I walk downstairs from my office after printing something, Home Assistant has turned on the power to the printer and the job has started printing.


# Usage

Create a config file (yaml)
