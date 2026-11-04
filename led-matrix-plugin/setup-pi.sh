#!/usr/bin/env bash
# One-time toolchain on the Pi for building led-matrix plugins (run on the Pi; takes a while):
# the led-matrix sources at the installed version, plus its vcpkg dependencies at the same
# baseline, built static with -fPIC so they link into the plugin .so.
# After a led-matrix upgrade: rm -rf ~/ledm-build/led-matrix and run this again.
set -euo pipefail
ROOT="${LEDM_BUILD:-$HOME/ledm-build}"
mkdir -p "$ROOT" && cd "$ROOT"

sudo apt-get update -q >/dev/null
sudo apt-get install -y -q cmake ninja-build git curl zip unzip tar pkg-config build-essential \
  autoconf autoconf-archive automake libtool bison flex python3-jinja2 \
  libgraphicsmagick++1-dev >/dev/null

version=$(dpkg-query -W -f '${Version}' led-matrix)
[ -d led-matrix ] || git clone -q --depth 1 --branch "v$version" https://github.com/sshcrack/led-matrix.git
baseline=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["default-registry"]["baseline"])' \
  led-matrix/vcpkg-configuration.json)

[ -d vcpkg ] || git clone -q https://github.com/microsoft/vcpkg.git
git -C vcpkg fetch -q origin "$baseline" 2>/dev/null || true
git -C vcpkg checkout -q "$baseline"
export VCPKG_FORCE_SYSTEM_BINARIES=1  # no prebuilt cmake/ninja for arm64
[ -x vcpkg/vcpkg ] || ./vcpkg/bootstrap-vcpkg.sh -disableMetrics

mkdir -p deps/triplets
cat > deps/triplets/arm64-rpi-native.cmake <<'EOF'
set(VCPKG_TARGET_ARCHITECTURE arm64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_LIBRARY_LINKAGE static)
set(VCPKG_CMAKE_SYSTEM_NAME Linux)
set(VCPKG_BUILD_TYPE release)
set(VCPKG_CXX_FLAGS "-fPIC")
set(VCPKG_C_FLAGS "-fPIC")
EOF
# What the plugin API headers include (see led-matrix plugins/CMakeLists.txt). GraphicsMagick
# comes from apt instead: the API only names Magick::Image in function signatures the plugin
# never calls, so any 1.3.x headers do, and their vcpkg overlay port fails to build natively.
cat > deps/vcpkg.json <<'EOF'
{ "dependencies": ["fmt", "nlohmann-json", "spdlog", "restinio", "magic-enum", "libxml2", "rpi-rgb-led-matrix"] }
EOF
cat > deps/vcpkg-configuration.json <<EOF
{ "default-registry": { "kind": "git", "baseline": "$baseline", "repository": "https://github.com/microsoft/vcpkg" },
  "overlay-ports": ["$ROOT/led-matrix/cmake/overlay-ports"] }
EOF
cd deps
../vcpkg/vcpkg install --triplet arm64-rpi-native --overlay-triplets=triplets --x-install-root=installed
echo SETUP_DONE
