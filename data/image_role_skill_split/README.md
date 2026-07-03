# image_role_skill Data

This folder currently contains the first lightweight calibration set.

- `train/items.json`: 10 lightweight optimization cases, used as `train v0.1`.
- `val/items.json`: currently empty; add separate validation cases before real gated training.
- `test/items.json`: currently empty; add separate held-out cases before final assessment.

See `success-rubric.md` for the current pass/fail standard.

Item shape:

```json
{
  "id": "case_001",
  "input_prompt": "用户原始文生图需求",
  "fixed_facts": ["必须保留的事实"],
  "must_include": ["最终 prompt 必须包含的要点"],
  "must_exclude": ["不能作为正向内容出现的内容"],
  "visual_type": "poster | product | character | icon | environment | ui_mockup | other",
  "task_type": "fixed_fact_preservation"
}
```

Do not treat results as real improvement evidence until all three splits are non-empty.
