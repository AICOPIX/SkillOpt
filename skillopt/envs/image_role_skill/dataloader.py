from __future__ import annotations

import json
from pathlib import Path

from skillopt.datasets.base import SplitDataLoader


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _normalize(raw: dict) -> dict:
    item_id = raw.get("id") or raw.get("uid")
    if not item_id:
        raise ValueError(f"Image-role item is missing id: {raw!r}")
    return {
        "id": str(item_id),
        "input_prompt": str(raw.get("input_prompt") or raw.get("prompt") or ""),
        "fixed_facts": _as_list(raw.get("fixed_facts")),
        "must_include": _as_list(raw.get("must_include")),
        "must_exclude": _as_list(raw.get("must_exclude")),
        "visual_type": str(raw.get("visual_type") or "unknown"),
        "task_type": str(raw.get("task_type") or "image_role_prompt"),
    }


class ImageRoleSkillDataLoader(SplitDataLoader):
    """Load image-role prompt optimization items from JSON split folders."""

    def load_split_items(self, split_path: str) -> list[dict]:
        path = Path(split_path)
        json_files = sorted(path.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(f"No .json file found in {split_path}")
        with json_files[0].open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            raise ValueError(f"Expected a JSON array in {json_files[0]}")
        return [_normalize(item) for item in payload]
