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
from importlib import metadata

from ha_franklin import __version__ as VERSION
from ha_franklin.monitor import monitor_cupsd_queue, printer_unreachable
from ha_franklin.utils import load_monitor_settings, setup_logging


def cupsmon_parser(description: str = ""):
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
        help="DNS name/IP of CUPS server",
    )
    parser.add_argument(
        "--cupsd-queue-name",
        "--cups-queue-name",
        "--queue-name",
        type=str,
        help="Name of CUPS printer queue to monitor",
    )

    parser.add_argument("--mqtt-server", type=str, help="DNS name/IP of MQTT server")
    parser.add_argument(
        "--mqtt-user", "--mqtt-username", type=str, help="MQTT username"
    )
    parser.add_argument("--mqtt-password", type=str, help="MQTT password")
    parser.add_argument(
        "--check-interval", type=int, help="Number of seconds between checks"
    )

    parser.add_argument(
        "--settings-file",
        type=str,
        default="/config/ha-franklin.yaml",
        help="Path to a settings file",
    )
    return parser


def cupsmon_cli(description: str):
    """
    Parse the command line options and set up a printer monitor
    """
    parser = cupsmon_parser(
        description="Monitor a CUPS printer queue and create a set of MQTT topics compatible with Home Assistant"
    )
    cli = parser.parse_args()
    return cli


def check_cupsd_queue_status_app():
    """
    Check a CUPS queue's status
    """
    cli = cupsmon_cli(description=f"Check a CUPSD queue's status\nVersion {VERSION}")
    setup_logging(log_format=cli.log_format, log_level=cli.log_level)
    settings = load_monitor_settings(path=cli.settings_file, cli=cli)
    logging.debug(f"Settings: {settings}")
    printer = settings[0]
    status = printer_unreachable(
        server=printer["cupsd_server"], queue=printer["cupsd_queue_name"]
    )
    print(f"printer unreachable = {status}")


def monitor_cupsd_queue_app():
    """
    Create a CUPS queue monitor
    """
    cli = cupsmon_cli(description=f"Monitor a CUPSD queue\nVersion {VERSION}")
    setup_logging(log_format=cli.log_format, log_level=cli.log_level)
    settings = load_monitor_settings(path=cli.settings_file, cli=cli)
    logging.debug(f"Settings: {settings}")
    logging.info(f"Found {len(settings)} print queue definitions...")
    logging.debug("Creating thread pool...")
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(settings)
    ) as monitor_pool:
        monitor_pool.map(monitor_cupsd_queue, settings)


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
