# HyperTrade

## Getting started

## Language specific

### Python

#### Debugging Python targets

Example:

```bash
bazel test \
--run_under="debugpy --listen 0.0.0.0:5678 --wait-for-client" \
//hypertrade/libs/finance/tests:accounting_tests
```
