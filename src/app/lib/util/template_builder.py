import re
from loguru import logger
from pathlib import Path


class TemplateBuilder:

    @staticmethod
    def build(template_path: Path or str, data: dict) -> str:
        """ Builds a configuration file from a template and the given data. """

        if not isinstance(template_path, Path):
            template_path = Path(template_path)

        template: str = template_path.read_text()
        output_lines: list = template.splitlines()
        line_template_start: int = -1
        line_template_end: int = -1

        # Evaluate the template string and determine the line numbers for the start and end of the LINES comment section

        for i, line in enumerate(output_lines):
            if line_template_start < 0 and line.strip() == '<!-- for LINE in LINES -->':
                line_template_start = i
                continue

            if line_template_start > -1 and line_template_end < 0 and line.strip() == '<!-- endfor -->':
                line_template_end = i
                break

        if line_template_start < 0 or line_template_end < 0:
            logger.debug(f'Template Start: {line_template_start}; Template End: {line_template_end};')
            raise Exception('Failed to find the line section in the template.')

        # Extract the lines section from the template
        line_template: str = '\n'.join(output_lines[line_template_start + 1:line_template_end])

        # Cache the non-repeating lines of the template for later reassembly
        output_start: list = output_lines[:line_template_start]
        output_end: list = output_lines[line_template_end + 1:]

        # Build individual line configurations
        for line_index, line in enumerate(data['lines']):
            properties: list = re.findall('<P([0-9]{1,4})>', line_template)
            line_output: str = line_template

            # Update the configuration property keys to reflect the appropriate indexes for the associated FXS port
            for config_key in properties:
                property_id: int = int(config_key) + line_index
                line_output = re.sub(f'<(/?)P{config_key}>', f'<\g<1>P' + str(property_id) + '>', line_output)

            # Update the line configuration template with data from the line's CSV input row
            for key, value in line.items():
                line_output = line_output.replace(f'$LINE.{key}', str(value))

            output_start = output_start + line_output.split('\n')

        # Reassemble the output lines
        output_lines = output_start + output_end

        return '\n'.join(output_lines)
