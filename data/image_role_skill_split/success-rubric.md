# Lightweight Optimization Rubric v0.1

This first set tests stability, controllability, and restraint rather than maximum visual richness.

## What This Round Tests

- Fixed-fact preservation: subject, quantity, color, material, time, style, and explicit exclusions remain intact.
- Visual type judgment: photography, interior, poster, UI, web, infographic, character, and architecture cases stay in the right family.
- Lightweight optimization: add only necessary visual details, not a full creative rewrite.
- Exclusion compliance: constraints such as no people, no logo, no text, no extra subject remain visible.
- Locked copy: supplied titles, buttons, and Chinese text are not rewritten.
- No new main subjects: do not add unrequested people, animals, brands, characters, or plot.
- Chinese output: Chinese input should produce Chinese final prompts.
- Final prompt only: provider-facing prompt should not contain explanations, rules, or analysis.

## Passing Standard

A passing output must:

1. Preserve all fixed facts.
2. Match the visual type implied by the input.
3. Add only 3-6 useful visual enhancement points.
4. Avoid new main subjects.
5. Preserve explicit exclusions.
6. Be directly usable as a text-to-image prompt.

## Failure Conditions

Fail the case if the output:

- Changes the user subject.
- Changes quantity.
- Changes explicit color, material, time, or style.
- Removes an exclusion.
- Adds a new main subject.
- Becomes an overlong story or highly expanded prompt.
- Outputs explanation instead of the final prompt.
- Leaks internal skill rules into the prompt.
- Clearly misclassifies the visual type.

## Length Guidance

- Ordinary image prompts: about 40-90 Chinese characters.
- Complex poster, UI, web, or infographic prompts: about 80-160 Chinese characters.

This is a calibration set. Use these 10 items as `train v0.1`; add separate validation and test items before treating results as evidence of real improvement.
