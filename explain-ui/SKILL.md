---
name: explain-ui
description: Explain a UI element's appearance or motion, its controlling parameters, and how to adjust them.
disable-model-invocation: true
---

Help the user connect the chosen element's appearance or motion to its implementation and understand how to adjust it.

Explain without modifying files by default. When the user explicitly requests changes, carry them out within the requested scope.

1. Locate the element and its implementation.
   Inspect the relevant code and, when a running page is accessible, observe the relevant states.
   Identify whether CSS, Motion, or another mechanism drives the effect.
   With only a screenshot, label possible implementations as hypotheses and current parameter values as unknown.

2. Explain the mechanism.
   Briefly describe how the parts work together to produce the effect.
   For motion, explain the trigger, starting and ending states, and transition.
   Cite the smallest relevant code excerpts and their locations.

3. Explain the key parameters that affect the target effect.
   For each parameter, explain its location, current value and unit, purpose, and how changing it would affect the result.
   For numeric parameters, explain the effects of increasing or decreasing them; for curves or modes, explain the effects of alternatives.
   Discuss interacting parameters together.
   Present code using the current environment's supported display capabilities, next to its explanation.

4. Help the user judge the result.
   Explain the benefits and tradeoffs of the current choices in the context of the element's purpose.
   For suggested adjustments, explain when they would help and what observable behavior would indicate an improvement, such as timely feedback, legibility, or continuity during repeated interaction.
