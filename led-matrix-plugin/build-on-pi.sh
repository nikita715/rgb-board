#!/usr/bin/env bash
# Builds the ExternalFrame plugin on the Pi against the installed led-matrix and
# installs it to /usr/lib/led-matrix/plugins/ExternalFrame.
#
# Needs ~/ledm-build from setup-pi.sh: the led-matrix sources at the installed
# version and vcpkg dependencies at the same baseline, so the plugin matches the
# ABI of /usr/bin/led-matrix (also built with GCC 12.2).
set -euo pipefail

ROOT="${LEDM_BUILD:-$HOME/ledm-build}"
SRC="$(cd "$(dirname "$0")/ExternalFrame" && pwd)"
DEPS="$ROOT/deps/installed/arm64-rpi-native"
LM="$ROOT/led-matrix"
OUT="$ROOT/out/ExternalFrame"
LIBDIR=/usr/lib/led-matrix

installed=$(dpkg-query -W -f '${Version}' led-matrix)
built=$(git -C "$LM" describe --tags)
if [ "v$installed" != "$built" ]; then
  echo "led-matrix $installed is installed, but the sources in $LM are $built. Run setup-pi.sh again." >&2
  exit 1
fi

mkdir -p "$OUT"
g++ -std=c++23 -O2 -fPIC -shared -o "$OUT/libExternalFrame.so" \
  -DPLUGIN_NAME='"ExternalFrame"' -DSPDLOG_COMPILED_LIB -DSPDLOG_FMT_EXTERNAL \
  -I"$SRC" -I"$LM/shared/matrix/include" -I"$LM/shared/common/include" \
  -I"$DEPS/include" -I/usr/include/GraphicsMagick \
  "$SRC/matrix/ExternalFrame.cpp" "$SRC/scenes/ExternalFrameScene.cpp" \
  -L"$LIBDIR" -lSharedToolsMatrix -lSharedToolsCommon -lrpi-rgb-led-matrix \
  -L"$DEPS/lib" -lspdlog -lfmt \
  -Wl,-z,defs -Wl,-rpath,'$ORIGIN/../..'

sudo install -d "$LIBDIR/plugins/ExternalFrame"
sudo install -m 644 "$OUT/libExternalFrame.so" "$LIBDIR/plugins/ExternalFrame/"
sudo systemctl restart led-matrix
echo "Installed $LIBDIR/plugins/ExternalFrame/libExternalFrame.so and restarted led-matrix"
