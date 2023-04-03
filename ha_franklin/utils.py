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
import os
import yaml


def read_yaml_file(path: str):
    """
    Return the data structure contained in a yaml file

    Args:
        path (str): Path to read from

    Returns:
        Data decoded from YAML file content
    """
    with open(path) as yamlFile:
        data = yaml.safe_load(yamlFile)
        return data


def write_yaml_file(path: str, data):
    """
    Writes a data structure into a YAML file

    Args:
        path (str): Path to data file
        data (any): Data to convert and write
    """
    with open(path, "w") as yamlFile:
        yaml.safe_dump(data, yamlFile)


def valid_settings(settings: dict = {}) -> bool:
    """
    Validate that we have all settings we need

    Args:
        settings: Dictionary of settings

    Returns:
        bool of validity
    """
    fails = []
    required = (
        "cupsd_server",
        "cupsd_queue_name",
        "check_interval",
        "mqtt_server",
        "mqtt_user",
        "mqtt_password",
    )
    logging.debug(f"Settings: {settings}")
    for rs in required:
        logging.debug(f"Checking for {rs}...")
        if rs not in settings:
            fail_message = f"'{rs}' missing from settings."
            fails.append(fail_message)
            logging.critical(fail_message)
    if len(fails) > 0:
        return False
    else:
        return True


def load_monitor_settings(path: str, cli):
    """
    Load settings from a yaml file, allowing overrides from the CLI

    Args:
        path: Path to configuration file
        cli (argparse cli object): Command line options

    Returns:
        dict: A dictionary containing all of our settings
    """
    settings = {}
    # Allow overrides from command line
    if cli.cupsd_server:
        settings["cupsd_server"] = cli.cupsd_server
    if cli.cupsd_queue_name:
        settings["cupsd_queue_name"] = cli.cupsd_queue_name
    if cli.check_interval:
        settings["check_interval"] = cli.check_interval
    if cli.mqtt_server:
        settings["mqtt_server"] = cli.mqtt_server
    if cli.mqtt_password:
        settings["mqtt_password"] = cli.mqtt_password
    if cli.mqtt_user:
        settings["mqtt_user"] = cli.mqtt_user

    logging.debug(f"Processed settings: {settings}")
    return settings


def load_multiple_monitor_settings(path: str, cli):
    """
    Load settings from a yaml file

    Args:
        path: Path to configuration file
        cli (argparse cli object): Command line options

    Returns:
        dict: A dictionary containing settings for a group of CUPSD queues
    """
    if os.access(path, os.R_OK):
        settings = read_yaml_file(path=path)
    else:
        logging.error(f"Could not read {path}")
        settings = {}
    logging.debug(f"Base settings: {settings}")

    logging.debug(f"Processed settings: {settings}")
    return settings


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "[%(asctime)s][%(levelname)8s][%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s",
):
    """
    Set up logging

    Args:
        cli - An argparse cli object
    """
    log_level = getattr(logging, log_level.upper(), None)
    logging.basicConfig(level=log_level, format=log_format)
    logging.info("Log level set to %s", log_level)
    logging.debug(f"Using '{log_format}' for log format")
