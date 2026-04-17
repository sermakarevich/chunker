# typescript-package-structure-and-dependencies

**Parent:** [[index]]

The Claude Code agent system is architected with multiple specialized subsystems built into a single TypeScript package, which dictates its runtime behavior. The overall code structure is organized under a `src/` directory and comprises key files and directories that govern specific functionalities and dependencies.

### Directory-to-Responsibility Map

The primary subsystem files and directories, listed in Table 7, include:

*   **`main.tsx`**: Serves as the entry point, managing mode dispatch and initial setup.
*   **`query.ts`** and **`query/`**: `query.ts` contains the core agent loop (`queryLoop` AsyncGenerator), while the `query/` directory houses helper modules for loop configuration and context assembly.
*   **`QueryEngine.ts`**: Functions as a conversation wrapper for headless or SDK use, delegating turn execution to `query.ts`.
*   **`Tool.ts`** and **`history.ts`**: Define the tool interface, types, and utilities, respectively.
*   **`mcp/client.ts`**: Functions as the Mechanical Composition Protocol (MCP) client, supporting over 8 transport variants.
*   **`compact.ts`**: Acts as the compaction engine.
*   **`AgentTool.tsx`** and **`runAgent.ts`**: Manage agent tool invocation and the 21-parameter agent lifecycle.

Within the `tools/` directory, approximately 42 subdirectories implement concrete tools, each containing corresponding schemas, descriptions, permission requirements, and execution logic. The `commands/` directory contains approximately 86 slash command subdirectories.

Other key service directories include `services/tools/` (for `StreamingToolExecutor`, `toolOrchestration`, and `toolExecution`), `services/compact/` (housing the compaction engine), and `services/mcp/` (managing the MCP client and configuration).

The permission infrastructure is spread across: `utils/permissions/` (for rule evaluation and the `yoloClassifier` auto-mode), `hooks/useCanUseTool.tsx` (the permission handler), `types/permissions.ts` (for mode definitions), and `types/hooks.ts` (for event schemas).

Structurally, the codebase has a quirk where `query.ts` is a file containing the main query loop, while the sibling directory `query/` houses helper modules for loop configuration and context assembly.

### Conditional Tool Availability

The `getAllBaseTools()` function within `tools.ts` builds the tool set available to the model by constructing different sets depending on the runtime mode, build environment, and activated feature flags. The number of available tools can range from a minimum of 3 tools in simple mode (specifically the Bash, Read, and Edit tools) up to 40+ tools when running a full internal build with all features enabled. The table below details the categories influencing tool availability:

| Category | Examples | 
| :--- | :--- |
| **Always included** | `AgentTool`, `BashTool`, `FileReadTool`, `FileEditTool`, `FileWriteTool`, `SkillTool`, `WebFetchTool`, `WebSearchTool` | 
| **Environment** | `GlobTool`/`GrepTool` (unless embedded), `ConfigTool` (for `ant-only`), `PowerShellTool` (for Windows) | 
| **Feature flag** | `TaskCreate`/`Get/Update/List` (for `todoV2`), `EnterWorktreeTool` (for `worktree`), `TeamTools` (for swarms), `ToolSearchTool` | 
| **Null-checked** | `SuggestBackgroundPRTool`, `WebBrowserTool`, `RemoteTriggerTool`, `MonitorTool`, `SleepTool` | 

### Cross-File Dependencies

The import graph reveals specific dependencies: `QueryEngine.ts` delegates turn execution to `query.ts`. `query.ts` imports functionality from `services/tools/` (for `StreamingToolExecutor` and `runTools`) and `services/compact/` (for `autoCompact` and `buildPostCompactMessages`). Furthermore, `QueryEngine.ts` imports resources for memory and prompt assembly from `memdir/`. The code explicitly prevents circular imports by extracting `types/permissions.ts` and by implementing `setCachedClaudeMdContent()` in `context.ts` to avoid a cycle involving the `permissions/` filesystem path.
