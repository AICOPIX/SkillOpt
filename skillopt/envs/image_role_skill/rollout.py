from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from skillopt.model import chat_target


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _contains(text: str, phrase: str) -> bool:
    normalized = _normalize_text(text)
    needle = _normalize_text(phrase)
    return bool(needle) and needle in normalized


def _violates_exclusion(text: str, phrase: str) -> bool:
    normalized = _normalize_text(text)
    needle = _normalize_text(phrase)
    if not needle or needle not in normalized:
        return False
    allowed_negations = (
        f"no {needle}",
        f"without {needle}",
        f"exclude {needle}",
        f"excluding {needle}",
    )
    return not any(negation in normalized for negation in allowed_negations)


def _build_user(item: dict) -> str:
    return "\n\n".join(
        [
            "Optimize this text-to-image prompt.",
            f"Input prompt: {item['input_prompt']}",
            "Fixed facts:\n" + "\n".join(f"- {fact}" for fact in item.get("fixed_facts", [])),
            f"Visual type: {item.get('visual_type', 'unknown')}",
            "Must include:\n" + "\n".join(f"- {value}" for value in item.get("must_include", [])),
            "Must exclude:\n" + "\n".join(f"- {value}" for value in item.get("must_exclude", [])),
            "Return only the final optimized prompt.",
        ]
    )


def _mock_prediction(item: dict, skill_content: str) -> str:
    include_bits = ", ".join(item.get("must_include", []))
    exclude_bits = ", ".join(f"no {value}" for value in item.get("must_exclude", []))
    quality_bits = "clear composition, specific lighting, production-ready visual details"
    if skill_content.strip():
        quality_bits += ", fixed facts preserved"
    return f"{item['input_prompt']}, {include_bits}, {quality_bits}, {exclude_bits}".strip(", ")


def _score(prediction: str, item: dict) -> tuple[int, float, str]:
    include_terms = item.get("must_include", [])
    exclude_terms = item.get("must_exclude", [])
    include_hits = sum(1 for term in include_terms if _contains(prediction, term))
    exclude_hits = sum(1 for term in exclude_terms if _violates_exclusion(prediction, term))
    include_score = include_hits / max(len(include_terms), 1)
    exclude_score = 1.0 - (exclude_hits / max(len(exclude_terms), 1))
    soft = max(0.0, min(1.0, (include_score * 0.7) + (exclude_score * 0.3)))
    hard = int(include_hits == len(include_terms) and exclude_hits == 0)
    fail_reason = ""
    if include_hits != len(include_terms):
        missing = [term for term in include_terms if not _contains(prediction, term)]
        fail_reason = "missing required terms: " + ", ".join(missing)
    if exclude_hits:
        banned = [term for term in exclude_terms if _violates_exclusion(prediction, term)]
        fail_reason = (fail_reason + "; " if fail_reason else "") + "included banned terms: " + ", ".join(banned)
    return hard, soft, fail_reason


def process_one(
    item: dict,
    out_root: str,
    skill_content: str,
    *,
    mock: bool = False,
    max_completion_tokens: int = 2048,
) -> dict:
    item_id = str(item["id"])
    pred_dir = Path(out_root) / "predictions" / item_id
    pred_dir.mkdir(parents=True, exist_ok=True)
    user_prompt = _build_user(item)
    system_prompt = skill_content.strip() or "You optimize text-to-image prompts."
    if mock:
        prediction = _mock_prediction(item, skill_content)
    else:
        prediction, _usage = chat_target(
            system=system_prompt,
            user=user_prompt,
            max_completion_tokens=max_completion_tokens,
        )
    hard, soft, fail_reason = _score(prediction, item)
    (pred_dir / "target_system_prompt.txt").write_text(system_prompt, encoding="utf-8")
    (pred_dir / "target_user_prompt.txt").write_text(user_prompt, encoding="utf-8")
    (pred_dir / "prediction.txt").write_text(prediction, encoding="utf-8")
    return {
        "id": item_id,
        "task_type": item.get("task_type", "image_role_prompt"),
        "task_description": item.get("input_prompt", ""),
        "input_prompt": item.get("input_prompt", ""),
        "visual_type": item.get("visual_type", "unknown"),
        "fixed_facts": item.get("fixed_facts", []),
        "must_include": item.get("must_include", []),
        "must_exclude": item.get("must_exclude", []),
        "predicted_answer": prediction,
        "response": prediction,
        "hard": hard,
        "soft": soft,
        "fail_reason": fail_reason,
    }


def run_batch(
    *,
    items: list[dict],
    skill_content: str,
    out_root: str,
    workers: int = 4,
    mock: bool = False,
    max_completion_tokens: int = 2048,
) -> list[dict]:
    os.makedirs(out_root, exist_ok=True)
    results_path = Path(out_root) / "results.jsonl"
    results: list[dict] = []
    with results_path.open("w", encoding="utf-8") as handle:
        with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
            futures = [
                pool.submit(
                    process_one,
                    item,
                    out_root,
                    skill_content,
                    mock=mock,
                    max_completion_tokens=max_completion_tokens,
                )
                for item in items
            ]
            for index, future in enumerate(as_completed(futures), start=1):
                result = future.result()
                results.append(result)
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
                handle.flush()
                print(
                    f"    [image_role] {index}/{len(items)} id={result['id']} hard={result['hard']} soft={result['soft']:.3f}",
                    flush=True,
                )
    return results
