#!/usr/bin/bash
if [ -n "${ZONE-}" ] && [ -f "$ZONE/.gitconfig" ]; then
    export GIT_CONFIG_GLOBAL="$ZONE/.gitconfig"
fi

exec /usr/bin/git "$@"
