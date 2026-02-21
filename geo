#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$DIR/.venv/bin/python3" "$@"
