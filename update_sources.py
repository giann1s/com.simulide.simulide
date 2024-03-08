#!/usr/bin/env python3

from ruamel import yaml

MANIFEST_PATH = "com.simulide.simulide.yml"
GO_TASK_PATH = "generate_sources/task/go.mod.yml"
ARDUINO_CLI_PATH = "generate_sources/arduino-cli/go.mod.yml"

ARDUINO_CLI_URL = "https://github.com/arduino/arduino-cli/"
GO_TASK_URL = "https://github.com/go-task/task/"

yaml = yaml.YAML(typ="rt")
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 200                                # Prevent line wrapping
yaml.preserve_quotes = True                     # Preserve spaces before each entry

with open(MANIFEST_PATH, "r", encoding="UTF-8") as manifest_file:
    manifest_content = yaml.load(manifest_file)

with open(GO_TASK_PATH, "r", encoding="UTF-8") as go_task_file:
    go_task_content = yaml.load(go_task_file)

with open(ARDUINO_CLI_PATH, "r", encoding="UTF-8") as arduino_cli_file:
    arduino_cli_content = yaml.load(arduino_cli_file)

new_sources = []
for entry in manifest_content["modules"][0]["sources"]:
    if ARDUINO_CLI_URL in entry.get("url", "") or GO_TASK_URL in entry.get("url", ""):
        new_sources.append(entry)

for entry in go_task_content:
    new_sources.append(entry)

    if entry["type"] == "file" and entry["path"] == "modules.txt":
        entry["path"] = "task_" + entry["path"]
    entry["dest"] = "task/" + entry["dest"]

for entry in arduino_cli_content:
    new_sources.append(entry)

    if entry["type"] == "file" and entry["path"] == "modules.txt":
        entry["path"] = "arduino-cli_" + entry["path"]
    entry["dest"] = "arduino-cli/" + entry["dest"]

manifest_content["modules"][0]["sources"] = new_sources

# Write changes
with open(MANIFEST_PATH, "w", encoding="UTF-8") as manifest_file:
    yaml.dump(manifest_content, manifest_file)
