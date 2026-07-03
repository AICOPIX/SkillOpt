from __future__ import annotations

import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from skillopt.model import chat_target


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _compact_text(text: str) -> str:
    return re.sub(r"\s+", "", str(text or "").strip().lower())


CONCEPT_ALIASES: dict[str, tuple[str, ...]] = {
    "自然光": ("自然光", "自然阳光", "自然采光", "日光", "阳光", "柔和自然光", "白天柔和自然光"),
    "主体清晰": ("主体清晰", "主体清晰锐利", "主体居中", "主体明确", "轮廓清晰", "清晰主体"),
    "真实摄影风格": ("真实摄影风格", "真实摄影", "写实摄影", "摄影质感", "真实产品摄影", "商业产品摄影"),
    "背景简洁": ("背景简洁", "简洁背景", "背景干净", "背景是简洁", "画面干净", "环境简洁", "干净背景", "干净无杂物"),
    "空间布局": ("空间布局", "开放式空间", "功能分区", "布局", "空间通透"),
    "木质材质": ("木质材质", "木质", "木材", "实木", "原木", "木纹", "木质地板", "木质家具"),
    "真实室内摄影风格": ("真实室内摄影风格", "真实室内摄影", "室内摄影", "真实室内摄影效果", "家居摄影", "室内设计摄影"),
    "主标题清晰可读": ("主标题清晰可读", "标题清晰可读", "清晰可读", "完整可读", "字号足够大"),
    "科技感背景": ("科技感背景", "科技背景", "科技图形", "科技氛围", "数据流", "网格", "神经网络"),
    "海报版式": ("海报版式", "海报设计", "版式", "标题区", "主视觉", "发布会海报"),
    "黑金视觉": ("黑金视觉", "黑金配色", "黑色与金色", "深黑", "金色", "黑金"),
    "产品主体清晰": ("产品主体清晰", "主体清晰", "主体清晰锐利", "产品主视觉", "杯子位于画面中心", "主体明确"),
    "陶瓷质感": ("陶瓷质感", "陶瓷材质", "釉面", "陶瓷釉面", "光滑温润"),
    "柔和光线": ("柔和光线", "柔和光", "柔和的自然漫射光", "柔和侧光", "柔和阴影", "漫射光"),
    "干净背景": ("干净背景", "背景干净", "背景纯白", "极简干净", "画面干净", "干净无杂物"),
    "顶部余额区域": ("顶部余额区域", "顶部为余额", "余额概览区域", "顶部显示余额", "余额卡片"),
    "消费分类卡片": ("消费分类卡片", "消费分类", "分类卡片", "分类卡片网格", "圆角白色卡片"),
    "底部导航": ("底部导航", "底部标签栏", "底部 tab", "标签栏导航", "tab bar"),
    "清晰 UI 层级": ("清晰ui层级", "ui层级清晰", "字体层级清晰", "层级清晰", "视觉层级清晰"),
    "Hero 区域": ("hero区域", "hero区", "hero主视觉", "首屏中央", "首屏", "主视觉区"),
    "导航栏": ("导航栏", "顶部导航", "固定导航"),
    "CTA 按钮": ("cta按钮", "cta", "行动按钮", "免费试用", "立即开始"),
    "产品展示区": ("产品展示区", "作品展示", "展示卡片", "模型画廊", "产品展示"),
    "玻璃拟态卡片": ("玻璃拟态卡片", "毛玻璃卡片", "玻璃面板", "半透明玻璃", "glassmorphism"),
    "雨水": ("雨水", "雨滴", "雨幕", "雨天", "湿润街道"),
    "公交站环境": ("公交站环境", "公交站", "站牌", "透明雨棚", "长椅"),
    "电影级光影": ("电影级光影", "电影感光影", "电影级调色", "电影感构图", "胶片质感"),
    "情绪氛围": ("情绪氛围", "氛围", "孤独", "期待", "安静", "叙事感"),
    "标题区": ("标题区", "顶部标题", "主标题", "标题"),
    "3 个模块": ("3个模块", "三个模块", "三张卡片", "3个步骤模块", "三个并列"),
    "步骤编号": ("步骤编号", "编号01", "01", "02", "03", "步骤顺序"),
    "简短中文标签": ("简短中文标签", "短中文标签", "中文说明", "中文文字", "模块标题"),
    "清晰层级": ("清晰层级", "层级清楚", "信息层级", "层级分明", "版式清晰"),
    "可爱比例": ("可爱比例", "头大身小", "q版", "萌系", "身体小巧"),
    "圆润造型": ("圆润造型", "圆润", "柔和轮廓", "无尖锐边角", "圆形"),
    "角色主体清晰": ("角色主体清晰", "角色主体居中", "轮廓清晰", "主体居中", "角色清晰"),
    "简单背景": ("简单背景", "背景简单", "干净背景", "浅灰", "浅蓝", "柔和渐变", "无任何杂物"),
    "建筑透视": ("建筑透视", "透视视角", "透视准确", "仰角", "低角度", "几何体块关系"),
    "外立面材质": ("外立面材质", "立面", "混凝土", "玻璃幕墙", "材质细节", "清水混凝土"),
    "黄昏光线": ("黄昏光线", "黄昏", "夕阳光", "暖色", "低角度", "长投影"),
    "建筑可视化风格": ("建筑可视化风格", "建筑效果图", "建筑可视化", "效果图", "建筑摄影"),
    "环境简洁": ("环境简洁", "开阔场地", "画面干净", "简洁开阔", "浅色铺装", "无杂物"),
}


def _contains(text: str, phrase: str) -> bool:
    normalized = _normalize_text(text)
    needle = _normalize_text(phrase)
    return bool(needle) and needle in normalized


def _matches_concept(text: str, phrase: str) -> bool:
    normalized = _normalize_text(text)
    compact = _compact_text(text)
    candidates = CONCEPT_ALIASES.get(str(phrase), (str(phrase),))
    for candidate in candidates:
        if _normalize_text(candidate) in normalized or _compact_text(candidate) in compact:
            return True
    return False


def _extract_final_prompt(response: str) -> str:
    text = str(response or "").strip()
    lower = text.lower()
    end_tag = "</think>"
    if end_tag in lower:
        index = lower.rfind(end_tag)
        text = text[index + len(end_tag):].strip()
    if "```" in text:
        parts = text.split("```")
        fenced_blocks = [part.strip() for index, part in enumerate(parts) if index % 2 == 1 and part.strip()]
        if fenced_blocks:
            text = fenced_blocks[-1]
            if "\n" in text:
                first_line, rest = text.split("\n", 1)
                if first_line.strip().lower() in {"text", "prompt", "markdown", "md"}:
                    text = rest
    text = text.strip()
    prefixes = ("最终prompt：", "最终 prompt：", "最终Prompt：", "Final prompt:", "Final Prompt:")
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    return text


def _load_packaged_references() -> str:
    references_dir = Path(__file__).resolve().parent / "skills" / "references"
    if not references_dir.exists():
        return ""
    chunks: list[str] = []
    for path in sorted(references_dir.glob("*.md")):
        chunks.append(f"\n\n## Reference: {path.name}\n\n{path.read_text(encoding='utf-8').strip()}")
    return "".join(chunks)


def _build_system_prompt(skill_content: str) -> str:
    base = skill_content.strip() or "You optimize text-to-image prompts."
    references = _load_packaged_references()
    if not references:
        return base
    return f"{base}\n\n---\n\n# Bundled Skill References\n{references}"


def _violates_exclusion(text: str, phrase: str) -> bool:
    compact = _compact_text(text)
    needle = _compact_text(phrase)
    if not needle or needle not in compact:
        return False
    negation_cues = (
        "无",
        "无任何",
        "没有",
        "不要",
        "不出现",
        "禁止",
        "避免",
        "排除",
        "不能有",
        "不得出现",
        "不包含",
        "no",
        "without",
        "exclude",
        "excluding",
    )
    separators = "。；;.!?\n"
    start = 0
    while True:
        index = compact.find(needle, start)
        if index < 0:
            return False
        left = max(compact.rfind(separator, 0, index) for separator in separators) + 1
        right_candidates = [compact.find(separator, index) for separator in separators]
        right = min([pos for pos in right_candidates if pos >= 0], default=len(compact))
        clause = compact[left:right]
        prefix = clause[: max(0, clause.find(needle))]
        local_prefix = compact[max(0, index - 12):index]
        if any(cue in prefix or cue in local_prefix for cue in negation_cues):
            start = index + len(needle)
            continue
        return True


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
    include_hits = sum(1 for term in include_terms if _matches_concept(prediction, term))
    exclude_hits = sum(1 for term in exclude_terms if _violates_exclusion(prediction, term))
    include_score = include_hits / max(len(include_terms), 1)
    exclude_score = 1.0 - (exclude_hits / max(len(exclude_terms), 1))
    soft = max(0.0, min(1.0, (include_score * 0.7) + (exclude_score * 0.3)))
    hard = int(include_hits == len(include_terms) and exclude_hits == 0)
    fail_reason = ""
    if include_hits != len(include_terms):
        missing = [term for term in include_terms if not _matches_concept(prediction, term)]
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
    system_prompt = _build_system_prompt(skill_content)
    if mock:
        prediction = _mock_prediction(item, skill_content)
    else:
        response, _usage = chat_target(
            system=system_prompt,
            user=user_prompt,
            max_completion_tokens=max_completion_tokens,
        )
        prediction = _extract_final_prompt(response)
    hard, soft, fail_reason = _score(prediction, item)
    (pred_dir / "target_system_prompt.txt").write_text(system_prompt, encoding="utf-8")
    (pred_dir / "target_user_prompt.txt").write_text(user_prompt, encoding="utf-8")
    (pred_dir / "prediction.txt").write_text(prediction, encoding="utf-8")
    if not mock:
        (pred_dir / "raw_response.txt").write_text(response, encoding="utf-8")
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": prediction},
        {
            "role": "system",
            "content": (
                f"Evaluation: hard={hard}, soft={soft:.4f}. "
                f"Failure reason: {fail_reason or 'passed'}"
            ),
        },
    ]
    (pred_dir / "conversation.json").write_text(
        json.dumps(conversation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
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
