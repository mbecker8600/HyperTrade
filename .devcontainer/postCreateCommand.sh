#script.sh

#!/bin/sh

# Install third-party dependencies for Python
pip3 install -r third-party/requirements.txt

# Install typeshed for Pyre
git clone https://github.com/python/typeshed.git