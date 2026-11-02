from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
COUNT = 50
CJK_PATTERN = re.compile(r"[\u3400-\u9fff]")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def validate_records(records: list[dict[str, Any]]) -> None:
    if len(records) != COUNT:
        raise ValueError(f"Expected {COUNT} records, found {len(records)}")

    expected_ids = [f"AL-WORKING-SAMPLE-{i:03d}" for i in range(1, COUNT + 1)]
    if [item.get("record_id") for item in records] != expected_ids:
        raise ValueError("Invalid record IDs or order")

    source_rows: set[int] = set()
    titles: set[str] = set()
    hashes: set[str] = set()
    required_fields = set(records[0])

    for record in records:
        record_id = record["record_id"]
        if set(record) != required_fields:
            raise ValueError(f"{record_id}: inconsistent fields")
        for key in ("title_en", "abstract_en", "model_input_en"):
            value = record.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{record_id}: empty {key}")
            if CJK_PATTERN.search(value):
                raise ValueError(f"{record_id}: unexpected CJK text in {key}")

        if record["model_input_en"] != record["abstract_en"]:
            raise ValueError(f"{record_id}: model input differs from abstract")
        if len(record["abstract_en"].split()) < 30:
            raise ValueError(f"{record_id}: abstract is unusually short")

        source_row = record.get("source_excel_row")
        title = " ".join(record["title_en"].casefold().split())
        source_hash = record.get("source_record_sha256")
        if not isinstance(source_row, int) or source_row < 2:
            raise ValueError(f"{record_id}: invalid source row")
        if not isinstance(source_hash, str) or not SHA256_PATTERN.fullmatch(source_hash):
            raise ValueError(f"{record_id}: invalid source fingerprint")
        if source_row in source_rows or title in titles or source_hash in hashes:
            raise ValueError(f"{record_id}: duplicate source or title")
        source_rows.add(source_row)
        titles.add(title)
        hashes.add(source_hash)


def validate_csv(records: list[dict[str, Any]]) -> None:
    with (DATA / "aqualit_50_en.csv").open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("Invalid CSV header")
        csv_rows = list(reader)

    if len(csv_rows) != len(records):
        raise ValueError("CSV and JSONL row counts differ")

    for record, csv_record in zip(records, csv_rows):
        if set(record) != set(csv_record):
            raise ValueError(f"{record['record_id']}: CSV schema differs")
        for key, value in record.items():
            expected = "" if value is None else str(value)
            if csv_record[key] != expected:
                raise ValueError(f"{record['record_id']}: CSV mismatch in {key}")


def validate_inputs(records: list[dict[str, Any]]) -> None:
    model_inputs = read_jsonl(DATA / "model_inputs_en.jsonl")
    if len(model_inputs) != len(records):
        raise ValueError("Model-input count differs")

    for record, sample in zip(records, model_inputs):
        if (sample.get("record_id") != record["record_id"]
                or sample.get("text") != record["model_input_en"]
                or sample.get("language") != "en"
                or sample.get("label_ids") != record.get("level3_label_ids")
                or sample.get("split") != record.get("split")):
            raise ValueError(f"{record['record_id']}: model-input mismatch")


def validate() -> dict[str, Any]:
    records = read_jsonl(DATA / "aqualit_50_en.jsonl")
    validate_records(records)
    validate_csv(records)
    validate_inputs(records)
    return {
        "records": len(records),
        "unique_titles": len({record["title_en"].casefold() for record in records}),
        "unique_source_rows": len({record["source_excel_row"] for record in records}),
        "csv_jsonl_consistent": True,
        "model_inputs_consistent": True,
    }


def main() -> None:
    print(json.dumps(validate(), indent=2))


if __name__ == "__main__":
    main()
