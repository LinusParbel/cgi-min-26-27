# AI-assisted Blender modeling (Blender MCP + Claude Code, headless scripts, text-to-3D) for two Blender beginners building OBJ game assets

Research date: 2026-10-16. Context: 3-lane endless runner on a minimal C#/OpenTK engine (OBJ + one PNG per mesh; `.mtl` ignored; no glTF/PBR), 2 Blender beginners on Windows 11, 4–6 weeks, models are graded as the students' own work.

Source-quality caveat for the whole file: almost all "real-world experience" material on Blender MCP in 2026 is vendor or affiliate blog content (StraySpark sells a competing paid server, 3daistudio/Mixar/Neural4D/MindStudio sell adjacent products). I found **no Reddit or Hacker News threads** in search results and **no independent, reproducible benchmark** of geometry quality, speed or token cost. Claims below are labelled with their source; treat vendor claims as anecdotal.

---

## Q1. Current state of ahujasid/blender-mcp (now "mcp-for-blender"): repo, version, Windows + Claude Code install, Blender versions, features

### Takeaway
The community project is active and renamed: GitHub `ahujasid/mcp-for-blender`, PyPI `mcp-for-blender` 2.1.9 (6 Oct 2026, MIT, Python ≥3.10). It supports Blender 3.0+ and installs with `uv` plus a Blender add-on. In Claude Code you register it with `claude mcp add blender -- uvx mcp-for-blender`. It exposes arbitrary Python execution, scene inspection and viewport "look" screenshots, plus Poly Haven, Sketchfab and Poly Pizza assets, and Tripo, Hunyuan3D and Hyper3D Rodin generation.

### Cited Findings
- **Repo and name.** The repo is now `ahujasid/mcp-for-blender`, formerly `blender-mcp`. The PyPI package was renamed and old setups keep working. It describes itself as a "Community plugin to control Blender 3D with any LLM of your choice" and says it is a third-party integration, not made by Blender. — [GitHub README](https://github.com/ahujasid/blender-mcp)
- **PyPI release.** The latest version is **2.1.9, released 6 Oct 2026**, under the MIT license with Python ≥3.10. Releases are frequent: 2.0.4 on 24 Sep, 2.1.0 on 25 Sep, and 2.1.5 through 2.1.8 on 5 Oct 2026. — [PyPI mcp-for-blender](https://pypi.org/project/mcp-for-blender/)
- **Rename date conflict.**
  - StraySpark says the move to `mcp-for-blender` happened on 16 Sep 2026, "to avoid confusion with the official Blender Lab server", and that `uvx blender-mcp` still works as a compatibility wrapper. It counts 29,326 stars on 25 Sep 2026 and 36 tools, including `bpy_api_lookup` and `describe_node_type`, both added 15 Sep 2026. — [StraySpark comparison](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026) (vendor with a disclosed conflict of interest)
  - PyPI dates 2.1.0 to 25 Sep, so the exact rename date is unclear. — [PyPI](https://pypi.org/project/mcp-for-blender/)
- **Requirements.** Blender 3.0 or newer, Python 3.10 or newer, and the `uv` package manager. Install `uv` with the official installer, not `pip install uv`. — [GitHub README](https://github.com/ahujasid/blender-mcp)
- **Install steps, as given in the README:**
  - **Quick install:** a one-line PowerShell installer for Windows installs uv, configures MCP clients and installs the add-on.
  - **Claude Code:** `claude mcp add blender uvx mcp-for-blender`
  - **Add-on:** run `uvx mcp-for-blender install-addon`, then enable "Interface: MCP for Blender" in Blender's Add-ons preferences.
  - **Connect:** in the 3D viewport press N, open the "MCP for Blender" tab and click "Start MCP Server".

  — [GitHub README](https://github.com/ahujasid/blender-mcp)
- **Windows notes from the README:**
  - Add uv to the user PATH if needed.
  - GUI clients can fail with `spawn uvx ENOENT`. Use the full path to `uvx` or wrap the command as `cmd /c uvx mcp-for-blender`.
  - If conda or pyenv breaks the install, pin Python 3.11 with `UV_PYTHON_PREFERENCE=only-managed`.
  - Run only one MCP server instance at a time.

  — [GitHub README](https://github.com/ahujasid/blender-mcp)
- **Claude Code CLI syntax.** The general form is `claude mcp add [options] <name> -- <command> [args...]`. The `--` separates Claude's options (`--transport`, `--env`, `--scope`) from the server command.
  - `--env` accepts `KEY=value` pairs. If the server name directly follows `--env`, it is parsed as another pair, so put an option such as `--transport stdio` between them.
  - Scopes: `local` (default, `~/.claude.json`), `project` (`.mcp.json`, shared via git, approval prompt on first use) and `user`.
  - `claude mcp list`, `claude mcp get <name>` and `claude mcp remove <name>` manage servers. `/mcp` shows status inside a session.

  — [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)
- **Images in tool results.** When an MCP tool returns a PNG or JPEG, Claude sees the image inline. Claude Code also saves the full-resolution original under `~/.claude/projects/.../tool-results`, which needs v2.1.283+. `MAX_MCP_OUTPUT_TOKENS` controls the output limit. — [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)
- **Features.**
  - Core tools: `execute_blender_code` (run Python in Blender), `look` (viewport, camera, multi-angle, wireframe, X-ray, animation frames or renders), `get_scene_info` and `get_addon_status`.
  - Asset sources: Poly Haven (HDRIs, textures, models, no API key), Sketchfab, and Poly Pizza (low-poly models, free API key).
  - AI generation: `generate_3d` via Tripo, Hunyuan3D or Hyper3D Rodin. A "Premium" option provides these without your own keys; StraySpark says it costs $10 or $20 per month.

  — [GitHub README](https://github.com/ahujasid/blender-mcp); [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026)
- **Telemetry.**
  - Content collection (prompts, generated code, screenshots, scene data) is opt-in and off by default.
  - An anonymous usage record (install ID, tool name, success, duration, versions) is collected **by default**.
  - `DISABLE_TELEMETRY=true` turns off all telemetry.

  — [GitHub README](https://github.com/ahujasid/blender-mcp)
- **Documented limitations.**
  - Complex requests may need splitting into smaller steps, and timeouts can occur.
  - Poly Haven downloads run on Blender's main thread and freeze the UI.
  - Poly Pizza downloads can fail behind Cloudflare challenges from VPN or datacenter IPs.

  — [GitHub README](https://github.com/ahujasid/blender-mcp)
- **Older README note.** An earlier README said "Claude is sometimes erratic with its behaviour when using Poly Haven integration". — via [DEV Community summary](https://dev.to/githubopensource/blendermcp-unleash-the-power-of-ai-in-your-3d-modeling-workflow-1ooa) (older; may be stale)
- **Stability by version and OS.** MindStudio says stability depends on the Blender version and suggests 3.6 LTS as a common fix for compatibility errors. It reports socket reliability as "slightly better" on macOS and Linux than on Windows. — [MindStudio, 6 May 2026](https://www.mindstudio.ai/blog/claude-blender-mcp-real-world-performance) (vendor blog; this predates the 2.x releases and may be outdated)

### Inferences
- **Recommended Windows command for Claude Code**, using the documented flags with telemetry off and safe mode on. This is my synthesis of README and docs syntax, not tested here:
  `claude mcp add --transport stdio --env BLENDER_MCP_SAFE_MODE=1 --env DISABLE_TELEMETRY=true blender -- uvx mcp-for-blender`
  If you get `ENOENT` errors, replace the part after `--` with `cmd /c uvx mcp-for-blender`.
  Use local scope, not `project`, so the server is not pushed to teammates via `.mcp.json` without each person opting in.
- **Pin the version.** With roughly 10 releases in under three weeks, pin one (`uvx mcp-for-blender@2.1.9`, standard uvx syntax) for the duration of the project so behaviour doesn't change mid-semester.
- **Blender version choice.** The current manual is Blender 5.2 LTS ([Blender manual](https://docs.blender.org/manual/en/latest/files/import_export/obj.html)). A 5.x LTS works with both the community server (3.0+) and the official Lab server (5.1+), so choosing 5.1+ keeps both options open.

### Gaps
- I could not see GitHub release tags or the issue tracker contents. The README capture showed an empty Releases section, and I did not review the issues for Windows or Claude Code bugs.
- I found no first-hand test of the PowerShell one-line installer on Windows 11.

---

## Q2. Other or official Blender MCP servers (2025–2026)

### Takeaway
Yes. Since April 2026 there is an **official Blender Lab MCP server** (projects.blender.org/lab/blender_mcp, v1.0.3, Blender 5.1+, GPL-3.0-or-later per a secondary source). It is aimed at scene inspection, Python API and documentation lookup, and debugging, not asset generation. Anthropic launched a Blender connector for Claude on 28 Apr 2026 and joined the Blender Development Fund as a Corporate Patron. Many smaller community servers and paid servers also exist.

### Cited Findings
- **What the official server is.** Blender.org describes "a lightweight MCP server for Blender" that provides a natural language interface to Blender's Python API, better access to documentation, and help exploring complex scenes.
  - The add-on package is **v1.0.3** and needs **Blender 5.1 or newer**.
  - You install three parts separately: the add-on (drag-drop or "Install from Disk", optionally adding the Blender Lab extension repo), an MCP-compatible client, and the MCP server, either as a `.mcpb` bundle or from source.
  - The page names Llama.cpp as an example client and does not mention Claude Code.

  — [blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/)
- **Official example uses:**
  - finding high-poly objects that are small on screen
  - renaming data-blocks (applied only if approved)
  - querying which objects use a material
  - explaining a Geometry Nodes setup

  Known limits: results depend on the model, and the LLM's first scene analysis ignored non-viewport modifiers such as Solidify. — [blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/)
- **Official security statement.** The server "will execute LLM generated code in Blender without any guards in place to protect your data". Blender recommends a virtual machine or a system without sensitive data. — [blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/)
- **Version history, per StraySpark:**
  - v0.1.0 on 24 Mar 2026 (pre-release)
  - first `.mcpb` pre-release on 10 Apr 2026
  - v1.0.0 on 27 Apr 2026
  - v1.0.2 on 8 Sep 2026
  - v1.0.3 on 11 Sep 2026 (screenshot fix)

  — [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026) (vendor with a conflict of interest; I could not open projects.blender.org, HTTP 403)
- **Official architecture, per StraySpark.** The add-on opens a local TCP socket, and a separate Python process launched by the client over stdio relays to it. StraySpark lists 26 tools:
  - code execution
  - blend-file, object and collection summaries
  - screenshots and viewport navigation, plus viewport and thumbnail renders
  - two search tools over bundled copies of the Python API reference and the user manual
  - six `_for_cli` variants that open a `.blend` in a background Blender process

  — [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026)
- **Anthropic connector launch.** Anthropic announced a Blender connector on 28 Apr 2026 as one of nine creative-tool connectors, together with Adobe, Ableton, Autodesk Fusion, SketchUp and others. Claude can analyse and debug scenes, batch-edit objects via scripts, and add tools to Blender's UI. Anthropic joined the Blender Development Fund as a Corporate Patron, a tier of at least €240k per year. — [Unite.ai](https://www.unite.ai/anthropic-wires-claude-into-photoshop-blender-and-ableton/); [NYU RITS](https://rits.shanghai.nyu.edu/ai/anthropic-plugs-claude-into-adobe-blender-and-ableton-with-nine-new-connectors/); [implicator.ai](https://www.implicator.ai/anthropic-brings-claude-into-9-creative-tools-as-openai-and-gemini-push-images/)
  - One commentator called the demo examples underwhelming. — [texxr](https://texxr.com/1167883/anthropic-launches-claude-connectors-for-creatives)
- **Connector guide (mcp.directory).** It describes setup in Claude Desktop (Settings → Connectors → Browse → enable "Blender"; the BlenderMCP sidebar panel shows "Connected"), with no Claude Code command. It contrasts the two servers: the official connector covers core `bpy` only, while the community server adds Poly Haven, Sketchfab, Hyper3D and Hunyuan3D. Known issues it lists:
  - only one client per Blender session
  - the first command can hang on a startup race
  - no Python sandbox
  - screenshots add token cost
  - the connector "doesn't generate models by itself"

  — [mcp.directory, 29 Apr 2026](https://mcp.directory/blog/claude-blender-connector-guide)
  - **Conflict:** this guide says Blender 3.0+ with 4.5 LTS recommended for the official connector. That contradicts blender.org's "Blender 5.1 or newer", so I trust blender.org.
- **Brecht's guidance (devtalk).** In a Blender devtalk thread, user "brecht" recommended that Blender MCP focus on learning and usability rather than generative builds:
  - explaining errors
  - suggesting export settings
  - naming data-blocks
  - running scene checklists

  — [Blender devtalk, Feb 2026](https://devtalk.blender.org/t/3d-agent-blender-ai-assistant-built-a-multi-agent-system-on-top-of-blenders-mcp-and-python-api-and-sharing-architecture-learnings-for-the-lab-discussion/44260). The page doesn't state his role; it is widely known that Brecht Van Lommel is a Blender core developer, but that is my own knowledge, not stated in the source.
- **Other servers:** community servers such as `djeada/blender-mcp-server` (OBJ export tool, Python execution with "bridge" or "headless" transport), `ssoj13/blender-mcp-rs` and others are listed on Glama. StraySpark sells a paid "Blender MCP Server". — [djeada GitHub](https://github.com/djeada/blender-mcp-server); [Glama listing](https://glama.ai/mcp/servers/ssoj13/blender-mcp-rs); [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026)
- **BestGames split.** The guide recommends the official connector for scene inspection, cleanup and controlled batch edits, and the community server mainly for its asset integrations. — [BestGames, 20 Jul 2026](https://best-games.io/blog/codex-claude-code-blender-mcp-game-development-guide)

### Inferences
- **For graded own models:** the official server's tool set (API and manual search, scene summaries, screenshots, explanations) fits a *tutor / reviewer* role better than an *asset generator* role. It also lacks the one-click "download a model / generate a model" tools that would tempt beginners to skip modeling.
- **Claude Code + official server is unconfirmed.** The `.mcpb` bundle or a from-source stdio launch should work with Claude Code as with any stdio MCP server, but I found no documented `claude mcp add` command for it.

### Gaps
- The official repo README and license file were not directly accessible (projects.blender.org returned 403). The GPL-3.0 and 26-tool details are secondhand via StraySpark.
- I found no documented Claude Code setup for the official Lab server.

---

## Q3. Real-world experience: geometry quality, failure modes, speed, token cost, reliability

### Takeaway
Consistent (but mostly vendor-sourced) picture: LLM-written `bpy` geometry is **decent for primitive-based, hard-surface, architectural and modular shapes**. That covers cones, barriers, bins, benches, lamp posts, coins and street tiles. It is **poor for organic forms**, clean edge-flow topology, Geometry Nodes, and precise spatial placement. Quality depends heavily on a **screenshot/verification loop**. Without one, results drift after a few steps. No source quantifies token cost or time savings.

### Cited Findings
- **What works and what fails (MindStudio).**
  - Works: scene setup from primitives with transforms, lighting and camera ("where the integration shines"); hard-surface and architectural scenes; basic Principled BSDF materials; utility scripts (batch renaming, cleanup, export).
  - Fails or needs heavy correction: organic forms (faces, trees, foliage); clean topology ("doesn't think in terms of edge loops"); Geometry Nodes ("brittle", the API changes between versions); rigging and weight painting; precise spatial placement ("often takes several correction rounds"); visual judgment of proportions and aesthetics.
  - Python errors are common and complex scripts need several iterations. Sculpt mode "isn't accessible via MCP".
  - No speed benchmarks are given. Setup takes about 15–30 minutes. MindStudio says experienced artists are faster under tight deadlines.

  — [MindStudio, 6 May 2026](https://www.mindstudio.ai/blog/claude-blender-mcp-real-world-performance) (vendor blog)
- **Primitives, booleans and drift (3daistudio).** Organic forms end up as assemblies of primitives, and boolean results carry n-gons and uneven density. Hard-surface and architectural shapes fare much better. Long sessions suffer context drift, and every scene inspection uses context. — [3daistudio](https://www.3daistudio.com/3d-generator-ai-comparison-alternatives-guide/blender-mcp) (vendor of a competing generator)
- **Topology and visibility (StraySpark).** Edge flow and deformation-friendly layout are judgment calls the model doesn't make well, so output needs retopology before rigging or subdivision. Heavy operations (remesh, bake) can exceed tool-call timeouts. — [StraySpark step-by-step](https://www.strayspark.studio/blog/blender-mcp-ai-assisted-3d-modeling-step-by-step-2026) (vendor)
  - Its claim that agents "can't see the viewport in the standard setup" is contradicted by the current community README, which has a `look` tool with multi-angle and wireframe views. — [GitHub README](https://github.com/ahujasid/blender-mcp)
- **Undo is awkward** because each operation is a separate Python execution. — [Mixar](https://www.mixar.app/blender-agent/blender-mcp-guide) (vendor)
- **Multi-agent builder on devtalk (author's own claims, no benchmark):**
  - "Just executing code blindly produces garbage after 3-4 steps"; without verification the agent drifts into "geometry soup".
  - Sending a viewport screenshot back after each operation was "the single biggest quality improvement".
  - Lattice, curve and symmetry math "sometimes need a dedicated pass" and are "not fully reliable yet".
  - Two runs of the same prompt gave different results.
  - An Eiffel Tower demo took about 4–5 minutes. Author's verdict: "Is it production-ready? No."

  — [Blender devtalk, 7 Feb 2026](https://devtalk.blender.org/t/3d-agent-blender-ai-assistant-built-a-multi-agent-system-on-top-of-blenders-mcp-and-python-api-and-sharing-architecture-learnings-for-the-lab-discussion/44260)
- **BestGames guide (mostly secondhand).**
  - Agents suit "repetitive, measurable" work: low-poly props, modular pieces, naming and export automation.
  - It advises against relying on the agent for hero characters, UVs, rigging, animation or licensing.
  - It recommends writing a measurable asset brief first: grid size, module list, origin convention, naming prefix, material and texture limits, delivery format.
  - Suggested loop: blockout → four-view inspection → materials → game-ready checks → early export → player test.
  - Defects such as thin backs, reversed normals and floating parts can hide behind the hero camera.
  - It calls "production-ready" claims misleading.

  — [BestGames, 20 Jul 2026](https://best-games.io/blog/codex-claude-code-blender-mcp-game-development-guide)
- **Token cost.** Each viewport screenshot adds token cost. — [mcp.directory](https://mcp.directory/blog/claude-blender-connector-guide). MindStudio does not quantify cost and notes Pro subscribers can use it via Claude Desktop while API users pay per token. — [MindStudio](https://www.mindstudio.ai/blog/claude-blender-mcp-real-world-performance)
- **Community reports.** Searches for Reddit and Hacker News threads returned no relevant hits. — (search results, no citable thread)

### Inferences
- **Fit for the team's asset list:**
  - **Good candidates for script-based or AI-assisted construction:** traffic cone (lathe or cylinder with taper), construction barrier (boxes plus stripes via UV), wheelie bin (tapered box + lid + cylinders), bench (boxes and arrays), lamp post (cylinders + curve), coin (cylinder + bevel, maybe embossed text), modular street tiles and facades (arrays of windows and doors on a fixed grid, exactly 1 m units).
  - **Medium:** e-scooter (thin tubes, handlebars and wheels; placement precision issues are likely) and the simplified Kröpcke clock (a column with a 4-sided clock head, roof and finial). The Kröpcke clock is mostly cylinders and boxes, so it is feasible as a simplified blockout. Its distinctive proportions need human reference-checking.
  - **Organic content:** none on the list. That is favourable for AI assistance, but also means the parts graders may care about (silhouette, proportion, UV/texture work) are exactly the "visual judgment" areas where LLMs are weakest.
- **UVs are the main technical risk for this engine.** No source evaluated LLM UV unwrapping. The engine needs one UV set and one PNG per OBJ. Simple, scriptable approaches are cube or box projection and a small "palette texture" (each face mapped to a colour swatch). These are robust to script, but this is my inference and untested here.
- **Token and time estimates:** none are citable. Beginners should budget extra iterations, as the MindStudio and devtalk reports suggest.

### Gaps
- No independent benchmark of LLM-generated mesh quality, iteration count, wall-clock time or token cost for game props.
- No first-hand Reddit, HN or YouTube reports were retrievable through search. YouTube demos were not reviewed.
- No source specifically evaluated LLM-generated UV unwrapping or texture-atlas workflows.

---

## Q4. Security concerns and safeguards

### Takeaway
Both servers run **unsandboxed LLM-generated Python** inside Blender with the user's privileges. The community add-on's socket has **no authentication**, and a CVE (CVE-2026-10688) was filed against `execute_blender_code`. The safeguards are: localhost only, safe mode, telemetry off, save or back up work, keep the project in git, run one server, don't feed untrusted downloaded assets or text into the session, and review code before approving.

### Cited Findings
- **Community add-on.**
  - `execute_blender_code` "can run arbitrary Python. Save your work first."
  - The add-on socket has **no authentication or encryption**; anyone who can reach the port can run code. Keep it on localhost or use an SSH tunnel.
  - `BLENDER_MCP_SAFE_MODE=1` checks scripts and blocks file, network and process access.

  — [GitHub README](https://github.com/ahujasid/blender-mcp)
  - StraySpark adds that safe mode also blocks "persistent code". — [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026)
- **Official server.** It "will execute LLM generated code in Blender without any guards"; Blender recommends a VM or a system without sensitive data. — [blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/)
- **CVE-2026-10688.** A code-injection flaw in `execute_blender_code` in `src/blender_mcp/server.py`, in ahujasid blender-mcp up to commit `7636d13…`. The code parameter is passed to Blender's Python without sanitising or sandboxing.
  - NVD CVSS v3.x: 5.5 (Medium); CVSS v2: 6.5.
  - Sources disagree on patch status and on whether a public exploit exists.
  - Feedly references GHSA-fx9q-x9g5-jgg6.

  — [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-10688); [SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2026-10688/); [Feedly](https://feedly.com/cve/CVE-2026-10688)
- **Prompt injection (BestGames).** The guide cites a security report on unsanitised code execution and prompt injection. It recommends saving the `.blend` before agent edits, working in a disposable project, and keeping a manifest (source, creator, license, changes) for every external asset. — [BestGames](https://best-games.io/blog/codex-claude-code-blender-mcp-game-development-guide)
- **Claude Code's own guidance.**
  - Verify you trust each server; servers that fetch external content expose you to prompt injection.
  - Project-scoped `.mcp.json` servers require approval.
  - Server authors can mark a tool as always requiring approval (`anthropic/requiresUserInteraction`).

  — [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)
- **Telemetry** is on by default (anonymous usage records); `DISABLE_TELEMETRY=true` turns it off. — [GitHub README](https://github.com/ahujasid/blender-mcp)

### Inferences
- **Recommended safeguards for the team:**
  1. Set safe mode and turn telemetry off in the `claude mcp add` env.
  2. Never allow-list `execute_blender_code` permanently. Approve per call, which forces reading the code (also good for learning).
  3. Keep `.blend` files and generator scripts under git and save before each session.
  4. Don't enable Sketchfab, Poly Pizza or generator downloads in the graded workflow. Downloaded files are untrusted data, and they cause authorship issues.
  5. Don't expose the port (default localhost; no port forwarding).
  6. Run only one client at a time.
- **Headless scripts reduce exposure.** The headless-script pattern (Q5) has a smaller attack surface: no listening socket, and every script is a reviewable file in git before it runs.

### Gaps
- Whether CVE-2026-10688 is fixed in 2.1.x is unverified. I did not open the GHSA advisory.
- Exactly what safe mode blocks, and whether it can be bypassed, was not independently assessed.

---

## Q5. Alternative: Claude Code writes standalone Blender Python generator scripts run headless (`blender --background --python script.py`) to produce OBJ

### Takeaway
This is a well-supported, documented Blender workflow and fits this project unusually well:
- The engine's conventions (Y-up / −Z forward OBJ) match `wm.obj_export` defaults.
- The assets are procedural or hard-surface.
- Scripts in git are reproducible, reviewable and diffable, and they clearly document authorship.

The trade-off: no live visual feedback unless you render previews or open the result in Blender. Most importantly for grading, "we wrote/prompted a script" may count as less hands-on Blender modeling than the course wants.

### Cited Findings
- **Headless basics.** Blender runs in background mode with a Python script, and script arguments go after `--`. `print()` output goes to the terminal in background mode. — [Claude Code for Blender Python guide](https://claudecodeguides.com/claude-code-blender-python-scripting-2026/); [skills.sh blender-scripting](https://skills.sh/terminalskills/skills/blender-scripting)
- **Operator names.** Older builds used `export_scene.obj`; newer ones use `wm.obj_export` (3.6+). Prefer `bmesh` and `bpy.data` for geometry, and keep `bpy.ops` for context-dependent operations, because operators can fail without the right context. — [skills.sh blender-scripting](https://skills.sh/terminalskills/skills/blender-scripting) (community guide)
- **`bpy.ops.wm.obj_export` signature (current API docs).** Relevant defaults:
  - `forward_axis='NEGATIVE_Z'`, `up_axis='Y'`, `global_scale=1.0`
  - `apply_modifiers=True`, `apply_transform=True`, `export_selected_objects=False`
  - `export_uv=True`, `export_normals=True`, `export_materials=True`
  - `export_triangulated_mesh=False`, `export_smooth_groups=False`
  - `collection=''`

  — [Blender Python API: bpy.ops.wm](https://docs.blender.org/api/current/bpy.ops.wm.html)
- **Procedural materials don't export.** Procedural materials and assets don't export out of the box and must be baked first. — [Infinigen docs](https://infinigen.cs.princeton.edu/docs/latest/_sources/ExportingToExternalFileFormats.md)
- **Headless options in MCP servers.** The official Lab server includes `_for_cli` tool variants that open a `.blend` in a background Blender process. — [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026). `djeada/blender-mcp-server` offers a "headless" transport and an OBJ export tool. — [djeada GitHub](https://github.com/djeada/blender-mcp-server)
- **Non-determinism.** Same-prompt LLM runs differ. — [devtalk](https://devtalk.blender.org/t/3d-agent-blender-ai-assistant-built-a-multi-agent-system-on-top-of-blenders-mcp-and-python-api-and-sharing-architecture-learnings-for-the-lab-discussion/44260). Running a *saved* script is deterministic (aside from seeded randomness), which removes that problem at execution time.

### Inferences
- **Pros vs. live MCP:**
  - **Reproducible:** re-run the script to regenerate every OBJ after a scale change.
  - **Parametric:** lane width, segment length and facade window count become variables, which suits modular 3-lane segments that must tile exactly.
  - **Auditable:** git history shows who changed what, an authorship trail for grading.
  - **No socket, no extra MCP server, no telemetry;** Claude Code's normal Bash and Edit permissions cover it.
  - **Cheaper in tokens:** no screenshots needed per step, though preview renders can be added.
  - **CI-like batch export:** "export all assets" becomes one command.
- **Cons:**
  - No interactive viewport. Beginners must open the `.blend` or a rendered PNG to judge the look.
  - Scripts are poor at "artistic" tweaks (manual vertex nudging, UV seam placement).
  - Learning shifts from Blender UI and modeling skills to `bpy` scripting, which may not match what the CGI course grades.
  - API names drift between Blender versions (`export_scene.obj` vs `wm.obj_export`; Geometry Nodes changes), so pin one Blender version.
- **Engine-specific export settings** (derived from the API defaults and the engine constraints in CLAUDE.md):
  - Keep the defaults `forward_axis='NEGATIVE_Z'`, `up_axis='Y'` and `global_scale=1.0`.
  - Set `export_triangulated_mesh=True` (the engine triangulates anyway, but this avoids n-gon ambiguity).
  - Set `export_materials=False` (the engine ignores `.mtl`).
  - Keep `export_uv=True` and `export_normals=True`, and set `export_selected_objects=True`, or export per object so that one OBJ = one mesh = one texture.
  - Bake or paint textures to a single PNG; procedural shaders won't carry over.
- **Hybrid that keeps authorship (recommended):**
  1. Model each asset manually in Blender (blockout → refine → UV → texture).
  2. Use Claude Code mainly for:
     - a headless **export/validation script** (triangulate, apply transforms, check scale, origin, normals and UVs, write the OBJ and PNG to `RunnerGame/Assets/`)
     - **procedural generators only for the truly repetitive pieces** (street-segment variants, facade window arrays, coin)
  3. Treat the live MCP as a tutor: "explain why my normals are flipped", "list objects without UVs".

  This matches brecht's devtalk suggestion (diagnostics, export settings, checklists) and the BestGames "repetitive, measurable" framing.

### Gaps
- No source directly compares headless-script vs. live-MCP workflows on quality, time or cost. The pros and cons above are reasoned, not measured.
- Not verified here by actually running Blender headless on this machine.

---

## Q6. AI text-to-3D / image-to-3D generators (Meshy, Tripo, Hyper3D Rodin, Hunyuan3D, TRELLIS)

### Takeaway
These tools produce **dense, often messy triangle meshes** with baked or PBR textures, usually as GLB/FBX. Using them in this engine requires decimation or retopology, plus conversion to OBJ with a single base-colour PNG. Licensing varies:
- **Meshy and Tripo free tiers:** CC BY 4.0 with attribution; free-tier Tripo models are public.
- **Rodin's free-tier terms:** unclear.
- **Hunyuan3D's community license explicitly excludes the EU, UK and South Korea.** This is a real problem for a team in Germany.
- **TRELLIS.2:** reportedly MIT, but local use needs Linux and a ≥24 GB NVIDIA GPU.

For graded "own models", a generated mesh is not the student's model.

### Cited Findings
- **Meshy.** The official pricing page licenses Free-plan outputs under **CC BY 4.0** with commercial use allowed with attribution; output ownership is listed as the user's. A full text/image-to-3D generation costs 20 credits, and failed generations are free. — [Meshy pricing docs](https://docs.meshy.ai/en/webapp/pricing)
  - The help centre says Meshy owns the output and licenses it to the user under CC BY 4.0. Community-page posts are CC0. — [Meshy help: commercial use](https://intercom.help/meshy/en/articles/16102098-can-i-use-meshy-assets-commercially)
  - Third-party sites claim 10 credits per generation and "non-commercial" free use, which contradicts the official page. — [StackSheriff](https://stacksheriff.com/ai-tools/meshy-ai-pricing/); [Sorceress](https://sorceress.games/blog/best-free-ai-3d-model-generator-honest-2026-picks)
- **Tripo.** Tripo's own blog says the free tier is CC BY 4.0, commercial use with attribution. — [Tripo blog](https://www.tripo3d.ai/blog/commercial-use-ai-3d-models)
  - Contradicted by third-party sites claiming free = non-commercial only. Free-tier models are reportedly public. Free credits are reported as 200 or 300 per month, depending on the source. — [CostBench Tripo free plan](https://costbench.com/software/ai-3d-generation/tripo-ai/free-plan/)
- **Hyper3D Rodin.** Third parties report about 10 free credits on signup, with credits spent only on download. I could not confirm the free-tier license from an official source. The official pricing page says exported models can be used for "any use" but is ambiguous about which tier that applies to. — [Hyper3D pricing](https://hyper3d.ai/pricing); [CostBench Rodin free plan](https://costbench.com/software/ai-3d-generation/rodin-hyper3d/free-plan/)
- **Hunyuan3D.** The 2.0 and 2.1 community licenses define "Territory" as worldwide **excluding the European Union, United Kingdom and South Korea**, and the rights grant is limited to that Territory. — [Hunyuan3D-2 LICENSE on Hugging Face](https://huggingface.co/tencent/Hunyuan3D-2/blob/main/LICENSE); [mirror of the 2.0 license text](https://open.windriver.com/info/uni-license-list/licenses/tencent-hunyuan-3d-2.0-cla.html)
- **TRELLIS.2.** Microsoft's model (released December 2025) is 4B parameters with an O-Voxel representation. It outputs PBR materials and exports to GLB. It is reported as MIT-licensed. Local use needs Linux and an NVIDIA GPU with ≥24 GB; a web demo exists. — [ComfyUI wiki](https://comfyui-wiki.com/en/news/2025-12-18-microsoft-trellis2-3d-generation); [mer.vin](https://mer.vin/2026/05/trellis-2-4b-explained-single-image-3d-with-o-voxel-pbr-glb-and-3-second-inference/?amp=1) (secondary sources; primary repo and license not checked)
- **Topology and density.**
  - AI meshes are "notoriously dense (500K+ polygons for a simple object)". — [levelup.gitconnected](https://levelup.gitconnected.com/building-game-ready-3d-assets-fast-the-best-ai-generators-for-production-workflows-in-2026-f1f725ff5df0)
  - A Tripo 3.0 model went from 1,482,050 triangles to 11,748 quad faces with Tripo's retopology tool. — [Scenario help: Tripo family](https://help.scenario.com/articles/4692888910-tripo-family-the-complete-guide)
  - Meshy's quad remesher is on paid plans. In a head-to-head test run by a Meshy employee (so possibly biased), Tripo had the cleanest topology and face count didn't predict quality. — [HackerNoon stress test](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show?source=rss)
- **Integration in mcp-for-blender.** The community server can call Tripo, Hunyuan3D and Rodin directly from Blender via `generate_3d`. — [GitHub README](https://github.com/ahujasid/blender-mcp)
- **Record-keeping (BestGames).** Downloaded models carry varying licenses, and AI-generated models need a record of the service terms and of human edits. — [BestGames](https://best-games.io/blog/codex-claude-code-blender-mcp-game-development-guide)

### Inferences
- **Suitability for this engine:** low to moderate. Each generated asset needs:
  1. GLB import into Blender
  2. decimation or retopology to a sensible budget (e.g. a few hundred to a few thousand triangles for a cone, bin or bench)
  3. re-UV or reuse of the generated UVs
  4. baking PBR down to a single base-colour PNG, because the engine has no PBR and does no sRGB conversion
  5. OBJ export

  For simple hard-surface props, modeling by hand is likely *faster* for this pipeline than cleaning up a 500k-triangle generator mesh.
- **Grading conflict:** a generator output is not "their own model" in any meaningful sense, even after cleanup. Defensible uses, if the course permits AI at all:
  - generating a **reference image or turnaround** to model from
  - a **throwaway placeholder** for gameplay testing, replaced before submission
  - a clearly labelled non-graded background asset

  Hunyuan3D should be avoided entirely by an EU-based team because of the license's territory clause. If the hosted Hunyuan3D API used via mcp-for-blender has different terms, that is unverified.

### Gaps
- Tripo's and Rodin's current official ToS were not read in full; free-tier commercial and attribution terms conflict across sources.
- No independent topology benchmark across generators was found; most reviews are vendor-affiliated.
- TRELLIS.2 primary license file and repo not checked.

---

## Q7. Recommendation framing: AI-assisted vs. manual share for graded beginners; how to document AI use

### Takeaway
I found no 3D-specific or LUH-specific policy. Generic university guidance converges on three points: check the course rules, assume restrictions unless AI use is permitted, and disclose the tool, its role and the extent of human work. The evidence on quality supports AI as **tutor, reviewer, pipeline/export automation and generator of repetitive procedural parts**, and modeling, UVs and texturing of each graded asset by hand.

### Cited Findings
- **Default rules differ by university.**
  - UNBC: students should assume GenAI use "might be restricted" unless the course says otherwise. Its guidance explicitly lists 3D models among GenAI outputs. — [UNBC guidance](https://unbc.ca/provost/guidance-acceptability-using-generative-ai-coursework)
  - Vanderbilt: without instructor guidance, GenAI use is allowed if disclosed; cite and disclose all uses when in doubt. — [Vanderbilt](https://www.vanderbilt.edu/generative-ai/students/)
- **What disclosures must contain.**
  - UMass Dartmouth requires disclosure of AI use in coursework submitted for credit, describing the tool's role. — [UMass Dartmouth guidelines](https://newbedfordlight.org/wp-content/uploads/2026/03/UMass-Dartmouth-Guidelines-on-Generative-AI_Approved-1.pdf)
  - UMass's graduate policy requires stating the extent of human oversight. — [UMass policy](https://www.umass.edu/resource-economics/book/policy-graduate-student-use-generative-artificial-intelligence-ai-technology)
  - Columbia TC asks for the specific tools and models. — [Columbia TC newsletter](https://www.tc.columbia.edu/media/centers-amp-labs/dfi/faculty-newsletters/Faculty-Newsletter-Vol-25.pdf)
- **German examples.**
  - Uni Münster (FB6): AI in exams is allowed in principle with conditions. It requires a declaration naming the tools and how they were used, and full prompts and outputs attached as an appendix. — [Uni Münster FB6](https://www.uni-muenster.de/FB6/studium/umgang_mit_ki/index.html)
  - Uni Bremen (IES): undisclosed AI content submitted as one's own work counts as misconduct, and the lecturer decides the permitted scope. — [Uni Bremen](https://www.uni-bremen.de/fb8/ies/ba-integrierte-europastudien-1/neue-ki-richtlinie)
  - TU Braunschweig has an AI guideline. — [TU Braunschweig Leitlinie KI](https://tu-braunschweig.de/fileadmin/Allgemeine_Dokumente/Ordnungen/2024-10-07_-_Leitlinie_KI_-_Guideline_AI.pdf)
  - TiHo Hannover has a student/teacher leaflet. — [TiHo Merkblatt](https://www.tiho-hannover.de/fileadmin/01_Verwaltung/Dez3_Studierende/230915_Merkblatt_KI_an_der_TiHo.pdf)
- **Experts' view.** Both the BestGames guide and the devtalk author say agents are not production-ready and work best for well-defined, measurable parts of the pipeline. — [BestGames](https://best-games.io/blog/codex-claude-code-blender-mcp-game-development-guide); [devtalk](https://devtalk.blender.org/t/3d-agent-blender-ai-assistant-built-a-multi-agent-system-on-top-of-blenders-mcp-and-python-api-and-sharing-architecture-learnings-for-the-lab-discussion/44260)

### Inferences
- **Ask the lecturer first** (one email): is AI-assisted scripting allowed for graded models, and do procedural `bpy` generators count as own models? Rules are set per course in German universities (Bremen, Kempten, Münster examples).
- **Suggested split for 2 beginners over 4–6 weeks** (judgment, not sourced):
  - **Manual, about 70–85% of graded modeling effort:** every graded prop's blockout, refinement, UV unwrap and texture painting or atlas, done in the Blender UI. Start with cone, barrier and coin to learn the basics, then bin, bench and lamp, then the e-scooter and Kröpcke clock.
  - **AI-assisted, about 15–30%:**
    - Claude Code writes the **export/validation script** (non-graded tooling).
    - It writes **procedural generators** for repetitive modular street segments and facade window arrays. The students define the parameters and design and review every line.
    - It acts as tutor or reviewer via MCP: diagnostics, explaining operators, checking normals and UVs.
  - **Avoid:** text/image-to-3D generators and Sketchfab/Poly Pizza downloads for any graded asset. Hunyuan3D is avoided entirely for license reasons.
- **Documentation recipe**, consistent with the policies cited above:
  - an `AI_USAGE.md` (or report section) per asset, listing the tool and model (e.g. "Claude Code, Claude Opus X, mcp-for-blender 2.1.9"), the purpose, and what was human vs. AI
  - committed generator scripts, with prompts summarised in comments or commit messages
  - before/after screenshots of manual edits
  - an asset manifest with source, creator, license and changes, as suggested by BestGames
- **Fallback if the course forbids AI for modeling:** the export/validation script and engine-side code are still likely fair use of Claude Code, as coding assistance on the C# side, but confirm this too.

### Gaps
- No LUH or Hochschule Hannover policy, and no CGI course-specific rule, was found. The lecturer's policy is the deciding factor and is unknown.
- No source addresses whether procedurally *scripted* geometry counts as "own modeling" in graphics courses.
