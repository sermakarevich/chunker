# permission-and-extensibility-architecture

**Parent:** [[content/L1/claude-code-architecture-deep-dive|claude-code-architecture-deep-dive]] — Claude Code utilizes a reactive ReAct loop (queryLoop) and a seven-layer safety system including deny-first rule evaluation and ML-based auto-mode classification. Context is managed via a five-layer compaction pipeline and a four-level CLAUDE.md hierarchy, while tools are assembled via a five-step pipeline and extended through MCP servers, plugins, and skills.

Production coding agents generally adopt safety architectures based on layered policy enforcement, OS-level sandboxing, or version-control-based rollback. Claude Code combines layered policy enforcement and OS-level sandboxing, implementing four specific design principles: deny-first with human escalation, graduated trust spectrum, defense in depth with layered mechanisms, and reversibility-weighted risk assessment.

When Claude Code decides to execute a tool—for example, using BashTool to run `npm test` to reproduce a failure in `auth.test.ts`—the request enters a permission pipeline. Every tool invocation passes through this system, where the default behavior is to deny or ask rather than allow silently. This design is motivated by Anthropic’s auto-mode analysis (Hughes, 2026), which found that users approve approximately 93% of permission prompts, suggesting that approval fatigue makes interactive confirmation behaviorally unreliable as a sole safety mechanism. Consequently, Claude Code maintains safety through independent layers: deny-first evaluation, blanket-deny pre-filtering, and sandboxing, which operate regardless of user attentiveness.

### Permission Modes and Rule Evaluation
Claude Code defines seven permission modes across its type definitions (five external modes in `types/permissions.ts`, an auto mode added conditionally, and a bubble mode in the type union):
1. **plan**: The model must create a plan; execution proceeds only after user approval.
2. **default**: Standard interactive use where most operations require user approval.
3. **acceptEdits**: Edits within the working directory and specific filesystem shell commands (`mkdir`, `rmdir`, `touch`, `rm`, `mv`, `cp`, `sed`) are auto-approved; other shell commands require approval.
4. **auto**: An ML-based classifier evaluates requests that do not pass fast-path checks, gated by the `TRANSCRIPT_CLASSIFIER` feature flag.
5. **dontAsk**: No prompting occurs, but deny rules are still enforced.
6. **bypassPermissions**: Skips most permission prompts, but safety-critical checks and bypass-immune rules still apply.
7. **bubble**: An internal-only mode used for subagent permission escalation to the parent terminal.

The five externally visible modes (`acceptEdits`, `bypassPermissions`, `default`, `dontAsk`, `plan`) are listed in the `EXTERNAL_PERMISSION_MODES` array. The `auto` mode is included only when the `TRANSCRIPT_CLASSIFIER` flag is active. The `bubble` mode exists in the type union but not in the mode arrays.

Permission rules are evaluated in `permissions.ts` using a deny-first order. The `toolMatchesRule()` function ensures a deny rule always takes precedence over an allow rule, even if the allow rule is more specific (e.g., a broad "deny all shell commands" cannot be overridden by a narrow "allow `npm test`"). The system supports tool-level matching by tool name and content-level matching for specific input patterns, such as `Bash(prefix:npm)`.

These seven modes create a graduated autonomy spectrum from `plan` (maximum user control) to `bypassPermissions` (minimal prompting). While other systems like SWE-Agent and OpenHands use Docker container isolation to sandbox the entire environment, and Aider relies on Git for reversibility, Claude Code layers multiple policy-enforcement mechanisms on top of optional container sandboxing for fine-grained control over individual actions.

### The Authorization Pipeline
The full authorization pipeline consists of several stages:
1. **Pre-filtering**: Before runtime evaluation, `filterToolsByDenyRules()` in `tools.ts` removes blanket-denied tools from the model's view during tool pool assembly. This prevents the model from attempting to invoke forbidden tools (e.g., MCP server-prefix rules like `mcp__server` strip all tools from that server). 
2. **PreToolUse hook**: Registered hooks in `types/hooks.ts` fire during the permission pipeline. A `PreToolUse` hook can return a `permissionDecision` (deny or ask) or an `updatedInput` to modify tool parameters. A hook's "allow" decision does not bypass subsequent rule-based denies or safety checks. In interactive paths, the user dialog is queued first and hooks run asynchronously; in coordinator or background-agent paths, automated checks are awaited before the dialog is shown.
3. **Rule evaluation**: The deny-first rule engine evaluates the request. MCP tools are matched by their fully qualified `mcp__server__tool` name, and server-level rules apply to all tools from that server.
4. **Permission handler**: The handler in `useCanUseTool.tsx` branches into four paths based on runtime context:
    - **Coordinator**: For multi-agent coordination mode; attempts automated resolution via classifier, hooks, and rules before falling back to user interaction.
    - **Swarm worker**: Handles worker agents in a multi-agent swarm using their own resolution logic.
    - **Speculative classifier**: When `BASH_CLASSIFIER` is enabled and the tool is `BashTool`, a speculative classifier races a pre-started classification result against a timeout; if high confidence is returned, the tool is approved instantly.
    - **Interactive**: The fallback path that presents the standard user approval dialog through the terminal UI.

If a classifier or deny rule blocks an action, the system treats the denial as a routing signal: the model receives the reason for the denial, revises its approach, and attempts a safer alternative in the next loop iteration. This recovery-oriented design is supported by the `PermissionDenied` hook event, allowing external code to respond programmatically.

### Auto-Mode Classifier and Hook Lifecycle
The auto-mode classifier (`yoloClassifier.ts`) participates in decisions when `TRANSCRIPT_CLASSIFIER` is enabled. It loads a base system prompt, an external permissions template, and, for Anthropic-internal users, a separate internal template. The classifier evaluates the tool invocation against the conversation transcript and the permission template. The `function isUsingExternalPermissions()` checks the `USER_TYPE` and `forceExternalPermissions` config flag to select the template.

Of the 27 hook events defined in `coreTypes.ts`, five directly participate in the permission flow via Zod-validated output schemas in `types/hooks.ts`:
- **PreToolUse**: Returns `permissionDecision` (deny or ask), `permissionDecisionReason`, and `updatedInput`.
- **PostToolUse**: Injects `additionalContext` and can return `updatedMCPToolOutput` for MCP tools to modify results before they enter context.
- **PostToolUseFailure**: Injects `additionalContext` for error-specific guidance.
- **PermissionDenied**: Provides retry guidance after auto-mode denials.
- **PermissionRequest**: Returns a decision of `allow` or `deny`. In coordinator paths, this can resolve before the user dialog; in interactive paths, it runs alongside the dialog.

For non-MCP tools, `tool_result` is emitted before the `PostToolUse` hook fires. For MCP tools, the result is delayed until the hooks run, allowing `updatedMCPToolOutput` to take effect.

### Shell Sandboxing
Shell sandboxing (`shouldUseSandbox.ts`) provides protection for Bash and PowerShell commands. The `shouldUseSandbox()` function checks if sandboxing is globally enabled, if the invocation opted out, and if the command matches exclusion patterns.

Sandboxing provides filesystem and network isolation independent of the application-level permission model. A command may be permission-approved but still sandboxed, or permission-denied and never reach the sandbox check. This layered architecture assumes that if one layer fails, others will catch the violation. However, security researchers from Adversa.ai (2026) noted a performance constraint: commands with more than 50 subcommands fall back to a single generic approval prompt instead of per-subcommand deny-rule checks to prevent UI freezes.

### Extensibility Architecture
Claude Code uses a composable multi-mechanism extensibility model and an externalized programmable policy to manage its action surface. When a turn begins, the model sees a flat tool pool comprising built-in tools (e.g., `BashTool`, `FileReadTool`), tools from MCP servers, custom lint skills from `.claude/skills/`, and tools from installed plugins. These four mechanisms extend the agent at different points of the loop:
1. **MCP servers**: Provide external tool integration via Model Context Protocol. MCP servers are configured from project, user, local, and enterprise scopes, merged at runtime via `services/mcp/config.ts`. The MCP client in `services/mcp/client.ts` supports transports like stdio, SSE, HTTP, WebSocket, SDK, and IDE-specific variants (`sse-ide`, `ws-ide`).
2. **Plugins**: Package and distribute bundles of components.
3. **Skills**: Inject domain-specific instructions via the `SkillTool` meta-tool.
4. **Hooks**: Intercept the tool execution lifecycle. 

While `CLAUDE.md` and subagents also extend the agent's capabilities, they are managed in separate subsystems for context construction and delegation, respectively. The architectural significance of these mechanisms is that they each trade off expressiveness against the bounded context window.
