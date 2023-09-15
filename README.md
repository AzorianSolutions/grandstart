# Grandstart

[![CodeQL](https://github.com/AzorianSolutions/grandstart/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/AzorianSolutions/grandstart/actions/workflows/codeql-analysis.yml)

This project provides a simple CLI tool to generate Grandstream HT-812, HT-814, and HT-818 configuration files
from a CSV dataset.

## TL;DR - Linux

To get started quickly with a simple deployment, execute the following `bash` commands on a *nix based system
with `git`, `python3`, `python3-pip`, and `python3-venv` installed:

```
git clone https://github.com/AzorianSolutions/grandstart.git
cd grandstart
./deploy/bare-metal/linux/debian.sh
source venv/bin/activate
grandstart run -i /path/to/input.csv -o /path/to/output/directory
```

## TL;DR - Windows

Start with checking out the project's official repository using git. The official repository can be
cloned from `https://github.com/AzorianSolutions/grandstart.git`.

```
cd C:/Path/To/Project/Root
python3 -m venv venv
venv\Scripts\activate
pip install -e .
copy deploy\config\defaults.env deploy\config\production.env
```

Edit the default settings as needed in `deploy\config\production.env`.

Then, run the following commands each time you want to activate the project for use:

```
cd C:/Path/To/Project/Root
venv\Scripts\activate
for /F %A in (deploy\config\production.env) do SET %A
grandstart run -i C:/Path/To/Input.csv -o C:/Path/To/Output/Directory
```

## Project Documentation

### Configuration

Grandstart is configured via environment variables. Until I can provide more in-depth documentation of the project,
please refer to the default values in [deploy/config/defaults.env](./deploy/config/defaults.env) for a list of the
environment variables that can be set.

To see the concrete implementation of the settings associated with the environment variables, please see the
[src/app/config.py](./src/app/config.py) file.

### Contributing

This project is not currently accepting outside contributions. If you're interested in participating in the project,
please contact the project owner.

## [Security Policy](./.github/SECURITY.md)

Please see our [Security Policy](./.github/SECURITY.md).

## [Support Policy](./.github/SUPPORT.md)

Please see our [Support Policy](./.github/SUPPORT.md).

## [Code of Conduct](./.github/CODE_OF_CONDUCT.md)

Please see our [Code of Conduct](./.github/CODE_OF_CONDUCT.md).

## [License](./LICENSE)

This project is released under the MIT license. For additional information, [see the full license](./LICENSE).

## [Donate](https://www.buymeacoffee.com/AzorianMatt)

Like my work?

<a href="https://www.buymeacoffee.com/AzorianMatt" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

**Want to sponsor me?** Please visit my organization's [sponsorship page](https://github.com/sponsors/AzorianSolutions).
