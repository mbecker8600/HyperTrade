# Debugging

## Python

The only way I've been able to figure out how to get good integration with
VSCode is to import the `debugpy` module on the file you want to debug and then
attach a debugger to it (i.e. in the launch.json).

### Steps to debug

1. Import the one liner

```python
import hypertrade.libs.debugging
```

1. Add to bazel file

```bazel
...
deps = ["//hypertrade/libs:python_debugger"]
```

1. Run your code

```bash
bazel run //hypertrade/path/to:executable
```

1. Attach debugger in the `Run and Debug` section
