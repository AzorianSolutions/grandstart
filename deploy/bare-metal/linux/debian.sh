#!/usr/bin/env bash

root_path=$(pwd)
config_path=${1:-/etc/grandstart/grandstart.env}
source_path=${2:-$root_path/deploy/config/defaults.env}
GRST_SECRET_KEY=$(echo $RANDOM | sha256sum | head -c 64; echo;)

rm -fr venv
python3 -m venv venv
source venv/bin/activate

pip install -e .

sudo rm -fr "$config_path"
sudo mkdir -p "$(dirname "$config_path")"
sudo cp "$source_path" "$config_path"

export GRST_ENV_FILE=$config_path
export GRST_SECRET_KEY

GRST_SALT=$(grst gen_salt -r)

{
  echo ""
  echo "GRST_SALT=$GRST_SALT"
  echo "GRST_SECRET_KEY=$GRST_SECRET_KEY"
} | sudo tee -a "$GRST_ENV_FILE"
