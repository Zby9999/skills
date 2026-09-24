---
name: eval-driven-optimize
description: Iteratively improve a target using explicit evaluations and guardrails.
disable-model-invocation: true
---

# Eval-Driven Optimization

## 1. Identify the target

If the target is unclear, ask "What do you want to optimize?" and wait for the answer. Otherwise, proceed. Establish verifiable evaluation criteria before optimizing.

## 2. Define the goal and baseline

Define a goal with guardrails. Evaluate the current version and save it as the baseline and current best.

## 3. Hill-climb

Repeat continuously and autonomously:

- Explore a new angle and propose a candidate.
- Evaluate it against the current best using fixed criteria.
- Keep verified improvements within the guardrails; discard the rest.
- Use feedback for the next attempt; change approach when progress stalls.

## 4. Stop and deliver

Stop when substantially different approaches yield no meaningful improvement, or when a guardrail or the user requires it. Return the best verified solution, its improvement over the baseline, and the reason for stopping.
