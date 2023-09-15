import click
import csv
import math
import os
import subprocess
from loguru import logger
from app.cli.start import Environment, pass_environment


def calculate_devices(total_lines: int) -> tuple[int, int, int, int]:
    total_ht818: int = math.floor(total_lines / 8)
    total_ht814: int = math.floor((total_lines - total_ht818 * 8) / 4)
    total_ht812: int = math.ceil((total_lines - (total_ht818 * 8) - (total_ht814 * 4)) / 2)
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
def cli(ctx: Environment, input_file: str, output_path: str):
    """ Run the CSV conversion to process to create Grandstream configuration files."""

    lines: list = []
    line_map: dict = {}
    counters: dict = {
        'total_devices': 0,
        'total_ht812': 0,
        'total_ht814': 0,
        'total_ht818': 0,
    }

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
        total_lines: list = len(subscriber_lines)
        total_ht812: int = 0
        total_ht814: int = 0
        total_ht818: int = 0

        if not ctx.settings.use_location_id:
            # Automatically determine the spread of lines across the devices using the most conservative approach
            total_devices, total_ht812, total_ht814, total_ht818 = calculate_devices(total_lines)

            # Update statistics counters to reflect additional devices
            counters = update_counters(counters, total_devices, total_ht812, total_ht814, total_ht818)
        else:
            # Use the location ID to determine the spread of lines across the devices
            location_map: dict = {}
            total_devices = 0

            for line in subscriber_lines:
                if line['LOCATION_ID'] not in location_map:
                    location_map[line['LOCATION_ID']] = []

                location_map[line['LOCATION_ID']].append(line)

            for location_id, location_lines in location_map.items():
                total_location_lines: int = len(location_lines)

                if location_id == '':
                    location_id = 'DEFAULT'

                if total_location_lines > 0:
                    # Automatically determine the spread of lines across the devices using the most conservative approach
                    total_devices, total_ht812, total_ht814, total_ht818 = calculate_devices(total_location_lines)

                    if total_devices > 0:
                        # Update statistics counters to reflect additional devices
                        counters = update_counters(counters, total_devices, total_ht812, total_ht814, total_ht818)

                        logger.trace(
                            f"Subscriber: {subscriber_id}; Location: {location_id}; Total Lines: {total_location_lines}; Total Devices: {total_devices}; HT812: {total_ht812}; HT814: {total_ht814}; HT818: {total_ht818};")

        logger.debug(
            f"Subscriber: {subscriber_id}; Total Lines: {total_lines}; Total Devices: {total_devices}; HT812: {total_ht812}; HT814: {total_ht814}; HT818: {total_ht818};")

    logger.info(f'Total Subscriber Locations: {len(line_map)}')
    logger.info(f'Total Subscriber Lines: {len(lines)}')
    logger.info(f'Total Grandstream Devices: {counters["total_devices"]}')
    logger.info(f'Total Grandstream HT812 Devices: {counters["total_ht812"]}')
    logger.info(f'Total Grandstream HT814 Devices: {counters["total_ht814"]}')
    logger.info(f'Total Grandstream HT818 Devices: {counters["total_ht818"]}')
