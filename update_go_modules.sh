manifest="com.simulide.simulide.yml"
DIR=$PWD/generate_sources

# Create folders and set go path

mkdir -p $DIR; rm -rf $DIR/*

cd $DIR

mkdir $DIR/go
export GOPATH=$DIR/go

# Extract versions from yaml

base_url="https://github.com/go-task/task/archive/refs/tags/"
line=$(grep "$base_url" "$manifest")
task_ver=$(echo "$line" | grep -oP "(?<=${base_url}v)[0-9]+\.[0-9]+\.[0-9]+")
task_ver="v$task_ver"

base_url="https://github.com/arduino/arduino-cli/archive/refs/tags/"
line=$(grep "$base_url" "$manifest")
arduino_cli_ver=$(echo "$line" | grep -oP "(?<=${base_url}v)[0-9]+\.[0-9]+\.[0-9]+")
arduino_cli_ver="v$arduino_cli_ver"

# Download sources

wget -O task.tar.gz https://github.com/go-task/task/archive/refs/tags/$task_ver.tar.gz
tar -xf task.tar.gz
rm -rf ./task && mv ./task-* ./task

wget -O arduino-cli.tar.gz https://github.com/arduino/arduino-cli/archive/refs/tags/$arduino_cli_ver.tar.gz
tar -xf arduino-cli.tar.gz
rm -rf ./arduino-cli && mv ./arduino-cli-* ./arduino-cli

# Create flatpak sources

cd ./task; go run github.com/dennwc/flatpak-go-mod@latest; cd ..
cd ./arduino-cli; go run github.com/dennwc/flatpak-go-mod@latest; cd ..
unset GOPATH

cd ..

cp $DIR/task/modules.txt ./task_modules.txt
cp $DIR/arduino-cli/modules.txt ./arduino-cli_modules.txt

cp $DIR/task/go.mod.yml $DIR/task.mod.yml
cp $DIR/arduino-cli/go.mod.yml $DIR/arduino-cli.mod.yml

sed -i 's/vendor/task\/vendor/g' $DIR/task.mod.yml
sed -i 's/vendor/arduino-cli\/vendor/g' $DIR/arduino-cli.mod.yml

sed -i 's/modules.txt/task_modules.txt/g' $DIR/task.mod.yml
sed -i 's/modules.txt/arduino-cli_modules.txt/g' $DIR/arduino-cli.mod.yml

# Apply indentation
sed -i -e 's/^/      /' $DIR/task.mod.yml
sed -i -e 's/^/      /' $DIR/arduino-cli.mod.yml
sed -i '/^\s*$/s/\s*//' $DIR/task.mod.yml
sed -i '/^\s*$/s/\s*//' $DIR/arduino-cli.mod.yml
sed -i ':a;/^[ \n]*$/{$d;N;ba}' $DIR/task.mod.yml
sed -i ':a;/^[ \n]*$/{$d;N;ba}' $DIR/arduino-cli.mod.yml

sed -i '1d' $DIR/task.mod.yml
sed -i '1d' $DIR/arduino-cli.mod.yml

# Clear old go modules
sed -i '/        dest: .\/arduino-cli/,/  - name: simulide/c\        dest: .\/arduino-cli\n\n  - name: simulide' $manifest
# Insert new ones
sed -i "/^        dest: .\/arduino-cli$/r $DIR/arduino-cli.mod.yml" $manifest
sed -i "/        dest: .\/arduino-cli/G" $manifest
sed -i "/^        dest: .\/arduino-cli$/r $DIR/task.mod.yml" $manifest
sed -i "/        dest: .\/arduino-cli/G" $manifest
