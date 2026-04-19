# claude-code-architecture-deep-dive

**Parent:** [[index]]

Claude Code's architecture is centered around a reactive loop, implemented as the `queryLoop()` async generator in `query.ts`, which operates as a while-loop following the ReAct pattern. This loop handles the interaction between the model and the execution environment, where reasoning resides in the model and the harness handles execution. Only 1.6% of the codebase is AI decision logic, while 98.4% is operational infrastructure. The `QueryEngine` class in `QueryEngine.ts` acts as a conversation wrapper for non-interactive surfaces (headless CLI, Agent SDK), delegating to the shared `query()` function; however, the interactive CLI bypasses `QueryEngine` and calls `query()` directly.

### Context Assembly and Management
Context is treated as a scarce resource, with a context window of 200K for older models and 1M for the Claude 4.6 series. Context is assembled from nine sources: the system prompt (including output style modifications and `--append-system-prompt` content), environment info via `getSystemContext()` (including git status and `BREAK_CACHE_COMMAND` injections), the `CLAUDE.md` hierarchy via `getUserContext()`, path-scoped rules loaded lazily when reading files in matching directories, asynchronously prefetched auto memory, tool metadata (skill descriptions, MCP tool names, and deferred tool definitions via `ToolSearch`), conversation history, tool results (file reads, command outputs, subagent summaries), and compact summaries. The `CLAUDE.md` hierarchy is implemented as a four-level instruction hierarchy via `claudemd.ts` and uses plain-text Markdown for transparency, avoiding vector similarity indexes in favor of an LLM-based scan of memory-file headers to select up to five relevant files on demand.

To manage the context bottleneck, the system employs a five-layer compaction pipeline in `query.ts` that executes before every model call:
1. **Budget reduction (`applyToolResultBudget()`):** Enforces per-message size limits on tool results, replacing oversized outputs with content references. Content replacements are persisted for agent and session query sources to allow reconstruction on resume.
2. **Snip (`snipCompactIfNeeded()`):** A lightweight trim of older history segments, gated by `HISTORY_SNIP`. Freed tokens are passed to auto-compact.
3. **Microcompact:** Performs fine-grained compression. It includes a time-based path and an optional cache-aware path (gated by `CACHED_MICROCOMPACT`) that defers boundary messages until after the API response to use actual `cache_deleted_input_tokens`.
4. **Context collapse (`applyCollapsesIfNeeded()`):** A read-time projection over conversation history where summary messages live in a collapse store; the model sees the collapsed version while the full history remains available.
5. **Auto-compact (`compactConversation()`):** Triggers a full model-generated summary via `compact.ts` if the context still exceeds pressure thresholds after the previous four shapers.

Further constraints include CLAUDE.md lazy loading, deferred tool schemas (loading full schemas only on demand when `ToolSearch` is enabled), subagent summary-only returns, and per-tool-result budgets.

### The Query Pipeline and Execution Loop
Each turn of the query pipeline in `query.ts` follows a fixed sequence:
1. **Settings resolution:** Destructuring immutable parameters (system prompt, user context, permission callback, model configuration).
2. **Mutable state initialization:** A single `State` object stores messages, tool context, and recovery counters; the loop's seven "continue sites" overwrite this object via whole-object assignment.
3. **Context assembly:** `getMessagesAfterCompactBoundary()` retrieves messages from the last boundary forward.
4. **Pre-model context shapers:** Execution of the five sequential shapers listed above.
5. **Model call:** A `for await` loop over `deps.callModel()` streams the response. The call includes thinking configuration, available tool set, and model specifications (fast-mode, effort, fallback model).
6. **Tool-use dispatch:** `tool_use` blocks flow to the orchestration layer.
7. **Permission gate:** Requests pass through the permission system.
8. **Tool execution and result collection:** Results are added as `tool_result` messages, and the loop continues.
9. **Stop condition:** The turn ends if the response is text-only, or if max turns, context overflow (`prompt_too_long`), or explicit abort signals are reached. Other stop conditions include hook intervention (`hook_stopped_continuation`) and the `maxTurns` limit.

For tool execution, the system chooses between the `StreamingToolExecutor` (`StreamingToolExecutor.ts`) for low-latency streaming and `runTools()` in `toolOrchestration.ts` as a fallback. Both classify tools as concurrent-safe (read-only) or exclusive (state-modifying). `StreamingToolExecutor` manages concurrency using a sibling abort controller to terminate in-flight subprocesses if any Bash tool errors, and a progress-available signal for the `getRemainingResults()` consumer. Results are buffered and emitted in the order they were requested.

Recovery mechanisms include retrying max output token hits up to three times (`MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3`), reactive compaction (`REACTIVE_COMPACT`) to free space once per turn, and handling `prompt_too_long` errors via context-collapse overflow recovery and reactive compaction before termination.

### Safety and Permission Architecture
Claude Code implements a safety-by-default principle through seven independent layers:
1. **Tool pre-filtering (`tools.ts`):** Blanket-denied tools are removed from the model's view during pool assembly.
2. **Deny-first rule evaluation (`permissions.ts`):** Deny rules always take precedence over allow rules, even if the allow rule is more specific.
3. **Permission mode constraints (`types/permissions.ts`):** Determines baseline handling for requests matching no explicit rule.
4. **Auto-mode classifier (`yoloClassifier.ts`):** An ML-based classifier that evaluates requests against the conversation transcript and permission templates (selecting between external or internal templates based on `USER_TYPE` and `forceExternalPermissions`).
5. **Shell sandboxing (`shouldUseSandbox.ts`):** Approved Bash and PowerShell commands may execute in a sandbox that restricts filesystem and network access.
6. **Non-restoration of permissions on resume (`conversationRecovery.ts`):** Session-scoped permissions are not restored during resume or fork operations.
7. **Hook-based interception (`types/hooks.ts`):** `PreToolUse` hooks can modify parameters or return a `permissionDecision` (deny or ask). `PermissionRequest` hooks can resolve decisions asynchronously.

There are seven permission modes: `plan` (model must plan; user approves), `default` (standard interactive), `acceptEdits` (auto-approves edits and specific shell commands like `mkdir`, `rmdir`, `touch`, `rm`, `mv`, `cp`, `sed`), `auto` (ML-classifier gated by `TRANSCRIPT_CLASSIFIER`), `dontAsk` (no prompting, but deny rules enforced), `bypassPermissions` (skips most prompts, but safety-critical checks apply), and `bubble` (internal subagent escalation). The externally visible modes are `acceptEdits`, `bypassPermissions`, `default`, `dontAsk`, and `plan`.

### Tool Pool and Extensibility
The `assembleToolPool()` function in `tools.ts` creates a flat tool pool using a five-step pipeline: (1) base tool enumeration (up to 54 tools; 19 unconditional, 35 conditional), (2) mode filtering (e.g., `CLAUDE_CODE_SIMPLE` mode), (3) deny rule pre-filtering, (4) MCP tool integration (filtered by deny rules), and (5) deduplication (built-ins take precedence over MCP).

Extensibility is provided through four mechanisms:
1. **MCP Servers:** Integrated via `services/mcp/client.ts` using transports like stdio, SSE, HTTP, WebSocket, SDK, and IDE-specific variants. Provides access to `ListMcpResourcesTool` and `ReadMcpResourceTool`.
2. **Plugins:** Packaged via `PluginManifestSchema` (supporting commands, agents, skills, hooks, MCP servers, LSP servers, output styles, channels, settings, and user configuration). `pluginLoader.ts` validates these manifests.
3. **Skills:** Defined by `SKILL.md` files with YAML frontmatter (over 15 fields parsed by `loadSkillsDir.ts`). The `SkillTool` meta-tool injects skill instructions into the context.
4. **Hooks:** 27 hook events across six categories (tool authorization, session lifecycle, user interaction, subagent coordination, context management, and workspace events). Fifteen of these have Zod-validated output schemas. Persisted hooks use shell commands, LLM prompt hooks, HTTP hooks, or agentic verifier hooks.

### State and Persistence
Runtime state is managed in `src/state/`. Session transcripts are stored as append-only JSONL files in `sessionStorage.ts`. Global prompt history is maintained in `history.jsonl` via `history.ts`. `conversationRecovery.ts` handles session state reconstruction for resume and fork operations. Subagent sidechains in `sessionStorage.ts:247` store subagent conversations in separate files to prevent parent context inflation. The `getSystemContext()` and `getUserContext()` functions in `context.ts` are memoized state loaders.

### Backend Execution
The backend layer handles shell command execution via `BashTool.tsx` and `PowerShellTool.tsx` with optional sandboxing, remote execution in `src/remote/`, and MCP server connections via `services/mcp/client.ts` and the `claudeai-proxy`.

## Children
- [[content/L0/claude-code-execution-loop|claude-code-execution-loop]] — This chunk details the internal execution loop of Claude Code, including its seven-layer safety system, the five-layer context compaction pipeline (Budget reduction, Snip, Microcompact, Context collapse, and Auto-compact), and the detailed sequence of the `queryLoop()` function.
- [[content/L0/permission-and-extensibility-architecture|permission-and-extensibility-architecture]] — Claude Code implements a layered safety architecture combining deny-first policy enforcement and shell sandboxing, utilizing seven permission modes (e.g., plan, auto, acceptEdits) and a five-stage authorization pipeline. The system extends its action surface through four primary mechanisms: MCP servers, plugins, skills, and hooks, each managing different context costs.
- [[content/L0/extension-mechanisms-and-context-assembly|extension-mechanisms-and-context-assembly]] — Claude Code uses four extension mechanisms (MCP servers, plugins, skills, and hooks) with varying context costs, and assembles its tool pool via a five-step pipeline in `assembleToolPool()`. Context is constructed from nine sources, including a plain-text `CLAUDE.md` hierarchy and LLM-based memory scanning instead of embeddings.
