# claude-code-source-structure-methodology

**Parent:** [[index]]

This analysis details the source code structure and evidence methodology for Claude Code (version 2.1.88), an agentic coding tool by Anthropic. 

### Source Code Structure and Runtime Responsibility
Claude Code's codebase is organized into several key files and directories, each with specific runtime responsibilities:
- **main.tsx (804KB)**: Serves as the entry point, handling mode dispatch and setup.
- **query.ts (68KB)**: Contains the core agent loop and the five context shapers.
- **QueryEngine.ts (47KB)**: Acts as a conversation wrapper for SDK and headless modes, delegating turn execution to `query.ts`.
- **Tool.ts (30KB)**: Defines the tool interface, types, and utilities.
- **history.ts (14KB)**: Manages global prompt history.
- **mcp/client.ts (Large)**: Implements the Model Context Protocol (MCP) client, supporting eight or more transport variants.
- **compact.ts (Large)**: Houses the compaction engine.
- **AgentTool.tsx (Large)**: Manages the agent tool and subagent dispatch.
- **runAgent.ts (Large)**: Governs the 21-parameter agent lifecycle.

Further organizational details include:
- **tools/ directory**: Contains approximately 42 subdirectories, each implementing a tool with its own schema, description, permission requirements, and execution logic.
- **commands/ directory**: Contains approximately 86 slash command subdirectories.
- **Key service directories**: `services/tools/` (responsible for `StreamingToolExecutor`, tool orchestration, and tool execution), `services/compact/` (the compaction engine), and `services/mcp/` (the MCP client and configuration).
- **Permission infrastructure**: Distributed across `utils/permissions/` (rule evaluation and the `yoloClassifier`), `hooks/useCanUseTool.tsx` (the permission handler), `types/permissions.ts` (permission mode definitions), and `types/hooks.ts` (event schemas).
- **Structural Quirk**: `query.ts` (a file) and `query/` (a directory) coexist; the file contains the main query loop, while the directory contains helper modules for loop configuration and context assembly.

### Tool Availability and Dependencies
The `getAllBaseTools()` function in `tools.ts` determines tool availability based on mode, build, environment, and feature flags. In simple mode, the model may see as few as 3 tools (Bash, Read, Edit), whereas a full internal build with all features enabled may provide 40+ tools. Tools are categorized as follows:
- **Always included**: `AgentTool`, `BashTool`, `FileReadTool`, `FileEditTool`, `FileWriteTool`, `SkillTool`, `WebFetchTool`, and `WebSearchTool`.
- **Environment-specific**: `GlobTool`/`GrepTool` (unless embedded), `ConfigTool` (Ant-only), and `PowerShellTool` (Windows).
- **Feature flag-gated**: `TaskCreate`/`Get`/`Update`/`List` (todoV2), `EnterWorktreeTool` (worktree), `TeamTools` (swarms), and `ToolSearchTool`.
- **Null-checked**: `SuggestBackgroundPRTool`, `WebBrowserTool`, `RemoteTriggerTool`, `MonitorTool`, and `SleepTool`.

Regarding cross-file dependencies, `QueryEngine.ts` delegates to `query.ts`. `query.ts` imports from `services/tools/` (specifically `StreamingToolExecutor` and `runTools`) and `services/compact/` (specifically `autoCompact` and `buildPostCompactMessages`). `QueryEngine.ts` imports from `memdir/` for memory and prompt assembly. To prevent circular imports, `types/permissions.ts` was extracted as a separate file, and the `setCachedClaudeMdContent()` function in `context.ts` avoids cycles between the permissions and filesystem paths.

### Evidence Base and Methodology
The study's claims are grounded in three evidence tiers:
- **Tier A (Product-documented)**: Claims from official Anthropic documentation and engineering publications (establishes intent).
- **Tier B (Code-verified)**: Claims citing specific files and functions in the TypeScript codebase v2.1.88, extracted from a public npm package (strongest evidence).
- **Tier C (Reconstructed)**: Claims derived from community analysis, structural comparison with OpenClaw, or inference from code patterns (stated with hedging language).

The source corpus consists of approximately 1,884 files and roughly 512K lines of TypeScript. OpenClaw is used for calibration rather than ground truth.

### Design-Space Analytic Procedure and Limitations
Design questions were identified by comparing subsystems against alternative designs in other production agents. Claude Code's answers were traced through source files and function implementations (Tier B). The five-value framework (human decision authority, safety, security and privacy, reliable execution, capability amplification, and contextual adaptability) was derived from official documentation (Tier A) and mapped to thirteen design principles. Long-term capability preservation is used as an evaluative lens rather than a design value. Token economics is treated as a cross-cutting constraint bounding all five values.

Limitations of the analysis include:
- **Static snapshot**: The analysis is limited to version 2.1.88. Build-time variability caused by feature flags (e.g., `TRANSCRIPT_CLASSIFIER`, `CONTEXT_COLLAPSE`) means different builds may be functionally different.
- **Reverse-engineering epistemology**: The source code reveals structure and control flow but cannot confirm design intent, runtime prevalence, or enabled production flags.
- **Single-system analysis**: Findings are bounded to Claude Code's design space.
- **OpenClaw snapshot**: The comparison reflects a specific state of OpenClaw and may not be current.

### Comprehensive Source Structure (v2.1.88)
- **Entry & Startup**: `main.tsx` (entry point), `replLauncher.tsx` (interactive REPL), `entrypoints/` (SDK/headless startup), and `cli/` (argument handlers).
- **UI Layer**: `components/` and `screens/` (ink framework terminal UI), and `outputStyles/` (system-prompt output style logic).
- **UI Layer**: `components/` and `screens/` (ink framework terminal UI), and `outputStyles/` (system-prompt output style logic).
- **Core Loop**: `query.ts` (queryLoop AsyncGenerator and 5 shapers), `query/` (loop config helpers), `QueryEngine.ts` (headless/SDK wrapper), and `context.ts` (context assembly).
- **Tools & Commands**: `Tool.ts` (interface/types), `tools/` (42 concrete tools), `services/tools/` (execution/orchestration), and `commands/` (86 slash commands).
- **Safety & Permissions**: `utils/permissions/` (rule evaluation and `yoloClassifier`), `types/permissions.ts` (7 permission modes), `hooks/useCanUseTool.tsx` (permission handler), and `components/permissions/` (UI dialogs).
- **Extensibility**: `plugins/` (loader/manifests), `skills/` (loader/SKILL.md parsing), `utils/hooks.ts` (registry/dispatch), and `types/hooks.ts` (Zod schemas).
- **Context & Memory**: `services/compact/` (5-layer compaction), `memdir/` (auto memory), `utils/claudemd.ts` (CLAUDE.md hierarchy), and `state/` (runtime state).
- **Context & Memory**: `services/compact/` (L5 compaction), `utils/claudemd.ts` (CLAUDE.md hierarchy), and `state/` (runtime state).
- **Persistence**: `history.ts` (global prompt history) and `utils/sessionStorage.ts` (JSONL transcripts and sidechains).
- **Services & Integration**: `services/` (MCP client, API adapters, LSP), `remote/` (remote execution), and `coordinator/` (multi-agent coordination).
- **Additional Infrastructure**: `bootstrap/`, `bridge/`, `constants/`, `server/`, `ink/`, `keybindings/`, `vim/`, and `buddy/` (initialization, WebSocket communication, and terminal rendering).
