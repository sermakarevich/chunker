# agent-architecture-and-extensibility-pipeline

**Parent:** [[content/L1/agent-architecture-mechanisms|agent-architecture-mechanisms]] — The agent's highly layered architecture employs a 'deny-first' authorization pipeline, managed through three mechanisms (declarative rules, global trust modes, and hooks), and five permission modes (e.g., `plan`, `acceptEdits`, `auto`) to enforce safety; context assembly is non-static, starting with a four-level CLAUDE.md memory hierarchy and evolving during the turn through late injections; and extensibility is achieved via four core mechanisms (MCP servers, Plugins, Skills, Hooks) plus agent spawning, which collectively manage context state and tool reach through sophisticated meta-tools and a five-layer compaction process.

The Mechanical Composition Protocol (MCP) client, located at `services/mcp/client.ts`, supports multiple transport types: stdio, SSE, HTTP, WebSocket, SDK, and IDE-specific variants, including `sse-ide` and `ws-ide`. During one turn of the Claude Code agent loop, the system follows these steps:

**a) Assemble Context (What the Model Sees):** The context is built using a function called `assemble()` which incorporates the following elements for the model:

*   **CLAUDE.md files:** These files are loaded into the context; files above the working directory load at startup, and subdirectory files load on demand.
*   **Skill descriptions:** These advertise skills, enabling the model to call a `SkillTool`.
*   **MCP resources & prompts:** Non-tool content that an MCP server pushes into the context.
*   **Output style:** This feature replaces the response formatting system block.
*   **UserPromptSubmit hook:** This hook can inject context or block a turn whenever a user submits a prompt.
*   **SessionStart hook:** This hook is used for one-shot context injection at the beginning of a session.

**b) Model Action (What the Model Can Reach):** The model selects its next action using the `model()` function based on the following available elements:

*   **Built-in tools:** Tools such as Read, Edit, Bash, and others shipped with the CLI.
*   **MCP tools:** Tools sourced from any connected MCP server, all merged into the same flat tool pool.
*   **SkillTool:** A meta-tool designed to launch a skill by its name.
*   **AgentTool:** A meta-tool designed to recursively spawn a sub-agent.

**c) Execute Action (Whether/How an Action Runs):** The system determines whether and how the action executes through the `execute()` function, implementing several layers of control:

*   **Permission rules:** These govern declarative allow, deny, or ask decisions for every call.
*   **PreToolUse hook:** This hook can approve, block, or rewrite a tool call.
*   **PostToolUse hook:** This hook can mutate the output or inject additional context after a tool call.
*   **Stop hook:** This hook can force the loop to continue even if the model suggests stopping.
*   **SubagentStop hook:** This hook performs the same function but is specific to sub-agents spawned via `AgentTool`.
*   **Notification hook:** This hook enables external side effects on user notifications.

Figure 5 illustrates where Claude Code's extension mechanisms plug into the agent loop. The pseudocode provided for the Agent Loop highlights three critical injection points: `assemble()` controls what the model sees, `model()` controls what the model can reach, and `execute()` controls whether and how an action actually runs. This architecture is complemented by several extensions: 

**Plugins:** Plugins function both as a packaging format and a distribution mechanism. The `PluginManifestSchema` (found in `utils/plugins/schemas.ts`) accepts ten component types: commands, agents, skills, hooks, MCP servers, LSP servers, output styles, channels, settings, and user configuration. The `pluginLoader` (in `utils/plugins/pluginLoader.ts`) validates manifests and routes each component to its dedicated registry: commands and skills use the `SkillTool` meta-tool, agents are consumed by `AgentTool`, hooks merge into the hook registry, MCP and LSP servers are added to their standard configurations, and output styles modify response formatting. A single plugin package can extend Claude Code across multiple component types simultaneously, making plugins the primary distribution vehicle for third-party extensions.

**Skills:** Every skill is defined by a `SKILL.md` file containing YAML frontmatter. The `parseSkillFrontmatterFields()` function (in `loadSkillsDir.ts`) analyzes over 15 fields, which include display name, description, allowed tools (granting the skill access to additional tools), argument hints, model overrides, execution context (specifying 'fork' for isolated execution), associated agent definitions, effort levels, and shell configuration. Skills can also define their own hooks, which register dynamically when the skill is invoked. When the system invokes a skill, the `SkillTool` meta-tool injects the skill’s instructions into the context.

**Hooks:** The source code defines 27 distinct hook events, which cover tools authorization (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied), session lifecycle (SessionStart, SessionEnd, Setup, Stop, StopFailure), user interaction (UserPromptSubmit, Elicitation, ElicitationResult), subagent coordination (SubagentStart, SubagentStop, TeammateIdle, TaskCreated, TaskCompleted), context management (PreCompact, PostCompact, InstructionsLoaded, ConfigChange), workspace events (CwdChanged, FileChanged, WorktreeCreate, WorktreeRemove), and notifications (documented in `coreTypes.ts` and `coreSchemas.ts`). Of these 27 events, 15 have specific output schemas detailed in `types/hooks.ts`. These rich fields support rich capabilities such as permission decisions, context injection, input modification, MCP result transformation, and retry control. Users configure persistent hook commands through settings and plugins using four command types: shell commands (`type: command`), LLM prompt hooks (`type: prompt`), HTTP hooks (`type: http`), and agentic verifier hooks (`type: agent`) (defined in `schemas/hooks.ts`). Additionally, the runtime supports non-persistable callback hooks (`type: callback`) used by the SDK and internal instrumentation (documented in `types/hooks.ts`). Hook sources include `settings.json`, plugins, and managed policy at startup; skill hooks register dynamically when the skill is invoked (documented in `utils/hooks.ts`).

**Tool Pool Assembly:** The `assembleToolPool()` function in `tools.ts` serves as the single source of truth for combining built-in tools and MCP tools. The assembly proceeds through five steps:

1. **Base tool enumeration:** The `getAllBaseTools()` function (in `tools.ts`) returns an array containing up to 54 tools. These tools include 19 tools that are always included (such as BashTool, FileReadTool, AgentTool, SkillTool), and 35 tools that are conditionally included based on feature flags, environment variables, and user type. Anthropic-internal users receive additional internal tools. If the system operates in worktree mode, it includes `EnterWorktreeTool` and `ExitWorktreeTool`. If agent swarms are enabled, the system includes team tools. The dedicated `GlobTool` and `GrepTool` are omitted if embedded search tools are available in the Bun binary.
2. **Mode filtering:** The `getTools()` function (in `tools.ts`) applies mode-specific filtering. For example, in `CLAUDE_CODE_SIMPLE` mode, only Bash, Read, and Edit tools are available (or REPLTool if running in the REPL branch, plus coordinator tools if applicable). Each tool’s `isEnabled()` method is called for runtime availability checks.
3. **Deny rule pre-filtering:** The `filterToolsByDenyRules()` function (in `tools.ts`) strips blanket-denied tools from the model’s view before any tool invocation.
4. **MCP tool integration:** MCP tools from `appState.mcp.tools` are filtered by deny rules and subsequently merged with the built-in tools.
5. **Deduplication:** Tools are deduplicated by name, with built-in tools always taking precedence over MCP tools. Both the `REPL.tsx` and `AgentTool.tsx` components invoke this function, ensuring consistent assembly across all execution paths. At request time, deferred tools may be hidden from the model’s context until the model explicitly queries them using `ToolSearch` (in `tools.ts`).

Agent-based extensions (custom agent definitions, such as those defined via `.claude/agents/*.md` and plugin-contributed agents) are treated separately, as they fundamentally differ from the four mechanisms listed above because they create new, isolated context windows rather than extending the existing one.
