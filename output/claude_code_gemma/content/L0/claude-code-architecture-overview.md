# claude-code-architecture-overview

**Parent:** [[content/L1/claude-code-architecture-details|claude-code-architecture-details]] — Claude Code's architecture, based on TypeScript version 2.1.88, is built on a five-value philosophy (Authority, Safety, Reliability, Capability, and Adaptability) operationalized through 13 design principles, featuring a minimal operational harness where reasoning resides in the model (1.6% of codebase) and infrastructure (98.4%) manages a 200K-1M context window via a five-layer compaction pipeline.

This study, authored by Jiacheng Liu, Xiaohan Zhao, Xinyi Shang, and Zhiqiang Shen from the VILA Lab at Mohamed bin Zayed University of Artificial Intelligence and University College London, analyzes the architecture of Claude Code, an agentic coding tool by Anthropic. Claude Code is designed to run shell commands, edit files, and call external services on behalf of a user. The researchers analyzed the publicly available TypeScript source code (version 2.1.88) and compared it with OpenClaw, an independent open-source multi-channel personal assistant gateway. 

Through this analysis, the researchers identify five human values and philosophies that motivate Claude Code's architecture: human decision authority, safety and security, reliable execution, capability amplification, and contextual adaptability. These values are traced through thirteen design principles to specific implementation choices. The core of Claude Code is a simple while-loop that calls the model, runs tools, and repeats. Most of the system's complexity resides in the supporting subsystems: a permission system with seven modes and an ML-based classifier, a five-layer compaction pipeline for context management, four extensibility mechanisms (MCP, plugins, skills, and hooks), a subagent delegation and orchestration mechanism, and append-oriented session storage.

Comparing Claude Code with OpenClaw reveals that different deployment contexts lead to different architectural answers to recurring design questions. For example, Claude Code focuses on per-action safety evaluation, whereas OpenClaw uses perimeter-level access control; Claude Code employs a single CLI loop, whereas OpenClaw uses an embedded runtime within a gateway control plane; and Claude Code uses context-window extensions, while OpenClaw uses gateway-wide capability registration. The study also identifies six open design directions for future agent systems: the observability-evaluation gap, cross-session persistence, harness boundary evolution, horizon scaling, governance, and the evaluative lens.

Claude Code's shift from suggestion-based tools (like GitHub Copilot) to autonomous action-based systems introduces new architectural requirements regarding safety, context management, extensibility, and delegation. Anthropic's internal survey of 132 engineers and researchers found that approximately 27% of Claude Code-assisted tasks were work that would not have been attempted without the tool, suggesting the architecture enables qualitatively new workflows. 

Regarding the five motivating values, Human Decision Authority ensures users retain ultimate control through a principal hierarchy (Anthropic, operators, then users). The system uses sandboxing and auto-mode classifiers to define boundaries where the agent can work freely, avoiding per-action approval fatigue. Safety, Security, and Privacy focus on protecting users and data from risks such as overeager behavior, honest mistakes, prompt injection, and model misalignment. Reliable Execution ensures the agent stays coherent and verifies work through a three-phase loop: gather context, take action, and verify results. Capability Amplification aims to increase what humans can accomplish by investing in deterministic infrastructure (context management, tool routing, recovery) rather than rigid decision scaffolding. Finally, Contextual Adaptability allows the system to fit the user's specific project and tools through mechanisms like CLAUDE.md, skills, MCP, hooks, and plugins. Longitudinal data shows that auto-approve rates increase from approximately 20% at fewer than 50 sessions to over 40% by 750 sessions.

These values are operationalized through thirteen design principles:
1. Deny-first with human escalation (Authority, Safety)
2. Graduated trust spectrum (Authority, Adaptability)
3. Defense in depth with layered mechanisms (Safety, Authority, Reliability)
4. Externalized programmable policy (Safety, Authority, Adaptability)
5. Context as scarce resource with progressive management (Reliability, Capability)
6. Append-only durable state (Reliability, Authority)
7. Minimal scaffolding, maximal operational harness (Capability, Reliability)
8. Values over rules (Capability, Authority)
9. Composable multi-mechanism extensibility (Capability, Adaptability)
10. Reversibility-weighted risk assessment (Capability, Safety)
11. Transparent file-based configuration and memory (Adaptability, Authority)
12. Isolated subagent boundaries (Reliability, Safety, Capability)
13. Graceful recovery and resilience (Reliability, Capability)
