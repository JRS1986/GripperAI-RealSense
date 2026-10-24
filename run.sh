#!/usr/bin/env bash
# Starts the grasp detection UI (needs a connected RealSense D400 camera).
cd "$(dirname "$0")"
exec .venv/bin/python dexgripQtUi/main_uic.py "$@"
