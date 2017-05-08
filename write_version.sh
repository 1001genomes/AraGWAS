#!/bin/sh


VERSION_FILE=aragwas_server/gwasdb/__init__.py

cat <<EOF > $VERSION_FILE
# DON'T MODIFY THIS FILE. Version and git commit will be written by build pipeline
import datetime
#TODO fix version
__version__="0.0.1a"
__build__="${BUILD_NUMBER:-N/A}"
__githash__="$(git describe --always)"
__buildurl__="${BUILD_URL:-N/A}"
# if it was linux only, we could do 'date -Iseconds' instead of date -u +"%Y-%m-%dT%H:%M:%SZ"
__date__="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
EOF

