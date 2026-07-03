---
name: arvune-text-to-image-prompt
description: "Optimize, rewrite, classify, and structure text-to-image prompts only. Use when the user asks to improve an image-generation prompt, expand a short visual idea, classify the visual type, extract fixed facts, apply type-specific prompt templates, or produce a copyable final text-to-image prompt. Do not use for image editing, inpainting, reference-image workflows, multi-image composition, API calls, code changes, or actual image generation."
---

# ARVUNE Text-to-Image Prompt Skill

Use this skill only for text-to-image prompt optimization.

The job is not to generate an image or call an image API. The job is to turn a short user idea or rough image prompt into a structured, controllable, visually expressive prompt that can be copied into a text-to-image model.

Core workflow:

```text
user idea
-> extract fixed facts
-> classify visual type
-> apply the matching type pattern
-> enrich visual expression
-> output final text-to-image prompt
```

## Boundaries

Do:

- Optimize text-to-image prompts.
- Structure rough or one-sentence visual ideas.
- Extract fixed facts that must not be changed.
- Classify the visual type.
- Add composition, lighting, materials, layout, atmosphere, camera, and quality details.
- Return a final copyable prompt.

Do not:

- Generate images.
- Call OpenAI, Gemini, Midjourney, Stable Diffusion, or any image API.
- Handle uploaded images, reference images, masks, inpainting, image-to-image, or multi-image composition.
- Read or modify the user's project code.
- Create API keys, `.env` files, scripts, or provider integrations.
- Put internal skill rules into the final prompt.

If the user asks for image generation, API integration, or image editing, explain briefly that this skill only optimizes text-to-image prompts. If they still want a prompt, convert the visual intent into plain text and continue.

## Input Handling

Read the user's raw request and decide whether it can be treated as a pure text-to-image prompt task.

If the user gives a short idea such as `一只猫`, `现代客厅`, `一个科技海报`, or `钢铁侠大战蜘蛛侠`, do not repeat it as-is. Classify the type and enrich it.

Do not ask follow-up questions unless the core subject is missing or the request has a direct contradiction. Otherwise produce the most reasonable first version.

## Fixed Facts

Extract fixed facts from the user input and preserve them:

- Subject: cat, living room, robot, poster, webpage, character, product, etc.
- Quantity: one cat, two people, three cards, four comic panels, etc.
- Named objects or roles: `ARVUNE`, named characters, product names, title text.
- Explicit style: watercolor, 3D, SU style, comic, cinematic, minimal, etc.
- Explicit colors, materials, time, location, spatial relationships, visible text, exclusions, ratio, size, or output format.

Fixed facts may be organized and strengthened, but not replaced, reversed, or contradicted.

## Visual Type

Choose one main visual type. If several are plausible, choose the strongest user intent.

Available types:

- `photography_life_scene`: realistic photography, daily scenes, pets, objects, food, street scenes.
- `cinematic_scene`: cinematic action, combat, chase, rain, explosions, narrative shots.
- `poster_design`: posters, covers, campaign visuals, promotional key art.
- `typography_poster`: text-led posters where typography is the main visual.
- `product_render`: product render, commercial hero image, premium product photography.
- `ecommerce_visual`: ecommerce main image, detail page, selling-point graphic.
- `interior_design`: living room, bedroom, office, restaurant, hotel, interior space.
- `architecture_render`: architecture exterior, landscape, pavilion, residential facade, urban space.
- `sketchup_style_render`: SU or SketchUp style, massing model, white model, architecture presentation.
- `ui_design`: app, dashboard, software UI, mobile UI, control panel.
- `web_design`: website, homepage, landing page, SaaS or product site.
- `infographic`: infographic, process diagram, structure diagram, knowledge card.
- `comic_manga`: comic, manga, storyboard, panel, action frame.
- `illustration_art`: illustration, watercolor, flat art, decorative art.
- `character_design`: character design, avatar, IP character, persona.
- `game_concept`: game concept art, scene design, HUD, character card.
- `three_d_model_render`: 3D model, figure, toy, model showcase, white model render.
- `logo_concept`: logo concept, symbol, mark sketch.
- `brand_visual`: brand system, VI, brand board, mockups.
- `document_layout`: PPT, report page, white paper, publication layout.
- `unknown_general_image`: still valid as text-to-image, but no stronger category fits.

Default type hints:

- Daily object or pet -> `photography_life_scene`.
- Battle, chase, explosion, rain night, cinematic wording -> `cinematic_scene`.
- Poster, cover, campaign, title, promotion -> `poster_design` or `typography_poster`.
- Living room, bedroom, dining room, office, interior -> `interior_design`.
- Building, pavilion, museum, facade, SU, SketchUp, white model -> `architecture_render` or `sketchup_style_render`.
- Website, official site, landing page -> `web_design`.
- App, dashboard, console, software interface -> `ui_design`.
- Product, package, ecommerce, selling point -> `product_render` or `ecommerce_visual`.
- Comic, storyboard, manga, American comic -> `comic_manga`.
- 3D, model, toy, figure, render -> `three_d_model_render`.

## Enrichment Rules

Only enrich visual expression. Do not change fixed facts.

Allowed enrichment:

- Composition and layout.
- Camera and perspective.
- Lighting and color.
- Materials and detail density.
- Background and scene treatment.
- Atmosphere and spatial depth.
- Render or photographic quality.
- Type-specific visual language.

Disallowed enrichment:

- New main subjects not requested by the user.
- Extra main characters.
- Real brand logos not requested by the user.
- Random visible text.
- Content that conflicts with exclusions.
- Style changes that conflict with explicit user style.

## Output Contract

Default to Chinese unless the user asks for English.

Use this structure unless the user asks for `只要最终 prompt`:

````markdown
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
这里放最终可复制的 prompt。
```

## 边界说明
- 保留了：
- 增强了：
- 没有添加：
````

If the user says `只要最终 prompt`, output only the final prompt text with no explanation.

Before returning, check that the final prompt:

- Preserves fixed facts.
- Has one visual type.
- Adds type-appropriate visual detail.
- Does not add a new main subject.
- Does not put internal rules into the final prompt.
- Is more useful for text-to-image generation than the original input.

## Reference Loading

For simple tasks, this file is enough.

For complex or ambiguous tasks, read only the relevant references:

- `references/01-workflow.md` for the step-by-step workflow.
- `references/02-content-types.md` for visual type definitions.
- `references/03-locked-facts.md` for fixed-fact extraction.
- `references/04-type-templates.md` for type-specific templates.
- `references/05-prompt-craft.md` for prompt writing rules.
- `references/06-output-format.md` for output formatting.
- `references/07-examples.md` for examples.
