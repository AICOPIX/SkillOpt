# 06 Output Format

默认输出：

## 类型判断
- 视觉类型：
- 判断理由：

## 固定内容
- 不可修改内容：
- 明确排除项：

## 结构化补全
- 构图 / 版式：
- 光照 / 色彩：
- 材质 / 细节：
- 背景 / 场景：
- 类型专属增强：

## 最终文生图 Prompt

```text
最终 prompt
```

## 边界说明
- 保留了：
- 增强了：
- 没有添加：

如果用户说“只要最终 prompt”，只输出纯文本 prompt。

如果用户说“给 JSON”，输出：

```json
{
  "raw_prompt": "",
  "visual_type": "",
  "locked_facts": [],
  "negative_constraints": [],
  "enrichment_slots": {
    "composition": "",
    "lighting": "",
    "materials": "",
    "background": "",
    "type_specific": ""
  },
  "optimized_prompt": ""
}
```
