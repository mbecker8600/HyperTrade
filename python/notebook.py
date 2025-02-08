"""notebook.py

This script is used to launch the Jupyter Notebook server
with all of the required bazel dependencies.

See Python docs for more information:
    //docs/python.md

Usage:
    1. Create a BUILD.bazel file with the following content:
        py_binary(
            name = "server",
            srcs = ["//python:notebook.py"],
            main = "notebook.py",
            deps = [
                "//path/to/your/dependencies:dep1",
                "//path/to/your/dependencies:dep2",
                "//path/to/your/dependencies:dep3",
                # Add more dependencies as needed
            ],
        )
    2. Run the following command to start the Jupyter Notebook server:
        bazel run //path/to/target:server
    3. Open notebook with kernel set to running server.
        Note, you need the token from the console output to login.

"""

import os
import sys

from nbclassic.notebookapp import main

if __name__ == "__main__":
    # Change the current working directory to the location of the notebook
    os.chdir(os.path.dirname(sys.argv[0]))
    main()
