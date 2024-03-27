#!/usr/bin/env python3

import os
import shutil
import tarfile
import requests
from ruamel import yaml

def clear_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

def download_file(url, save_path):
    response = requests.get(url)
    print(f"Downloading {url}")

    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print("File downloaded successfully.")
    else:
        print("Failed to download file.")

def extract_tar_gz(file_path, extract_path):
    try:
        with tarfile.open(file_path, "r:gz") as tar:
            tar.extractall(extract_path)
        print(f"Successfully extracted '{file_path}' to '{extract_path}'.")
    except tarfile.TarError as e:
        print(f"Error extracting '{file_path}': {e}")

def get_latest_github_tag(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/tags"
    response = requests.get(url)

    if response.status_code == 200:
        tags_info = response.json()
        stable_tags = [tag['name'] for tag in tags_info if not "rc" in tag['name']] # exclude pre-releases
        if stable_tags:
            latest_stable_tag = max(stable_tags)
            return latest_stable_tag
        else:
            return None
    else:
        return None

MANIFEST_PATH = "com.simulide.simulide.yml"
GO_TASK_PATH = "generate_sources/task/go.mod.yml"
ARDUINO_CLI_PATH = "generate_sources/arduino-cli/go.mod.yml"

GO_TASK_URL = "https://github.com/go-task/task"
ARDUINO_CLI_URL = "https://github.com/arduino/arduino-cli"

GO_TASK_TAG = get_latest_github_tag("go-task", "task")
ARDUINO_CLI_TAG = get_latest_github_tag("arduino", "arduino-cli")

DIR = f"{os.getcwd()}/generate_sources"

yaml = yaml.YAML(typ="rt")
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 200                                # Prevent line wrapping
yaml.preserve_quotes = True                     # Preserve spaces before each entry

# Create new sources

# clear_directory(f"{DIR}/go")
clear_directory(f"{DIR}/arduino-cli")
clear_directory(f"{DIR}/task")

download_file(f"https://github.com/go-task/task/archive/refs/tags/{GO_TASK_TAG}.tar.gz", f"{DIR}/task.tar.gz")
download_file(f"https://github.com/arduino/arduino-cli/archive/refs/tags/{ARDUINO_CLI_TAG}.tar.gz", f"{DIR}/arduino-cli.tar.gz")

extract_tar_gz(f"{DIR}/task.tar.gz", f"{DIR}")
extract_tar_gz(f"{DIR}/arduino-cli.tar.gz", f"{DIR}")

os.rename(f"{DIR}/task-{GO_TASK_TAG[1:]}", f"{DIR}/task")
os.rename(f"{DIR}/arduino-cli-{ARDUINO_CLI_TAG[1:]}", f"{DIR}/arduino-cli")

os.system(f"cd {DIR}/task ; GOPATH={DIR}/go go run github.com/dennwc/flatpak-go-mod@latest")
os.system(f"cd {DIR}/arduino-cli; GOPATH={DIR}/go go run github.com/dennwc/flatpak-go-mod@latest")

# Load manifest and generated sources

with open(MANIFEST_PATH, "r", encoding="UTF-8") as manifest_file:
    manifest_content = yaml.load(manifest_file)

with open(GO_TASK_PATH, "r", encoding="UTF-8") as go_task_file:
    go_task_content = yaml.load(go_task_file)

with open(ARDUINO_CLI_PATH, "r", encoding="UTF-8") as arduino_cli_file:
    arduino_cli_content = yaml.load(arduino_cli_file)

# Create new sources

new_sources = []

for entry in manifest_content["modules"][0]["sources"]:
    if GO_TASK_URL in entry.get("url", ""):
        entry["tag"] = GO_TASK_TAG
        new_sources.append(entry)

    if ARDUINO_CLI_URL in entry.get("url", ""):
        entry["tag"] = ARDUINO_CLI_TAG
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
