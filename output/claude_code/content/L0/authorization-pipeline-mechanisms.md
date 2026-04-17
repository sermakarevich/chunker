# authorization-pipeline-mechanisms

**Parent:** [[content/L1/agent-architecture-mechanisms|agent-architecture-mechanisms]] — The agent's highly layered architecture employs a 'deny-first' authorization pipeline, managed through three mechanisms (declarative rules, global trust modes, and hooks), and five permission modes (e.g., `plan`, `acceptEdits`, `auto`) to enforce safety; context assembly is non-static, starting with a four-level CLAUDE.md memory hierarchy and evolving during the turn through late injections; and extensibility is achieved via four core mechanisms (MCP servers, Plugins, Skills, Hooks) plus agent spawning, which collectively manage context state and tool reach through sophisticated meta-tools and a five-layer compaction process.

Other agent systems resolve the tension between autonomy and human control differently. SWE-Agent and OpenHands utilize Docker container isolation, sandboxing the agent’s entire execution environment rather than evaluating individual tool invocations. Aider relies on Git as a safety net, making all changes reversible through version control. Claude Code’s approach, conversely, layers multiple policy-enforcement mechanisms on top of optional container sandboxing, thereby trading simplicity for fine-grained control over individual actions. 

**The Authorization Pipeline**
The complete authorization pipeline proceeds through several stages: 

1. **Pre-filtering:** Before any tool request reaches runtime evaluation, the `filterToolsByDenyRules()` function in `tools.ts` strips blanket-denied tools from the model’s view entirely during tool pool assembly. The documentation clarifies that this mechanism uses the same matcher as the runtime permission check, meaning that Model Context Protocol (MCP) server-prefix rules, such as `mcp__server`, will strip all tools from that server before the model can see them. This prevents the model from attempting to invoke forbidden tools, thereby preventing the model from wasting calls on those tools.

2. **PreToolUse hook:** Registered hooks fire as part of the permission pipeline. A PreToolUse hook can perform three actions: return a `permissionDecision` (deny or ask), return a `permissionDecisionReason`, or provide an `updatedInput` that modifies the tool’s input parameters (defined in `types/hooks.ts`). A hook's allowance decision does not bypass subsequent rule-based denials or safety checks. In the interactive user path, the user dialog is queued first and the hooks run asynchronously; conversely, in coordinator and similar background-agent paths, the system waits for automated checks before displaying the user dialog.

3. **Rule evaluation:** The deny-first rule engine evaluates the request. MCP tools are matched by their fully qualified `mcp__server__tool` name, and server-level rules match all tools from that server.

4. **Permission handler:** The `canUseTool.tsx` handler branches into one of four paths based on the runtime context:
    * **Coordinator:** This mode handles multi-agent coordination, attempting automated resolution (classifier, hooks, rules) before falling back to user interaction.
    * **Swarm worker:** This mode handles worker agents participating in a multi-agent swarm, utilizing their own resolution logic.
    * **Speculative classifier:** When `BASH_CLASSIFIER` is enabled and the tool is a `BashTool`, a speculative classifier races a pre-started classification result against a timeout. If the classifier returns with high confidence, the system approves the tool instantly without requiring user interaction.
    * **Interactive:** This is the standard fallback path, which presents the user the standard approval dialog through the terminal UI.

In the coordinator and certain background paths, the system attempts automated resolution before requiring user interaction. In the standard interactive path, the user dialog can appear first while hooks or classifier checks continue running in parallel. When the classifier or a deny rule blocks an action, the system treats the denial as a routing signal rather than a hard stop: the model receives the denial reason, revises its approach, and attempts a safer alternative in the next loop iteration. The PermissionDenied hook event (detailed in Section 6) enables external code to observe and respond to these denials programmatically. This recovery-oriented design means that permission enforcement shapes the agent’s behavior rather than simply halting it.

**Auto-Mode Classifier and Hook Lifecycle**
The auto-mode classifier (found at `yoloClassifier.ts`) participates in permission decisions when enabled. When the `TRANSCRIPT_CLASSIFIER` feature flag is active, the classifier loads three prompt resources: a base system prompt, an external permissions template, and, for Anthropic-internal users, a separate internal template. The classifier evaluates the proposed tool invocation against the conversation transcript and the permission template, yielding an allow, deny, or request for manual approval. The function `isUsingExternalPermissions()` checks the `USER_TYPE` and a `forceExternalPermissions` configuration flag to select the appropriate template.

Of the 27 hook events defined in the source (`coreTypes.ts`), five participate directly in the permission flow, each with a specific Zod-validated output schema (`types/hooks.ts`): 
* **PreToolUse:** Can return a `permissionDecision` (deny or ask; note that `allow` does not bypass subsequent checks), a `permissionDecisionReason`, and `updatedInput` (which modifies parameters).
* **PostToolUse:** Can inject additional context and, for MCP tools, return `updatedMCPToolOutput` to modify results before they enter the context.
* **PostToolUseFailure:** Can inject additional context for error-specific guidance.
* **PermissionDenied:** Can provide retry guidance after auto-mode denials.
* **PermissionRequest:** Can return a decision of allow or deny. In coordinator and similar paths, this can resolve before the user dialog. In the standard interactive path, it can also run alongside the dialog.

For non-MCP tools, the `tool_result` is emitted before the PostToolUse hook fires. However, for MCP tools, the result is delayed until after the post hooks have run, allowing the `updatedMCPToolOutput` to take effect.

**Shell Sandboxing**
Shell sandboxing provides an additional protection layer for Bash and PowerShell commands (managed by `shouldUseSandbox.ts`).
The `shouldUseSandbox()` function checks three criteria: whether sandboxing is globally enabled, whether the invocation has opted out, and whether the command matches any exclusion patterns. When active, the sandbox provides filesystem and network isolation that operates independently of the application-level permission model. A command can be permission-approved but still sandboxed, or it can be permission-denied and never reach the sandbox check. The two systems operate on different axes: authorization versus isolation. The layered safety architecture assumes an independence of layers, meaning that if one layer fails, others will catch the violation. However, security researchers at Adversa.ai documented that commands with more than 50 subcommands fall back to a single generic approval prompt instead of running per-subcommand deny-rule checks, because per-subcommand parsing caused UI freezes. This specific example demonstrates that defense-in-depth can degrade when its layers share failure modes, illustrating a structural tension between safety and performance that is analyzed in Section 11.3.

**Extensibility: MCP, Plugins, Skills, and Hooks**

A recurring design question for coding agents involves how to structure the extension surface: whether to use a single unified mechanism, a small number of specialized mechanisms, or a layered stack with differing context costs. The analysis illustrates two design principles: composable multi-mechanism extensibility and externalized programmable policy. Returning to the running example of repairing `auth.test.ts` after the earlier `npm test` request was mediated by the permission system, the next question focuses on what extension-enabled action surface is available for the repair. When a turn begins in Claude Code, the model sees not only built-in tools like `BashTool` and `FileReadTool`, but also database query tools from an MCP server, a custom lint skill from the `.claude/skills/` directory, and tools contributed by an installed plugin. These tools arrive through four distinct mechanisms that extend the agent at different points of the loop:

1. **MCP servers:** The Model Context Protocol is the primary external tool integration path. MCP servers are configured across multiple scopes: project, user, local, and enterprise, with additional plugin and claude.ai servers merged at runtime (`services/mcp/config.ts`).
2. **Plugins:** Plugins package and distribute bundles of components.
3. **Skills:** Skills inject domain-specific instructions.
4. **Hooks:** Hooks intercept the tool execution lifecycle.

Anthropic’s documentation presents a broader view that includes `CLAUDE.md` (discussed in Section 7) and subagents (discussed in Section 8) alongside these four mechanisms. While the context-cost ordering of all mechanisms is architecturally significant, it reveals how each extension point trades off expressiveness against the bounded context window.
