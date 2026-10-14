#!/bin/sh
set -eu
exec sh "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/setup.sh" --game-package "$@"
