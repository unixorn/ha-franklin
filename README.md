
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
  - [Configuration](#configuration)
  - [Running the Monitor](#running-the-monitor)
  - [Home Assistant](#home-assistant)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Background

I wanted a non-toy test example of using the [ha-mqtt-discoverable](https://github.com/unixorn/ha-mqtt-discoverable/tree/v0.8.1) module.

`ha-franklin` will monitor CUPSD print queues, and present a binary sensor to Home Assistant over MQTT showing whether the printer is printing.

I use this to turn the smart switch for the HP 4050N in the basement on and off so that by the time I walk downstairs from my office after printing something, Home Assistant has turned on the power to the printer and the job has at least started printing.


## Usage

### Configuration

Create a config file (yaml) with a list of dictionaries in it. Each dictionary should have the following keys:
- `mqtt_server`: DNS name or a raw IP.
- `mqtt_user`: the_mqtt_user
- `mqtt_password`: the_mqtt_password
- `name`: Franklin@cupsd
- `unique_id`: printername-cupsd
- `cupsd_queue_name`: Queue_name_on_cupsd_server
- `cupsd_server`: cupsd.example.com
- `check_interval`: 10

The easiest way to create a configuration file is to start by copying `config/config-example.yaml` and editing it to fit.

### Running the Monitor

I recommend using `docker`, `nerdctl` or `podman` to run the tooling in a container.

`docker run -v "$(pwd)/config":/config --rm unixorn/ha-franklin ha-cupsd-monitor-queues --settings-file /config/config.yaml`

### Home Assistant

The container will create a set of MQTT topics using Home Assistant's MQTT discoverability protocol so that your print queue's printing status shows up in Home Assistant.

I set up two automations - one to turn on the peanut plug my HP 4050N is plugged into when jobs appear in the cupsd queue when the sensor turns to on, and a second that turns it off once the sensor switches back to off for ten minutes.

I give it ten minutes for a couple of reasons:

First, because CUPSD will report the queue as done printing when all the postscript has been spooled to the printer. Depending on the complexity of the print job, it may take a minute or two to print the last few pages of the job, even though cupsd considers it complete. If the power gets turned off too soon, you can lose the last page or two of the job, and more annoyingly, cause a printer jam if the power cuts off while a page is moving through the paper path.

Secondly, because although I print rarely, when I do, I typically print several things within a few minutes and I'd prefer to not toggle the printer on and off more than is strictly necessary.
