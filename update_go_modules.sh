#!/bin/bash

MANIFEST="com.simulide.simulide.yml"
DIR="$PWD/generate_sources"

# Create folders and set go path

mkdir -p $DIR; rm -rf $DIR/*

mkdir $DIR/go
export GOPATH=$DIR/go

# Extract versions from yaml

BASE_URL="https://github.com/go-task/task/archive/refs/tags/"
line=$(grep "$BASE_URL" "$MANIFEST")
task_ver=$(echo "$line" | grep -oP "(?<=${BASE_URL}v)[0-9]+\.[0-9]+\.[0-9]+")

BASE_URL="https://github.com/arduino/arduino-cli/archive/refs/tags/"
line=$(grep "$BASE_URL" "$MANIFEST")
arduino_cli_ver=$(echo "$line" | grep -oP "(?<=${BASE_URL}v)[0-9]+\.[0-9]+\.[0-9]+")

# Download sources

cd $DIR

wget -O task.tar.gz https://github.com/go-task/task/archive/refs/tags/v$task_ver.tar.gz
tar -xf task.tar.gz
rm -rf ./task && mv ./task-* ./task

wget -O arduino-cli.tar.gz https://github.com/arduino/arduino-cli/archive/refs/tags/v$arduino_cli_ver.tar.gz
tar -xf arduino-cli.tar.gz
rm -rf ./arduino-cli && mv ./arduino-cli-* ./arduino-cli

# Create flatpak sources

cd ./task; go run github.com/dennwc/flatpak-go-mod@latest; cd ..
cd ./arduino-cli; go run github.com/dennwc/flatpak-go-mod@latest; cd ..
unset GOPATH

cd ..

cp $DIR/task/modules.txt ./task_modules.txt
cp $DIR/arduino-cli/modules.txt ./arduino-cli_modules.txt

python3 update_sources.py
