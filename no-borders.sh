#!/bin/bash
# No-Borders KVM Switch - Quick Launcher
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
echo "🚀 Launching No-Borders KVM Switch..."
python3 -m kvm_switch "$@"
