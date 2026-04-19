# claude-code-architecture-overview-2

**Parent:** [[content/L1/claude-code-architecture-details|claude-code-architecture-details]] — Claude Code's architecture, based on TypeScript version 2.1.88, is built on a five-value philosophy (Authority, Safety, Reliability, Capability, and Adaptability) operationalized through 13 design principles, featuring a minimal operational harness where reasoning resides in the model (1.6% of codebase) and infrastructure (98.4%) manages a 200K-1M context window via a five-layer compaction pipeline.

The five human values and philosophies motivating Claude Code's architecture—human decision authority, safety and security, reliable execution, capability amplification, and contextual adaptability—are operationalized through thirteen design principles. Each of these principles addresses a recurring question that production coding agents must resolve. These principles distinguish Claude Code from three alternative design families: rule-based orchestration (such as LangGraph, which uses explicit state graphs and typed edges to prioritize scaffolding over a minimal harness), container-isolated execution (such as SWE-Agent and OpenHands, which rely on Docker isolation rather than layered policy enforcement), and version-control-as-safety (such as Aider, which uses Git rollback as the primary safety mechanism instead of deny-first evaluation). Claude Code is distinctive in its combination of minimal decision scaffolding, layered policy enforcement, values-based judgment, deny-first defaults, progressive context management, and composable extensibility.

From a value-to-architecture mapping, the five motivating values trace through the design principles to specific architectural decisions:
- Human Decision Authority motivates deny-first evaluation, the graduated trust spectrum, append-only state for auditable history, externalized programmable policy, and values-over-rules.
- Safety, Security, and Privacy motivates defense in depth, deny-first defaults, reversibility-weighted assessment, externalized policy, and isolated subagent boundaries.
- Reliable Execution motivates treating context as a scarce resource, append-only durable state, graceful recovery, isolated subagent boundaries, and defense in depth.
- Capability Amplification motivates minimal scaffolding, composable extensibility, reversibility-weighted risk, context management, and graceful recovery.
- Contextual Adaptability motivates transparent file-based memory, composable extensibility, the graduated trust spectrum, and externalized programmable policy.

This mapping reveals that Claude Code does not impose explicit planning graphs on model reasoning, does not provide a single unified extension mechanism, and does not restore all session-scoped trust-related state across resumes.

Additionally, the researchers apply an evaluative lens of long-term capability preservation to determine if the architecture preserves human skill. This is informed by an Anthropic study of 132 engineers and researchers documenting a "paradox of supervision" where AI overreliance risks skill atrophy, and independent research showing developers in AI-assisted conditions score 17% lower on comprehension tests. While not a primary design driver, this concern is treated as a cross-cutting question across all five values to see if short-term amplification comes at the cost of long-term human understanding and codebase coherence.

Claude Code's architecture consists of seven functional components connected by a main data flow: a user submits a prompt through one of several interfaces, which feeds into a shared agent loop. The agent loop assembles context, calls the Claude model, receives responses that may include tool-use requests, routes those requests through a permission system, and dispatches approved actions to concrete tools that interact with the execution environment. State and persistence mechanisms record conversation transcripts, manage session identity, and support resume, fork, and rewind operations. This architecture answers four recurring design questions:

1. Where does reasoning live? Reasoning resides in the model, while the harness is responsible for execution. The model emits tool_use blocks, which the harness parses, checks permissions, and dispatches. The model never directly accesses the filesystem, runs shell commands, or makes network requests. Only about 1.6% of Claude Code’s codebase constitutes AI decision logic, while 98.4% is operational infrastructure. This contrasts with Devin, which maintains explicit planning structures, and LangGraph, which uses developer-defined state graphs.

2. How many execution engines? Claude Code uses a single queryLoop() function for all interactions, whether through an interactive terminal, headless CLI invocation, the Agent SDK, or an IDE integration. This differs from systems with mode-specific engines for different surfaces.

3. What is the default safety posture? The posture is deny-first with human escalation, where deny rules override ask rules, which in turn override allow rules. Unrecognized actions are escalated to the user. Multiple independent safety layers—permission rules, PreToolUse hooks, an auto-mode classifier, and optional shell sandboxing—apply in parallel. This differs from SWE-Agent and OpenHands' container-based isolation or Aider's Git-based rollback.

4. What is the binding resource constraint? The context window (200K for older models, 1M for the Claude 4.6 series) is the binding constraint. To manage this, a five-layer compaction pipeline (budget reduction, snip, microcompact, context collapse, and auto-compact) executes before every model call. Other decisions like lazy loading of instructions and deferred tool schemas also limit context consumption. This contrasts with architectures that prioritize compute budget or working memory.

To illustrate these principles, the study uses the running example of fixing a failing test in auth.test.ts.

The high-level system structure maps to specific source files and directories:
- The User interacts with interfaces and approves permissions.
- Interfaces (Interactive CLI, headless CLI (claude -p), Agent SDK, and IDE/Desktop/Browser) all feed the same agent loop.
- The Agent loop is implemented as the queryLoop() async generator in query.ts.
- The Permission system consists of deny-first rule evaluation (permissions.ts), an auto-mode ML classifier (yoloClassifier.ts), and hook-based interception (types/hooks.ts).
- Tools include up to 54 built-in tools (19 unconditional, 35 conditional on feature flags and user type) assembled via assembleToolPool() (tools.ts), merged with MCP-provided tools. Plugins and skills contribute indirectly.
- State & persistence includes append-only JSONL session transcripts (sessionStorage.ts), global prompt history (history.ts), and subagent sidechain files.
- The Execution environment includes shell execution with optional sandboxing (shouldUseSandbox.ts), filesystem operations, web fetching, and MCP server connections.

Entry point main() in main.tsx initializes security settings (including NoDefaultCurrentDirectoryInExePath to prevent Windows PATH hijacking) and registers signal handlers.

The architecture is further decomposed into five layers:
- Surface layer: Entry points (src/entrypoints/) and rendering (src/screens/ and src/components/ using the ink framework). It includes the interactive CLI, headless CLI, Agent SDK, and Agent SDK.
- Core layer: The agent loop (queryLoop() in query.ts) and the compaction pipeline of five sequential shapers (budget reduction, snip, microcompact, context collapse, and auto-compact) located in query.ts:365–453.
- Safety/action layer: The permission system (permissions.ts) with up to seven permission modes (types/permissions.ts) and the yoloClassifier.ts ML classifier, a hook pipeline of 27 event types (coreTypes.ts; types/hooks.ts) where 5 are safety-related and 22 are for orchestration, an extensibility subsystem for plugins and skills, tool pool assembly (assembleToolPool() in tools.ts), and a shell sandbox (shouldUseSandbox.ts). Subagent spawning (AgentTool.tsx, runAgent.ts) re-enters the queryLoop() with an isolated context window and returns only a summary to the parent.
- State layer: Handles context assembly, runtime state, persistence, memory, and sidechains.
- Backend layer: Handles execution backends and external resources.
