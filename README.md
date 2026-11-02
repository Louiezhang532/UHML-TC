# Aqua-Lit: English Sample Dataset

A 50-record English-language aquaculture literature sample with tools for data validation, model-input preparation, and hierarchical classification evaluation.

## Contents

```text
data/aqualit_1.jsonl      Structured records in JSON Lines format
data/model_inputs_en.jsonl    Model-ready text interface
code/validate.py             Dataset integrity checks
code/prepare_inputs.py       Model-input generation
code/hierarchical_metrics.py Micro-F1 and hierarchical F1 functions
```

## Requirements

Python 3.10 or newer. No third-party dependencies are required for the included utility scripts.

## Usage

```bash
python code/validate.py
python code/prepare_inputs.py
python code/validate.py
```


