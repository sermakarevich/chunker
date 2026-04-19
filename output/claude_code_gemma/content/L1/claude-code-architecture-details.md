# claude-code-architecture-details

**Parent:** [[index]]

Claude Code is an agentic coding tool by Anthropic, analyzed by Jiacheng Liu, Xiaohan Zhao, Xinyi Shang, and Zhiqiang Shen from the VILA Lab at Mohamed bin Zayed University of Artificial Intelligence and University College London. The researchers analyzed the publicly available TypeScript source code (version 2.1.88) of Claude Code and compared it with OpenClaw, an independent open-source multi-channel personal assistant gateway. This analysis reveals that Claude Code shifts from suggestion-based tools (like GitHub Copilot) to autonomous action-based systems, introducing new architectural requirements for safety, context management, extensibility, and delegation. An internal Anthropic survey of 132 engineers and researchers found that approximately 27% of tasks assisted by Claude Code were tasks that users would not have attempted without the tool, indicating that the architecture enables qualitatively new workflows.

The architecture of Claude Code is motivated by five human values and philosophies: human decision authority, safety and security, reliable execution, capability amplification, and contextual adaptability. These values are operationalized through thirteen design principles:

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

These principles distinguish Claude Code from three alternative design families: rule-based orchestration (e.g., LangGraph, which prioritizes scaffolding over a minimal harness using explicit state graphs and typed edges), container-isolated execution (e.g., SWE-Agent and OpenHands, which rely on Docker isolation), and version-control-as-safety (e.g., Aider, which uses Git rollback as the primary safety mechanism). Claude Code is characterized by its combination of of minimal decision scaffolding, layered policy enforcement, and deny-first defaults.

From a value-to-architecture mapping, Human Decision Authority motivates deny-first evaluation, the graduated trust spectrum, append-only state for auditable history, externalized programmable policy, and values-over-rules. Safety, Security, and Privacy motivates defense in depth, defense-first defaults, reversibility-weighted assessment, externalized policy, and isolated subagent boundaries. Reliable Execution motivates treating context as a scarce resource, append-only durable state, graceful recovery, isolated subagent boundaries, and defense in depth. Capability Amplification motivates minimal scaffolding, java-based extensibility, composable extensibility, reversibility-weighted risk, context management, and graceful recovery. Contextual Adaptability motivates transparent file-based memory, composable extensibility, the graduated trust spectrum, and externalized programmable policy. This mapping also shows that Claude Code does not impose explicit planning graphs on model reasoning, does not provide a single unified extension mechanism, and does not restore all session-scoped trust-related state across resumes.

Claude Code's architecture consists of seven functional components connected by a main data flow: a user submits a prompt through one of several interfaces, which feeds into a shared agent loop. The agent loop assembles context, calls the Claude model, and receives responses that may include tool-use requests. These requests are routed through a permission system and dispatched to concrete tools that interact with the execution environment. State and persistence mechanisms record conversation transcripts, manage session identity, and support resume, fork, and rewind operations. This architecture answers four recurring design questions:

1. Where does reasoning live? Reasoning resides in the model, while the harness is responsible for execution. The model emits `tool_use` blocks, which the harness parses, checks permissions, and dispatches. The model never directly accesses the filesystem, runs shell commands, or makes network requests. Only about 1.6% of Claude Code's codebase constitutes AI decision logic, while 98.4% is operational infrastructure. This contrasts with Devin, which maintains explicit planning structures, and LangGraph, which uses developer-defined state graphs.

2. How many execution engines? Claude Code uses a single `queryLoop()` function (an async generator in `query.ts`) for all interactions, whether through an interactive terminal, headless CLI invocation (`claude -p`), the Agent SDK, or an IDE integration. This differs from systems with mode-specific engines.

3. What is the default safety posture? The posture is deny-first with human escalation, where deny rules override ask rules, which in turn override allow rules. Unrecognized actions are escalated to the user. Multiple independent safety layers—permission rules, `PreToolUse` hooks, `yoloClassifier.ts` (an ML-based classifier), and optional shell sandboxing—apply in parallel. This differs from the container-based isolation of SWE-Agent and OpenHands or the Git-based rollback of Aider.

4. What is the binding resource constraint? The context window (200K for older models, 1M for the Claude 4.6 series) is the binding constraint. To manage this, a five-layer compaction pipeline (budget reduction, snip, microcompact, context collapse, and auto-compact) executes before every model call, located in `query.ts:365–453`. Other decisions like lazy loading of instructions and deferred tool schemas also limit context consumption. This contrasts with architectures that prioritize compute budget or working memory.

Regarding long-term capability preservation, the researchers applied an evaluative lens to see if the architecture preserves human skill. This is informed by an Anthropic study of 132 engineers and researchers documenting a 

## Children
- [[content/L0/claude-code-architecture-overview|claude-code-architecture-overview]] — This study analyzes Claude Code's TypeScript source code (v2.1.88) to identify five motivating human values—authority, safety, reliability, amplification, and adaptability—and thirteen design principles that govern its agentic architecture.
- [[content/L0/claude-code-architecture-overview-2|claude-code-architecture-overview-2]] — Claude Code's architecture is built on five core values operationalized through 13 design principles, featuring a thin reasoning layer (1.6% of codebase) and a comprehensive five-layer context compaction pipeline to manage context windows up to 1M tokens.
