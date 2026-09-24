---
name: eval-driven-optimize
description: Iteratively improve a target using explicit evaluations and guardrails.
disable-model-invocation: true
---

# Eval-Driven Optimization

## 1. Identify the target

If the target is unclear, ask "What do you want to optimize?" and wait for the answer. Otherwise, proceed. Establish verifiable evaluation criteria before optimizing.

## 2. Define the goal and baseline

Briefly state and record the following. Reuse known requirements; ask only about missing details that affect tradeoffs:

- **Goal:** Real-world benefit, primary metric, improvement direction, and minimum meaningful gain.
- **Evaluation:** Fixed method, representative samples, and pass criteria. Prefer direct measurements. Validate proxy metrics against real-world benefits; ground model judgments in an explicit rubric and evidence.
- **Guardrails:** Editable scope, required behavior and quality, complexity limits, and experiment budget. If no budget is specified, state a default maximum of 12 iterations.

Evaluate the current version and save a recoverable baseline. Repeat noisy measurements to establish a reliable improvement threshold. Begin iteration once the evaluation works and the baseline is recorded.

## 3. Hill-climb

Repeat autonomously within the guardrails and budget:

1. Use evaluation feedback and prior attempts to find a new bottleneck or angle. Form one testable improvement hypothesis.
2. Create a reversible candidate from the current best version. Test one hypothesis per iteration and preserve the best version as a fallback.
3. Evaluate in a separate step using fixed criteria, identical conditions, and observed results. Check every guardrail. Judge the evidence rather than the rationale for the change; remeasure small or unstable gains.
4. Keep the candidate only if it passes all guardrails and meets the improvement threshold; update the current best. Otherwise, undo this iteration while preserving the user's existing work. Keep the evaluation fixed; if it needs correction, remeasure both baseline and candidate.
5. Briefly log the hypothesis, result, keep/revert decision, and lesson. Carry verified gains into subsequent regression checks, then seek the next improvement.

Continue exploring within scope after reaching the initial target unless the user explicitly made it the endpoint. After 3 consecutive iterations without meaningful improvement, use the remaining budget to try at least 2 substantially different directions, including a structural alternative.

## 4. Stop and deliver

Stop and preserve the best version when changing direction yields no meaningful improvement, the budget is exhausted, the user stops the run, or further progress requires crossing a guardrail. Deliver the best solution, baseline comparison, guardrail results, stopping reason, and remaining opportunities. Describe it as the best verified so far; claim a global optimum only with sufficient proof.
