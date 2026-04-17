# multimodal-professional-benchmarks

**Parent:** [[content/L1/opus-4-7-multi-benchmark-evaluation|opus-4-7-multi-benchmark-evaluation]] — Claude Opus 4.7 demonstrated strong performance across varied benchmarks, achieving an 87.6% score on the SWE-bench Verified subset and an 86.3% score on OfficeQA, and a 79.3% score on the BrowseComp web search benchmark. In agentic and coding security tests, Opus 4.7 showed significant gains, dropping the Attack Success Rate in the Coding Environment from 25.92% (for Opus 4.6) to 2.34% at 1 attempt without safeguards.

The document evaluates multiple specialized benchmarks to assess model capabilities, covering multimodal reasoning, professional software use, and multilingual understanding.

**ChartXiv Reasoning**
This comprehensive evaluation suite, built from 2,323 real-world charts sourced from arXiv papers across eight major scientific disciplines, tests models' ability to synthesize visual information across complex scientific charts to answer multi-step reasoning questions. Models are evaluated on 1,000 questions from the validation split, with average scores reported over five runs.
- Using adaptive thinking, maximum effort, and no tools, Claude Opus 4.7 achieved a score of 82.1%. With adaptive thinking, maximum effort, and Python tools, Claude Opus 4.7 achieved a score of 91.0%. 
- Claude Opus 4.6 scored 69.1% and 84.7% respectively, using the same settings.

**ScreenSpot-Pro**
ScreenSpot-Pro is a GUI grounding benchmark that tests whether models can precisely locate specific user interface elements in high-resolution screenshots of professional desktop applications given natural language instructions. The benchmark comprises 1,581 expert-annotated tasks spanning 23 professional applications—including IDEs, CAD software, and creative tools—across three operating systems, requiring target elements to occupy on average less than 0.1% of the screen area.
- When using adaptive thinking, maximum effort, and no tools, Claude Opus 4.7 achieved a score of 79.5% on ScreenSpot-Pro. With adaptive thinking, maximum effort, and Python tools, Claude Opus 4.7 achieved a score of 87.6%. 
- Claude Opus 4.6 scored 57.7% and 83.1% using the same settings.
- Additionally, researchers observed a significant uplift in ScreenSpot-Pro scores when increasing the maximum image resolution. With adaptive thinking and maximum effort, Claude Opus 4.7 scored 79.5% without Python tools and 87.6% with Python tools at the lower image resolution (up to 1568px along a single dimension and up to 1.15MP in total). When using the new resolution (up to 2576px along a single dimension and up to 3.75MP in total), Claude Opus 4.7 scored 69.0% and 85.9% on the lower resolution setting, demonstrating improved performance on the higher resolution setting.

**OSWorld**
OSWorld is a multimodal benchmark that evaluates an agent’s ability to complete real-world computer tasks, such as editing documents, browsing the web, and managing files, by interacting with a live Ubuntu virtual machine via mouse and keyboard actions. The standard evaluation followed default settings of 1080p resolution and a maximum of 100 action steps per task.
- Claude Opus 4.7 achieved an OSWorld score of 78.0% (first-attempt success rate, averaged over five runs).
- Re-running Claude Opus 4.6 under an updated agent scaffolding (which included guidance to batch predictable actions into a single tool call, declaring tasks infeasible early, and per-turn awareness of the remaining step budget) yielded 72.6%, which is within run-to-run noise of Claude Opus 4.6's previously reported 72.7%, indicating that the setup improvements did not provide a meaningful performance lift for prior Claude models.

**OfficeQA**
OfficeQA is a benchmark for evaluating language models on realistic office-style question answering tasks. These tasks are derived from documents, spreadsheets, and presentations that knowledge workers routinely handle, requiring models to read long, heterogeneous professional documents and answer questions that depend on precise extraction, synthesis across sections, and numerical or tabular reasoning.
- Claude Opus 4.7 achieved 86.3% on OfficeQA and 80.6% on OfficeQA Pro, using exact-match grading for both (with 0% allowable relative error).

**Finance Agent**
Finance Agent is a public benchmark published by Vals AI that assesses a model’s performance on research involving SEC filings of public companies. Vals AI evaluated Claude Opus 4.7 on this benchmark (using adaptive thinking and high effort) and found that Claude Opus 4.7 achieved a score of 64.4%, placing it above all currently evaluated models on the benchmark.

**MCP Atlas**
MCP Atlas assesses language model performance on real-world tool use via the Model Context Protocol (MCP). This benchmark measures how well models execute multi-step workflows by discovering appropriate tools, invoking them correctly, and synthesizing results into accurate responses. Tasks require models to work with authentic APIs and real data across multiple tool calls in production-like MCP server environments, requiring management of errors and retries, and coordination across different servers.
- Vals AI evaluated Claude Opus 4.7 using adaptive thinking and maximum effort, and found a 77.3% Pass Rate, which improved upon Claude Opus 4.6's 75.8%, ranking Claude Opus 4.7 second on the public leaderboard. In an extended configuration scale run (256 turns / 100 tools vs. the leaderboard's 20 turns / 10–25 tools), Opus 4.7 achieved a 79.5% (maximum score; 79.7% high), suggesting potential for improved performance with a larger tool-calling budget.

**Vending-Bench**
Vending-Bench is a benchmark from Andon Labs that measures AI models’ performance on running a business over long time horizons. Unlike real-world experiments from Project Vend, Vending-Bench is purely simulated. Models are tasked with managing a simulated vending machine business for a year, starting with a $500 balance, and are scored on their final bank account balance, which requires demonstrating sustained coherence and strategic planning across thousands of business decisions. Tasks require models to successfully find and negotiate with suppliers via email, manage inventory, optimize pricing, and adapt to dynamic market conditions.
- When Opus 4.7 was run with Max and High effort, Claude Opus 4.7 achieved a final balance of $10,937 on Max effort and $7,971 on High effort, compared to Claude Opus 4.6's previous State-of-the-Art (SOTA) of $8,018.
