import csv
import json
from pathlib import Path
from typing import Generator, Any

def parse_csv(file_path: str, pagination: dict | None = None) -> Generator[dict, None, None]:
    """Parses a CSV file. If pagination has skip/limit, it slices the rows."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    skip = pagination.get("skip", 0) if pagination else 0
    limit = pagination.get("limit", -1) if pagination else -1

    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for i, row in enumerate(reader):
            if i < skip:
                continue
            if limit != -1 and count >= limit:
                break
            yield dict(row)
            count += 1

def parse_json(file_path: str, pagination: dict | None = None) -> Generator[dict, None, None]:
    """Parses a JSON array. If pagination has skip/limit, it slices the array."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON not found: {path}")

    with open(path, mode="r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON must be an array of objects")

    skip = pagination.get("skip", 0) if pagination else 0
    limit = pagination.get("limit", -1) if pagination else -1

    for item in data[skip:]:
        if limit != -1 and limit <= 0:
            break
        if isinstance(item, dict):
            yield item
            if limit != -1:
                limit -= 1