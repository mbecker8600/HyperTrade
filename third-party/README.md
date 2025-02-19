# third-party

This holds all of the third party dependency management for the monorepo.

## Python

DO NOT MODIFY THE `requirements_lock.txt` FILE!.

Use the following bazel command to regenerate it.

```bash
bazel run //third-party:requirements.update
```
