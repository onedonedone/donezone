#!/usr/bin/bash
if [[ -n "${ZONE-}" && -f "$ZONE/.tmux.conf" ]]; then
    exec /usr/bin/tmux -f "$ZONE/.tmux.conf" "$@"
fi

exec /usr/bin/tmux "$@"
