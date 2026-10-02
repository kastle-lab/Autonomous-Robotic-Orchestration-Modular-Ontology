# Scenario 1 source data

These CSVs support synthetic, symbolic testing of
[example scenario 1](../../example-scenario/example-scenario-1.md). 

## Current materialization and checks

Run from the repository root:

```sh
python3 -m pip install -r scripts/materialization/requirements.txt
python3 scripts/materialization/prepare_data.py
python3 -m morph_kgc scripts/materialization/mappings/configuration.ini
python3 scripts/materialization/validate_materialized.py
```
