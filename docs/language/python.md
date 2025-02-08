# Python

## Adding a new package (Python)

To add a new package to the monorepo, you can run the following command from the root of the monorepo:

```bash
pip install <package-name>
pip freeze > third-party/requirements.txt
```

## Running notebooks

- Create a BUILD.bazel file with the following content:

```bash
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
```

- Run the following command to start the Jupyter Notebook server:
  bazel run //path/to/target:server

- Open notebook with kernel set to running server.
  Note, you need the token from the console output to login.
