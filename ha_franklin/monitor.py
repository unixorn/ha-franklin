#    Copyright 2023 Joe Block <jpb@unixorn.net>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import time

from shell import shell
from ha_franklin.utils import valid_settings
from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo

PRINTER_UNREACHABLE = "The printer is unreachable at this time."


def print_queue_jobs(server: str = "", queue: str = "") -> list:
    """
    Shows all the jobs in a given print queue

    Args:
        server: What server to query
        queue: Print queue to check
    Returns:
        list of print job lines
    """
    jobs = shell(f"lpstat -h {server} -P {queue}")
    logging.debug(f"print jobs: {jobs.output()}")
    return jobs.output()


def printer_unreachable(server: str = "", queue: str = "") -> bool:
    """
    If the printer is off when we first print, it sometimes shows as unreachable.

    We need to detect that so we can kick cupsd in the head to wake it up

    Args:
        server: What server to query
        queue: Print queue to check
    Returns:
        True if the printer is reported as unreachable
    """
    logging.debug(f"Checking {queue} on {server}...")
    jobs = shell(f"lpstat -h {server} -p {queue}").output()
    logging.warning(f"jobs: {jobs}")
    for j in jobs:
        logging.debug(f"Checking {j.strip()}")
        if j.strip() == PRINTER_UNREACHABLE:
            logging.warning(f"Found '{j.strip()}'")
            return True
    return False


def print_job_count(server: str = "", queue: str = "") -> int:
    """
    Number of print jobs in a queue
    Args:
        server: CUPSD server
        queue: Printer queue
    Returns:
        number of jobs in the queue
    """
    logging.info(f"Checking {queue} at {server} for print ...")
    jobs = print_queue_jobs(server=server, queue=queue)
    return len(jobs)


def dump_settings(settings: dict):
    logging.debug(f"CUPSD server: {settings['cupsd_server']}")
    logging.debug(f"CUPSD queue name: {settings['cupsd_queue_name']}")
    logging.debug(f"Check Interval: {settings['check_interval']}")
    logging.debug(f"MQTT password: {settings['mqtt_password']}")
    logging.debug(f"MQTT server: {settings['mqtt_server']}")
    logging.debug(f"MQTT user: {settings['mqtt_user']}")
    logging.info(f"Settings: {settings}")


def monitor_cupsd_queue(settings: dict = {}):
    """
    Monitor a cupsd queue
    """
    if not valid_settings(settings):
        raise RuntimeError(f"Invalid settings: {settings}")
    dump_settings(settings=settings)

    ha_mqtt_settings = Settings.MQTT(
        host=settings["mqtt_server"],
        username=settings["mqtt_user"],
        password=settings["mqtt_password"],
    )

    if settings["unique_id"] != "":
        cups_uid = settings["unique_id"]
        logging.info(f"Using {cups_uid} from settings as unique_id.")
    else:
        cups_uid = f"{settings['cupsd_server']}-{settings['cupsd_queue_name']}"
        logging.warning(f"No unique_id in settings, using generated {cups_uid}.")

    # Define the device. At least one of `identifiers` or `connections` must be supplied
    device_info = DeviceInfo(name=settings["name"], identifiers=cups_uid)
    logging.debug(f"Device Info created: {device_info}")

    # Associate the sensor with the device via the `device` parameter
    # `unique_id` must also be set, otherwise Home Assistant will not display the device in the UI
    print_sensor_info = BinarySensorInfo(
        name=settings["name"],
        device_class="motion",
        unique_id=cups_uid,
        device=device_info,
    )
    logging.debug(f"print_sensor_info: {print_sensor_info}")

    print_queue_settings = Settings(mqtt=ha_mqtt_settings, entity=print_sensor_info)

    # Instantiate the sensor
    print_queue_sensor = BinarySensor(print_queue_settings)
    logging.debug(f"print_queue_sensor instantiated: {print_queue_sensor}")
    print_queue_monitoring_loop(settings=settings, sensor=print_queue_sensor)


def print_queue_monitoring_loop(settings: dict = {}, sensor=None):
    while True:
        job_count = print_job_count(
            server=settings["cupsd_server"], queue=settings["cupsd_queue_name"]
        )
        logging.info(f"Found {job_count} jobs in queue")

        # Change the state of the sensor, publishing an MQTT message that gets picked up by HA
        if job_count > 0:
            logging.info(f"job count: {job_count}, setting to on")
            sensor.on()
        else:
            sensor.off()
            logging.info(f"job count: {job_count}, setting to off")
        if "check_interval" in settings:
            logging.info(f"Sleeping {settings['check_interval']}...")
            time.sleep(settings["check_interval"])
        else:
            logging.warning("check_interval not set, doing a one and done")
            return
