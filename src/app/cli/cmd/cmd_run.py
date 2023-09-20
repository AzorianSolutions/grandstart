import click
import csv
import math
import os
import subprocess
from loguru import logger
from pathlib import Path
from app.cli.start import Environment, pass_environment
from app.lib.util.template_builder import TemplateBuilder


def calculate_devices(total_lines: int) -> tuple[int, int, int, int]:
    total_ht818: int = max(1 if 4 < total_lines < 8 else math.floor(total_lines / 8), 0)
    total_ht814: int = max(math.floor((total_lines - total_ht818 * 8) / 4), 0)
    total_ht812: int = max(math.ceil((total_lines - (total_ht818 * 8) - (total_ht814 * 4)) / 2), 0)
    total_devices = total_ht812 + total_ht814 + total_ht818
    return total_devices, total_ht812, total_ht814, total_ht818


def update_counters(counters: dict, total_devices: int, total_ht812: int, total_ht814: int, total_ht818: int) -> dict:
    counters['total_devices'] += total_devices
    counters['total_ht812'] += total_ht812
    counters['total_ht814'] += total_ht814
    counters['total_ht818'] += total_ht818
    return counters


@click.command("run", short_help="Run the CSV conversion to process to create Grandstream configuration files.")
@click.option('-i', '--input', 'input_file', type=click.Path(exists=True), help='The subscriber line CSV file.')
@click.option('-o', '--output', 'output_path', type=click.Path(exists=True),
              help='The output directory for the configuration files.')
@pass_environment
def cli(ctx: Environment, input_file: Path or str, output_path: Path or str):
    """ Run the CSV conversion to process to create Grandstream configuration files."""

    # Convert the given paths to Path instances if not already
    if not isinstance(input_file, Path):
        input_file = Path(input_file)

    if not isinstance(output_path, Path):
        output_path = Path(output_path)

    lines: list = []
    line_map: dict = {}
    counters: dict = {
        'total_devices': 0,
        'total_ht812': 0,
        'total_ht814': 0,
        'total_ht818': 0,
    }
    output: dict = {}

    logger.info(f"Subscriber Line CSV File: {input_file}")
    logger.info(f"Grandstream Configuration File Path: {output_path}")

    with open(input_file, 'r') as file:
        csvreader = csv.DictReader(file)
        for row in csvreader:
            lines.append(row)

            if row['SUBSCRIBER_ID'] not in line_map:
                line_map[row['SUBSCRIBER_ID']] = []

            line_map[row['SUBSCRIBER_ID']].append(row)

    for subscriber_id, subscriber_lines in line_map.items():
        total_lines: int = len(subscriber_lines)
        total_subscriber_devices: int = 0
        total_subscriber_ht812: int = 0
        total_subscriber_ht814: int = 0
        total_subscriber_ht818: int = 0

        if not ctx.settings.use_demarcation_id:
            # Automatically determine the spread of lines across the devices using the most conservative approach
            total_devices, total_ht812, total_ht814, total_ht818 = calculate_devices(total_lines)
            total_subscriber_devices += total_devices
            total_subscriber_ht812 += total_ht812
            total_subscriber_ht814 += total_ht814
            total_subscriber_ht818 += total_ht818

            # Update statistics counters to reflect additional devices
            counters = update_counters(counters, total_devices, total_ht812, total_ht814, total_ht818)
        else:
            # Use the location ID to determine the spread of lines across the devices
            location_map: dict = {}

            for line in subscriber_lines:
                if line['DEMARCATION_ID'] not in location_map:
                    location_map[line['DEMARCATION_ID']] = []

                location_map[line['DEMARCATION_ID']].append(line)

            for demarcation_id, location_lines in location_map.items():
                total_location_lines: int = len(location_lines)

                if demarcation_id == '':
                    demarcation_id = 'DEFAULT'

                total_ht812: int = 0
                total_ht814: int = 0
                total_ht818: int = 0

                if total_location_lines > 0:
                    # Automatically determine the spread of lines across the devices using a conservative approach
                    total_devices, total_ht812, total_ht814, total_ht818 = calculate_devices(total_location_lines)
                    total_subscriber_devices += total_devices
                    total_subscriber_ht812 += total_ht812
                    total_subscriber_ht814 += total_ht814
                    total_subscriber_ht818 += total_ht818

                    if total_devices > 0:
                        # Update statistics counters to reflect additional devices
                        counters = update_counters(counters, total_devices, total_ht812, total_ht814, total_ht818)

                        logger.trace(
                            f"Subscriber: {subscriber_id}; Location: {demarcation_id}; "
                            + f"Total Lines: {total_location_lines}; Total Devices: {total_devices}; "
                            + f"HT812: {total_ht812}; HT814: {total_ht814}; HT818: {total_ht818};")

                remaining_lines: list = location_lines.copy()
                tpl_path: Path = Path('src/app/templates/grandstream.cfg.tpl')

                # Build device configuration files from templates for Grandstream HT818 devices
                for i in range(0, total_ht818):
                    if len(remaining_lines) < 1:
                        break

                    device_id: str = f"{subscriber_id}-{demarcation_id}-ht818-{i + 1}"
                    config_path: Path = Path(output_path / (device_id + '.cfg'))
                    last_index: int = max(7, len(remaining_lines) - 1)
                    config_data: dict = {
                        'lines': remaining_lines[0:last_index],
                    }

                    # Cache a reference for the device configuration, and it's output path
                    output[config_path] = TemplateBuilder.build(tpl_path, config_data)

                    # Remove the lines that were just processed
                    remaining_lines = remaining_lines[last_index + 1:]

                    logger.trace(f"Subscriber: {subscriber_id}; Location: {demarcation_id}; Device: {device_id}; "
                                 + f"Lines: {len(config_data['lines'])};")

                # Build device configuration files from templates for Grandstream HT814 devices
                for i in range(0, total_ht814):
                    if len(remaining_lines) < 1:
                        break

                    device_id: str = f"{subscriber_id}-{demarcation_id}-ht814-{i + 1}"
                    config_path: Path = Path(output_path / (device_id + '.cfg'))
                    last_index: int = max(3, len(remaining_lines) - 1)
                    config_data: dict = {
                        'lines': remaining_lines[0:last_index],
                    }

                    # Cache a reference for the device configuration, and it's output path
                    output[config_path] = TemplateBuilder.build(tpl_path, config_data)

                    # Remove the lines that were just processed
                    remaining_lines = remaining_lines[last_index + 1:]

                    logger.trace(f"Subscriber: {subscriber_id}; Location: {demarcation_id}; Device: {device_id}; "
                                 + f"Lines: {len(config_data['lines'])};")

                # Build device configuration files from templates for Grandstream HT812 devices
                for i in range(0, total_ht812):
                    if len(remaining_lines) < 1:
                        break

                    device_id: str = f"{subscriber_id}-{demarcation_id}-ht812-{i + 1}"
                    config_path: Path = Path(output_path / (device_id + '.cfg'))
                    last_index: int = max(1, len(remaining_lines) - 1)
                    config_data: dict = {
                        'lines': remaining_lines[0:last_index],
                    }

                    # Cache a reference for the device configuration, and it's output path
                    output[config_path] = TemplateBuilder.build(tpl_path, config_data)

                    # Remove the lines that were just processed
                    remaining_lines = remaining_lines[last_index + 1:]

                    logger.trace(f"Subscriber: {subscriber_id}; Location: {demarcation_id}; Device: {device_id}; "
                                 + f"Lines: {len(config_data['lines'])};")

        logger.debug(
            f"Subscriber: {subscriber_id}; Total Lines: {total_lines}; Total Devices: {total_subscriber_devices}; "
            + f"HT812: {total_subscriber_ht812}; HT814: {total_subscriber_ht814}; HT818: {total_subscriber_ht818};")

    # Write the device configuration files to disk
    for config_path, config_contents in output.items():
        with open(config_path, 'w') as f:
            f.write(config_contents)
            f.close()

    logger.info(f'Total Subscriber Locations: {len(line_map)}')
    logger.info(f'Total Subscriber Lines: {len(lines)}')
    logger.info(f'Total Grandstream Devices: {counters["total_devices"]}')
    logger.info(f'Total Grandstream HT812 Devices: {counters["total_ht812"]}')
    logger.info(f'Total Grandstream HT814 Devices: {counters["total_ht814"]}')
    logger.info(f'Total Grandstream HT818 Devices: {counters["total_ht818"]}')
