# claude-code-execution-loop

**Parent:** [[content/L1/claude-code-architecture-deep-dive|claude-code-architecture-deep-dive]] — Claude Code utilizes a reactive ReAct loop (queryLoop) and a seven-layer safety system including deny-first rule evaluation and ML-based auto-mode classification. Context is managed via a five-layer compaction pipeline and a four-level CLAUDE.md hierarchy, while tools are assembled via a five-step pipeline and extended through MCP servers, plugins, and skills.

Claude Code's context assembly process is a memoized state loader rather than a routing hub. The `getSystemContext()` function in `context.ts` computes session-level system context, including git status, and the `getUserContext()` function in `context.ts` loads the current date and the CLAUDE.md hierarchy. Both are cached for reuse; the system context is appended to the system prompt, and the user context is added as a user-context message. The `src/state/` directory manages the runtime application state. Session transcripts are stored as mostly append-only JSONL files at project-specific paths, as handled by `sessionStorage.ts`. The CLAUDE.md and memory subsystem provides a four-level instruction hierarchy via `claudemd.ts` (ranging from managed settings to directory-specific files) and includes auto-memory entries that Claude writes during conversations. Sidechain transcripts, managed in `sessionStorage.ts:247`, store each subagent's conversation in a separate file to prevent subagent content from inflating the parent context. Global prompt history is maintained in `history.jsonl` via `history.ts`. Session state is reconstructed from transcripts for resume and fork operations using `conversationRecovery.ts`.

Claude Code's backend layer handles execution backends and external resources. This includes shell command execution with optional sandboxing via `BashTool.tsx` and `PowerShellTool.tsx`, remote execution support in `src/remote/`, and MCP server connections using various transport variants (stdio, SSE, HTTP, WebSocket, SDK, and IDE-specific adapters) via `services/mcp/client.ts`. Concrete tool logic is implemented in 42 tool subdirectories within `src/tools/`.

Regarding the `QueryEngine` class in `QueryEngine.ts`, the documentation states that it owns the query lifecycle and session state for a conversation, extracting core logic from `ask()` into a standalone class for use by the headless/SDK path and potentially a future REPL. Architecturally, `QueryEngine` is a conversation wrapper for non-interactive surfaces rather than the engine itself. Its constructor accepts a `QueryEngineConfig` containing initial messages, an abort controller, a file-state cache, and other per-conversation state. Its `submitMessage()` method is an async generator that orchestrates a single turn. The shared query path is the `query()` function in `query.ts`, which wraps an internal `queryLoop()`; `QueryEngine` delegates to `query()`.

This distinction is architecturally significant because the interactive CLI bypasses `QueryEngine` and calls `query()` directly. The shared code path is the loop function, not the `QueryEngine` class.

Claude Code implements a safety-by-default principle through seven independent layers. A request must pass all applicable layers, and any single layer can block it:
1. Tool pre-filtering (`tools.ts`): Blanket-denied tools are removed from the model's view before any call to prevent the model from attempting to invoke them.
2. Deny-first rule evaluation (`permissions.ts`): Deny rules always take precedence over allow rules, even when the allow rule is more specific.
3. Permission mode constraints (`types/permissions.ts`): The active mode determines baseline handling for requests matching no explicit rule.
4. Auto-mode classifier: An ML-based classifier evaluates tool safety and may deny requests that the rule system would allow.
5. Shell sandboxing (`shouldUseSandbox.ts`): Approved shell commands may execute inside a sandbox that restricts filesystem and network access.
6. Non-restoration of permissions on resume (`conversationRecovery.ts`): Session-scoped permissions are not restored during a resume or fork operation.
7. Hook-based interception (`types/hooks.ts`): PreToolUse hooks can modify permission decisions, and PermissionRequest hooks can resolve decisions asynchronously alongside or before the user dialog (in coordinator mode).

To address the context-as-bottleneck constraint, Claude Code employs several subsystem decisions beyond its five-layer compaction pipeline:
- CLAUDE.md lazy loading: The base CLAUDE.md hierarchy is loaded at session start, but nested-directory instruction files and conditional rules are loaded only when the agent reads files in those directories.
- Deferred tool schemas: When ToolSearch is enabled, some tools include only their names in the initial context; full schemas are loaded on demand.
- Subagent summary-only return: Subagents return only summary text to the parent agent, not their full conversation history.
- Per-tool-result budget: Individual tool results are capped at a configurable size to prevent a single verbose output from consuming disproportionate context.

When a user submits a request, such as "Fix the failing test in auth.test.ts," the input enters a reactive loop. Claude Code uses a simple while-loop architecture, illustrating design principles of minimal scaffolding with maximal operational harness, context as a scarce resource with progressive management, and graceful recovery and resilience.

Each turn of the query pipeline follows a fixed sequence in `query.ts`:
1. Settings resolution: The `queryLoop()` function destructures immutable parameters including the system prompt, user context, permission callback, and model configuration.
2. Mutable state initialization: A single `State` object stores all mutable state across iterations, including messages, tool context, compaction tracking, and recovery counters. The loop's seven "continue sites" overwrite this object via whole-object assignment rather than mutating fields individually.
3. Context assembly: The `getMessagesAfterCompactBoundary()` function retrieves messages from the last compact boundary forward, ensuring compacted content is represented by its summary.
4. Pre-model context shapers: Five sequential shapers execute (budget reduction, snip, microcompact, context collapse, and auto-compact).
5. Model call: A `for await` loop over `deps.callModel()` streams the model's response. The call passes the assembled messages (with user context prepended), the full system prompt, thinking configuration, the available tool set, an tool abort signal, and model specification, including fast-mode settings, effort value, and fallback model.
6. Tool-use dispatch: If the response contains `tool_use` blocks, they flow to the tool orchestration layer.
7. Permission gate: Each tool request passes through the permission system.
8. Tool execution and result collection: Tool results are added as `tool_result` messages, and the loop continues.
9. Stop condition: The turn is complete if the response contains only text and no `tool_use` blocks.

The `queryLoop()` function is an `AsyncGenerator` that yields `StreamEvent`, `RequestStartEvent`, `Message`, `TombstoneMessage`, and `ToolUseSummaryMessage` events. This design allows streaming output to the UI while maintaining a synchronous control flow within the loop. The reactive loop follows the ReAct pattern, where the model generates reasoning and tool invocations, the harness executes actions, and results feed the next iteration. This differs from explicit graph-based routing (e.g., LangChain) or tree-search methods. While Anthropic identifies five composable workflow patterns (prompt chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer), Claude Code primarily uses the orchestrator-workers pattern for subagent delegation while keeping the core loop reactive. The reactive design trades search completeness for simplicity and latency.

For tool dispatch and streaming execution, the system chooses between two paths. The primary path is the `StreamingToolExecutor` (`StreamingToolExecutor.ts`), which executes tools as they stream from the model response to reduce latency. The fallback path is `runTools()` in `toolOrchestration.ts`, which iterates over partitions produced by `partitionToolCalls()`. Both paths classify tools as concurrent-safe (read-only operations that can run in parallel) or exclusive (state-modifying operations like shell commands that must be serialized). 

`StreamingToolExecutor` manages concurrency with two mechanisms: a sibling abort controller that terminates other in-flight subprocesses if any Bash tool errors, and a progress-available signal that wakes up the `getRemainingResults()` consumer when new output is ready. Results are buffered and emitted in the order tools were received to ensure the model receives results in the same order as its requests. This concurrent-read, serial-write model is a middle ground between fully serial dispatch and speculative approaches like PASTE.

Tool result collection iterates over updates from the streaming executor or the `runTools()` generator. A check for `hook_stopped_continuation` attachments from PostToolUse hooks can set a `shouldPreventContinuation` flag. Results are normalized for the Anthropic API via `normalizeMessagesForAPI()`, filtering to keep only user-type messages.

Five pre-model context shapers execute sequentially in `query.ts` before every model call on the `messagesForQuery` array:
1. Budget reduction (`applyToolResultBudget()`): Enforces per-message size limits on tool results, replacing oversized outputs with content references. Exempt tools (where `maxResultSizeChars` is not finite) are retained in full. Content replacements are persisted for agent and session query sources to allow reconstruction on resume. This runs before microcompact because microcompact does not inspect content.
2. Snip (`snipCompactIfNeeded()`, gated by `HISTORY_SNIP`): A lightweight trim that removes older history segments. It returns `tokensFreed` tokens, which are passed to auto-compact because the token counter (derived from the `usage` field on the most recent assistant message) doesn't see the snipped tokens as savings.
3. Microcompact: Performs fine-grained compression. It always runs a time-based path and optionally a cache-aware path (gated by `CACHED_MICROCOMPACT`). If enabled, boundary messages are deferred until after the API response to use actual `cache_deleted_input_tokens` rather than estimates. Returns `compactionInfo` which may include `pendingCacheEdits`.
4. Context collapse (gated by `CONTEXT_COLLAPSE`): A read-time projection over conversation history. Summary messages live in a collapse store, and `applyCollapsesIfNeeded()` replaces the `messagesForQuery` array with a projected view. The model sees the collapsed version, but the full history remains available for reconstruction.
5. Auto-compact: Triggers a full model-generated summary via `compactConversation()` in `compact.ts`. This uses `PreCompact` hooks, `getCompactPrompt()`, and a model call to produce a compressed summary, which feeds into `buildPostCompactMessages()`. This only fires if the context still exceeds the pressure threshold after the four previous shapers have run.

Claude Code implements several recovery mechanisms for edge cases:
- Max output tokens escalation: If a response hits the output token cap, the system can retry up to three times (`MAX_OUTPUT_TOKENS_RECOVERY_LIMIT = 3`), subject to a `GrowthBook` flag and environment-variable caps.
- Reactive compaction (gated by `REACTIVE_COMPACT`): If context is near capacity, `hasAttemptedReactiveCompact` ensures this runs at most once per turn to summarize just enough to free space.
- Prompt-too-long handling: If the API returns a `prompt_too_long` error, the loop first attempts context-collapse overflow recovery and reactive compaction. If these fail, it terminates with the reason `prompt_too_long`.
- Streaming fallback: The `onStreamingFallback` callback handles streaming API issues, the loop can retry with a different strategy.

- Fallback model: The `fallbackModel` parameter allows switching to an alternative model if the primary model fails.

Finally, the loop terminates based on several stop conditions:
1. No tool use: The model produces only text content.
2. Max turns: The configurable `maxTurns` limit is reached.
3. Context overflow: The kalimat `prompt_too_long` is returned by the API.
4. Hook intervention: Aer own PostToolUse hook sets `hook_stopped_continuation`.
5. Explicit abort: The `abortController` signal fires.

The turn pipeline determines how tool requests are orchestrated and recovered, which then leads to the permission system that determines if a request is permitted to execute.


