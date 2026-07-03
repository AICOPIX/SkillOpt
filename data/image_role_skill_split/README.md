# image_role_skill Data

This folder is intentionally initialized with empty `items.json` arrays.

Fill these files before real evaluation or training:

- `train/items.json`: examples SkillOpt uses to propose skill edits.
- `val/items.json`: validation gate; decides whether an updated skill is accepted.
- `test/items.json`: final held-out assessment.

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

Do not run real SkillOpt training until all three splits are non-empty and the success rubric is agreed.
