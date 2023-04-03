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

import argparse
import concurrent.futures
import logging
import sys
from importlib import metadata

from ha_franklin import __version__ as VERSION
from ha_franklin.monitor import monitor_cupsd_queue, printer_unreachable
from ha_franklin.utils import (
    load_monitor_settings,
    load_multiple_monitor_settings,
    setup_logging,
)


def cupsmon_parser(description: str = "Monitor a set of CUPSD queues"):
    """
    Create a parser for ha-franklin commands

    Args:
        description: Will be used in the --help output
    Returns:
        an argparse parser
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-d", "--debug", help="Enable debug mode", action="store_true")
    parser.add_argument(
        "--log-format",
        type=str,
        help="Log format per logging module",
        default="[%(asctime)s][%(levelname)8s][%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s",
    )
    parser.add_argument(
        "--log-level",
        "--logging",
        "-l",
        type=str.upper,
        help="set log level",
        choices=["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"],
        default="INFO",
    )
    parser.add_argument(
        "--settings-file",
        type=str,
        default="/config/ha-franklin.yaml",
        help="Path to a settings file",
    )
    return parser


def cupsmon_single_queue_parser(description: str = "Monitor a single CUPSD queue"):
    """
    Create a parser for ha-franklin commands

    Args:
        description: Will be used in the --help output
    Returns:
        an argparse parser
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-d", "--debug", help="Enable debug mode", action="store_true")
    parser.add_argument(
        "--log-level",
        "--logging",
        "-l",
        type=str.upper,
        help="set log level",
        choices=["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"],
        default="INFO",
    )
    parser.add_argument(
        "--log-format",
        type=str,
        help="Log format per logging module",
        default="[%(asctime)s][%(levelname)8s][%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s",
    )

    parser.add_argument(
        "--cupsd-server",
        "--cups-server",
        "--print-server",
        type=str,
        required=True,
        help="DNS name/IP of CUPS server",
    )
    parser.add_argument(
        "--cupsd-queue-name",
        "--cups-queue-name",
        "--queue-name",
        type=str,
        required=True,
        help="Name of CUPS printer queue to monitor",
    )
    parser.add_argument(
        "--mqtt-server", type=str, required=True, help="DNS name/IP of MQTT server"
    )
    parser.add_argument(
        "--mqtt-user", "--mqtt-username", type=str, required=True, help="MQTT username"
    )
    parser.add_argument(
        "--mqtt-password", type=str, required=True, help="MQTT password"
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        help="Number of seconds between checks",
        default=10,
    )

    parser.add_argument(
        "--settings-file",
        type=str,
        default="/config/ha-franklin.yaml",
        help="Path to a settings file",
    )
    return parser


def cupsmon_cli(
    description: str = "Monitor CUPSD printer queues and create a set of MQTT topics compatible with Home Assistant",
):
    """
    Parse the command line options and set up a printer monitor
    """
    parser = cupsmon_parser(description=description)
    cli = parser.parse_args()
    return cli


def cupsmon_single_queue_cli(
    description: str = "Monitor a CUPS printer queue and create a MQTT topic compatible with Home Assistant",
):
    """
    Parse the command line options and set up a printer monitor
    """
    parser = cupsmon_single_queue_parser(description=description)
    cli = parser.parse_args()
    return cli


def check_cupsd_single_queue_status_app():
    """
    Check a CUPS queue to see if it's unreachable
    """
    cli = cupsmon_single_queue_cli(
        description=f"Check a CUPSD queue's status, version {VERSION}"
    )
    setup_logging(log_format=cli.log_format, log_level=cli.log_level)
    settings = load_monitor_settings(path=cli.settings_file, cli=cli)
    logging.info(f"Version: {VERSION}")
    logging.debug(f"Settings: {settings}")
    status = printer_unreachable(
        server=settings["cupsd_server"], queue=settings["cupsd_queue_name"]
    )
    print(f"printer unreachable = {status}")
    if status:
        sys.exit(0)
    sys.exit(1)


def check_cupsd_queue_status_app():
    """
    Check CUPS queues' statuses and present them to Home Assistant
    """
    cli = cupsmon_cli(
        description=f"Check CUPSD queues' statuses and present to Home Assistant, version {VERSION}"
    )
    setup_logging(log_format=cli.log_format, log_level=cli.log_level)
    settings = load_multiple_monitor_settings(path=cli.settings_file, cli=cli)
    logging.info(f"Version: {VERSION}")
    logging.debug(f"Settings: {settings}")
    printer = settings[0]
    status = printer_unreachable(
        server=printer["cupsd_server"], queue=printer["cupsd_queue_name"]
    )
    print(f"printer unreachable = {status}")


def monitor_cupsd_queue_app():
    """
    Create CUPS queue monitors for all queues defined in the settings file
    """
    cli = cupsmon_cli(
        description=f"Monitor CUPSD queues and present them to Home Assistant over MQTT, version {VERSION}"
    )
    setup_logging(log_format=cli.log_format, log_level=cli.log_level)
    settings = load_multiple_monitor_settings(path=cli.settings_file, cli=cli)
    logging.info(f"Version: {VERSION}")
    logging.debug(f"Settings: {settings}")
    logging.info(f"Found {len(settings)} print queue definitions...")
    logging.debug("Creating thread pool...")
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(settings)
    ) as monitor_pool:
        monitor_pool.map(monitor_cupsd_queue, settings)


def monitor_single_cupsd_queue_app():
    """
    Create CUPS queue monitors for all queues defined in the settings file
    """
    cli = cupsmon_single_queue_cli(
        description=f"Monitor CUPSD queues and present them to Home Assistant over MQTT, version {VERSION}"
    )
    setup_logging(log_format=cli.log_format, log_level=cli.log_level)
    printq_settings = load_monitor_settings(path=cli.settings_file, cli=cli)
    logging.info(f"Version: {VERSION}")
    if "unique_id" not in printq_settings:
        unique_id = (
            f"{printq_settings['cupsd_queue_name']}-{printq_settings['cupsd_server']}"
        )
        logging.warning(f"Unique ID unset, using {unique_id}")
        printq_settings["unique_id"] = unique_id
    if "name" not in printq_settings:
        name = (
            f"{printq_settings['cupsd_queue_name']}-{printq_settings['cupsd_server']}"
        )
        logging.warning(f"Unique ID unset, using {name}")
        printq_settings["name"] = name
    logging.debug(f"In singleton : Settings: {printq_settings}")
    logging.debug("Creating thread pool...")
    monitor_cupsd_queue(settings=printq_settings)


def app_summary():
    m = metadata.metadata(__package__)
    print(m["Summary"])
    print(f"Version: {VERSION}")
    print()
    print("Commands:")
    for command_name in metadata.entry_points()["console_scripts"]:
        if command_name.value.split(".")[0] == __package__:
            print(f" - {command_name.name}")


def app_version():
    print(f"Version: {VERSION}")
