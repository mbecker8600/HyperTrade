#!/bin/sh

# Install third-party dependencies for Python
pip3 install -r third-party/requirements.txt
npm install
curl https://get.trunk.io -fsSL | bash -s -- -y
