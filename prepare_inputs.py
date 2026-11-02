from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "aqualit_50_en.jsonl"
DEFAULT_OUTPUT = ROOT / "data" / "model_inputs_en.jsonl"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def prepare_inputs(source: Path, output: Path) -> int:
    records = read_jsonl(source)
    prepared = []

    for record in records:
        record_id = record.get("record_id")
        abstract = record.get("model_input_en")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError("Record ID is missing")
        if not isinstance(abstract, str) or not abstract.strip():
            raise ValueError(f"Missing English input for {record_id}")

        prepared.append({
            "record_id": record_id,
            "text": abstract,
            "language": "en",
            "translation_review_status": record.get("translation_review_status"),
            "label_ids": record.get("level3_label_ids"),
            "split": record.get("split"),
            "paper_equivalent_preprocessing": False,
        })

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        for record in prepared:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    return len(prepared)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    count = prepare_inputs(SOURCE, args.output)
    print(f"Prepared {count} records: {args.output}")


if __name__ == "__main__":
    main()
