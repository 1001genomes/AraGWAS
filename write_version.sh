#!/bin/sh


VERSION_FILE=${1:-aragwas_server/gwasdb/__init__.py}

cat <<EOF > $VERSION_FILE
# DON'T MODIFY THIS FILE. Version and git commit will be written by build pipeline
import datetime
#TODO fix version
__version__="${GIT_BRANCH:-undef}"
__build__="${BUILD_NUMBER:-undef}"
__githash__="${GIT_COMMIT:-undef}"
__buildurl__="${BUILD_URL:-undef}"
# if it was linux only, we could do 'date -Iseconds' instead of date -u +"%Y-%m-%dT%H:%M:%SZ"
__date__="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
EOF

