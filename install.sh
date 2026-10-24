#!/usr/bin/env bash
# Creates .venv with Python 3.13 and installs GripperAI-RealSense into it.
# Override the interpreter with e.g. PYTHON=~/.pyenv/versions/3.13.12/bin/python ./install.sh
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3.13}"
"$PYTHON" -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
# vendored, patched Dex-Net packages (dependencies are pinned in requirements.txt)
.venv/bin/pip install --no-deps -e perception_exactly_this_is_somehow_required -e gqcnn_jeffbranch_adapted
