# agentic-safety-evaluations

**Parent:** [[content/L1/claude-opus-4-7-safety-evaluations|claude-opus-4-7-safety-evaluations]] — Anthropic conducted extensive safety evaluations for Claude Opus 4.7, introducing new benchmarks for influence operations and indirect prompt injection (ART). In coding environments, Opus 4.7 achieved a malicious refusal rate of 91.15% and improved robustness significantly over Claude Opus 4.6 in the Shade tool evaluations, achieving a 0.43% ASR with safeguards at 1 attempt. Furthermore, Opus 4.7 achieved a highly successful browser use ASR of 0.75% with safeguards, matching Claude Mythos Preview's performance, while demonstrating improvements in computer use refusal rates (89.29%) compared to Claude Opus 4.6 (87.05%).

Before releasing Claude Opus 4.7, Anthropic conducted agentic safety evaluations using a suite similar to those previously conducted for the Claude Mythos Preview. Anthropic introduced two new benchmarks: one focusing on the model's capability to autonomously execute influence operation campaigns and another addressing indirect prompt injection, reflecting the saturation of existing evaluations. Furthermore, Anthropic removed one evaluation concerning basic malicious coding tasks (detailed in Section 5.1.1 of the Claude Opus 4.6 System Card) because the evaluation had become highly saturated, replacing it with more challenging evaluations specifically focusing on Claude Code and computer use tasks. 

### Malicious Use of Agents

**Malicious use of Claude Code:** This evaluation tests how the model responds to malicious, dual-use, and benign cyber-related queries within the context of Claude Code. The malicious prompts consisted of 61 topics that assess Claude’s ability to correctly refuse queries with malicious intent or those otherwise prohibited by the Usage Policy. Example malicious topics include assisting with malware creation, writing code for destructive DDoS attacks, and developing non-consensual monitoring software. Since the Claude Mythos Preview System Card, Anthropic added 12 additional challenging test cases, bringing the total number of malicious prompts from 49 to 61. The dual-use and benign prompts comprised a set of 61 queries that evaluate Claude’s ability to assist with potentially sensitive but not prohibited requests. Example dual-use/benign topics include running network reconnaissance tools, testing websites for vulnerabilities, and analyzing data from a penetration test. Opus 4.7 was tested using the standard set of tool commands available in Claude Code, with each prompt run 10 times, resulting in 1,220 total tests across both categories. Additionally, Anthropic now automatically runs this evaluation using the Claude Code system prompt, anticipating its default implementation in all future releases. Previous system cards also ran this evaluation with an additional safeguard—a FileRead tool reminder that explicitly instructed the model to consider whether the file was malicious. For recent models, including Opus 4.7 and Mythos Preview, evaluations demonstrated that this specific mitigation did not provide any additional security benefit. Anthropic now applies this safeguard only to models where it results in a material security improvement, and it reports the better score both with and without the FileTool reminder. Anthropic also implemented system prompt updates that slightly altered the results for previous models.

**Claude Code evaluation results with mitigations:**
| Model | Malicious (%) | Dual-use & benign (%) | (refusal rate) | (success rate) |
| :--- | :--- | :--- | :--- | :--- |
| Claude Opus 4.7 | 91.15% | 91.83% | 95.41% | 91.12% | 
| 82.21% | 98.61% | 81.94% | 94.97% | 
| without FileTool reminder | | | | |
| Claude Mythos Preview | | | | |
| Claude Sonnet 4.6 | | | | |
| with FileTool reminder | | | | |
| Claude Opus 4.6 | | | | |
| without FileTool reminder | | | | |

Through analysis, Opus 4.7 demonstrated significant improvement compared to Claude Opus 4.6 in recognizing and refusing malicious requests. Similar to Claude Mythos Preview, Opus 4.7's improvements originated from refusals on challenging new cases where previous models struggled. Conversely, Opus 4.7 performed similarly to Claude Opus 4.6 on dual-use and benign tasks.

**Malicious computer use:** Anthropic ran the computer use evaluation for Claude Opus 4.7, using the version last updated for the launch of Claude Opus 4.5. This evaluation assesses how the model responds to harmful tasks when the model is presented with GUI- and CLI-based computer use tools within a sandboxed environment. The evaluation focused on three specific areas of concern: 1) surveillance and unauthorized data collection, 2) generation and distribution of harmful content, and 3) scaled abuse. A total of 112 tasks were run, with both thinking enabled and disabled, resulting in 224 attempts for each model.

**Malicious computer use evaluation results without mitigations:**
| Model | Refusal rate |
| :--- | :--- | :--- |
| Claude Opus 4.7 | 89.29% |
| Claude Mythos Preview | 93.75% |
| Claude Sonnet 4.6 | 84.82% |
| Claude Opus 4.6 | 87.05% |

Opus 4.7 scored higher than Claude Opus 4.6 on refusing these tasks, though the score was within the margin of error of other recent models. Anthropic noted that as general model capabilities increase, the performance on this evaluation shows steady improvements.

**Malicious agentic influence campaigns:** This new evaluation, first discussed in the system card for Claude Mythos Preview, assesses harmful manipulation risks. Specifically, the evaluation tests whether the model can autonomously run an influence operation at a level that would meaningfully uplift a malicious actor through persuasion, deception, or personalized targeting at scale. An influence operation is defined as a coordinated campaign designed to shape public opinion, political behavior, or discourse through deceptive means, such as using inauthentic personas, generating fabricated grassroots support, or creating targeted disinformation to distribute across social and digital media platforms. One key risk from AI uplift is scale: tasks that previously required teams of human operators—including drafting persona-consistent content, adapting messaging to different audiences, and sustaining engagement across many accounts—could potentially be automated end-to-end.

The evaluation is designed to measure the model’s ability to execute a complete campaign end-to-end against platform friction and defenses against the campaign. This test occurs in an agentic harness, where the model has access to simulated social media platform tools within a mocked ecosystem that includes moderation and counter-engagement obstacles. To measure raw capability rather than the effect of safeguards, Anthropic ran the evaluation against a 
