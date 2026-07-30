---
name: read-paper-roughly
description: Rough-read an academic paper. Use when the user wants its core problem, research value, relevance, and most worthwhile sections assessed.
---

# Read Paper Roughly

## Workflow

Use the paper content supplied by the user, such as a PDF, pasted text, DOI, arXiv link, or paper title. If no paper is available, ask for the paper first.

Before assessing relevance, verify that the user's research goal is explicit in the current conversation. If it is absent or unclear, ask one concise clarifying question and wait for the answer. This step is complete only when the user's concrete research goal is available.

## Output

Use these sections:

1. `Full Abstract Translation`
   Translate the full Abstract faithfully when the Abstract text is available from the user-provided paper. Preserve technical terms where translation would reduce precision, and optionally include the original term in parentheses.

2. `The Problem This Paper Actually Solves`
   Explain the concrete problem the paper addresses. Focus on the valuable underlying bottleneck, failure mode, cost, uncertainty, or capability gap, not just the authors' claimed innovation points.

3. `Research Relevance`
   Assess relevance to the confirmed research goal. Explain why it is useful, partially useful, or not useful. Separate direct usefulness, indirect inspiration, and limitations.

4. `Most Worthwhile Sections`
   Identify the sections, figures, tables, experiments, or method details most worth reading closely. Explain why each part deserves attention.

Keep the answer analytical rather than encyclopedic. Prefer concrete claims tied to the paper over broad background summaries.
