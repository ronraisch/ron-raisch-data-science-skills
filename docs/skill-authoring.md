# Concise skill authoring — reviewed 2026-10-31

Use task-specific instructions with explicit inputs, definitions, actions, outputs and stop rules. Keep calculations and critical gates executable. Reference another skill for a distinct owned task; do not duplicate its procedure. Link detailed contracts or tools directly when required. Do not make an agent open a long upstream method merely to discover its procedure.

This is a supported modern design choice, not proof of an optimal prompt length for Ornith or Qwen. Smaller models may need more concrete examples. Remove repetition and irrelevant detail, not scientific controls, required context or failure criteria. Retain the original repositories' attribution, pins, licenses and offline utilities. ORIGIN.json carries source URLs outside the agent's required instructions.

## Primary sources

- [Qwen Code: Agent Skills](https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/): clear step-by-step instructions and one capability per skill; critical rules belong in executable enforcement. Open-model ecosystem guidance, not a prompt-length benchmark.
- [LangChain: Revamping Skills in Deep Agents, October 7, 2026](https://www.langchain.com/blog/revamping-skills-in-deep-agents): load only relevant instructions/resources. Supports focused context, not unconditional deletion of detail.
- [LangChain: How Deep Agents Remember, October 14, 2026](https://www.langchain.com/blog/context-engineering-deep-agents-remember): keep irrelevant context out and retrieve necessary context when needed.
- [Google Cloud: How we ship Google Agent Skills, October 28, 2026](https://cloud.google.com/blog/topics/developers-practitioners/behind-the-scenes-two-months-later-how-we-ship-google-agent-skills-like-products): compact core instructions, executable procedures and one-hop references; warns about chained reads. Not evidence specific to Qwen/Ornith.
- [Anthropic: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): concise instructions and task-appropriate guardrails; explicitly notes that less capable models may need more guidance. Claude-specific guidance is not open-model experimental evidence.

## Limits and conflicting guidance

[Hugging Face's skill-format course](https://huggingface.co/learn/context-course/unit1/skill-format) also emphasizes explicit steps and executable examples, but gives a much larger body-length range (400–800 lines). There is no consistent universal line-count rule across these sources. [A controlled long-document study](https://arxiv.org/abs/2607.17598) finds benefits depend on harness and corpus scale and warns about deeper routing. Its document-QA experiments do not establish a best length for scientific skills on local models.

Decision: remove mandatory long-method loading and repeated generic wrapper text; retain direct scientific procedures, necessary shared contracts and optional offline resources. No local-model performance claim or new benchmark evaluation is included.
