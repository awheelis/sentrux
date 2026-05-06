<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg?v=2">
  <source media="(prefers-color-scheme: light)" srcset="assets/logo-light.svg?v=2">
  <img alt="sentrux" src="assets/logo-dark.svg?v=2" width="500">
</picture>

<br>

**The sensor that helps AI agents close the feedback loop.**<br>Structural quality analysis for Python code.

[![CI](https://github.com/sentrux/sentrux/actions/workflows/ci.yml/badge.svg)](https://github.com/sentrux/sentrux/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**English** | [中文](README.zh-CN.md) | [Deutsch](README.de.md) | [日本語](README.ja.md)

[How it Works](#how-it-works) · [Quick Start](#quick-start) · [MCP Integration](#mcp-server) · [Rules Engine](#rules-engine)

</div>

## How it works

AI agents write code at machine speed. But without visibility into architectural health, codebases degrade just as fast.

sentrux measures structural quality in real-time:

- **5 root cause metrics** (modularity, acyclicity, depth, equality, redundancy)
- **One continuous score** (0–10000)
- **Architectural rules engine** (CI-friendly constraints)
- **MCP integration** (real-time feedback for Claude, Cursor, etc.)

When your agent writes code, you see immediately whether quality improved or degraded.

## Quick Start

**Install** (Python 3.9+)

```bash
pip install sentrux
```

**Run it**

```bash
sentrux scan .              # Analyze current project and show quality score
sentrux check .             # Check if project meets architectural rules
sentrux gate --save .       # Save baseline before starting an AI session
sentrux gate .              # Compare after — catches quality degradation
sentrux --mcp               # Start MCP server for AI agent integration
```

**Connect to your AI agent** (optional)

Claude Code:
```
/plugin marketplace add sentrux/sentrux
/plugin install sentrux
```

Cursor / Windsurf / any MCP client — add to your MCP config:
```json
{
  "mcpServers": {
    "sentrux": {
      "command": "sentrux",
      "args": ["--mcp"]
    }
  }
}
```

**From source**

```bash
git clone https://github.com/sentrux/sentrux.git
cd sentrux
pip install -e .
```

## The Problem

You start a project with Claude Code or Cursor. Day one is magic. The agent writes clean code, understands your intent, ships features fast.

Then something shifts.

The agent starts hallucinating functions that don't exist. It puts new code in the wrong place. It introduces bugs in files it touched yesterday. You're spending more time fixing the agent's output than writing it yourself.

Everyone assumes the AI got worse. **It didn't.** Your codebase did.

Here's what happened: you lost visibility into architecture. The agent modifies dozens of files per session. You see `Modified src/foo.py` in the terminal, but you've lost spatial awareness. You don't see the dependency graph. You don't see that it just created a cycle. You don't see that three modules now depend on a file that was supposed to be internal.

**Every AI session silently degrades your architecture.**

Same function names, different purposes, scattered across files. Unrelated code dumped in the same folder. Dependencies tangling into spaghetti. When the agent searches your project, it finds twenty conflicting matches — and picks the wrong one. Every session makes the mess worse.

**The traditional answer doesn't work.** Tools like GitHub Spec Kit try to plan architecture first, then let AI implement. But there's zero visibility into whether the implementation actually matches the spec. No feedback loop.

**You don't need a better plan. You need a better sensor.**

## The Solution

sentrux is the missing feedback loop for AI-assisted development.

It watches your Python codebase in real-time — every file, every dependency, every architectural relationship. Computed in milliseconds.

**5 root cause metrics, one continuous score.**

- **Modularity**: Are dependencies contained or scattered?
- **Acyclicity**: Are there circular dependencies?
- **Depth**: How deep is the import structure?
- **Equality**: Is complexity evenly distributed or concentrated?
- **Redundancy**: How much code is duplicated?

When architecture degrades, you see it immediately — not two weeks later when everything is broken.

sentrux gives you the sensor. Your rules give you the spec. The agent is the actuator. **The loop closes.**

## MCP Server

Connect sentrux to any AI agent via Model Context Protocol.

```
Agent: scan("/Users/me/myproject")
  → { overall_score: 7342, file_count: 139, modularity: 0.73, acyclicity: 0.92 }

Agent: session_start()
  → { status: "Baseline saved", score: 7342 }

  ... agent writes code ...

Agent: health()
  → { overall_score: 6891, modularity: 0.58, acyclicity: 0.85 }
  → Quality degraded during this session
```

**Available MCP tools:**

- `scan` – Analyze workspace and get quality metrics
- `health` – Get current project quality score
- `check_rules` – Verify architectural rules compliance
- `session_start` – Initialize a session and save baseline
- `session_end` – End session and compare results
- `evolution` – Track quality over time
- `test_gaps` – Identify untested modules

## Rules Engine

Define architectural constraints. Enforce them in CI. Let the agent know the boundaries.

**Example `.sentrux/rules.toml`**

```toml
[constraints]
max_cycles = 0              # No circular dependencies allowed
max_cc = 25                 # Max cyclomatic complexity per function
max_fn_lines = 100          # Max function length

[[layers]]
name = "core"
paths = ["src/core/*"]
order = 0

[[layers]]
name = "analysis"
paths = ["src/analysis/*"]
order = 1

[[layers]]
name = "app"
paths = ["src/app/*"]
order = 2

[[boundaries]]
from = "src/app/*"
to = "src/core/internal/*"
reason = "App must not depend on core internals"
```

```bash
sentrux check .
# ❌ Violations found:
#   - src/app/main.py: Cyclomatic complexity 28.0 exceeds max 25
```

Or in CI:
```bash
sentrux check . && echo "Architecture check passed"
```

## Supported Languages

Python 3.9+. Analyzes Python projects using the Python `ast` module.

Can be extended to support additional languages using tree-sitter Python bindings.

## Philosophy

The human role is changing — from writing code to governing code.

sentrux is built on three beliefs:

**1. Human-in-the-loop is non-negotiable.** AI agents are powerful but limited. They cannot hold the big picture and small details at once. A human must see what the agent is doing to the whole — not just which file it touched, but what that means to architecture.

**2. Verification is more valuable than generation.** Generating a correct solution is harder than verifying one. You don't need to out-code the machine. You need to out-evaluate it — specify what "correct" looks like, recognize when the output misses, judge whether the direction is right.

**3. Good systems make good outcomes inevitable.** A well-designed system constrains behavior so that the right thing is the easy thing. A quality gate that blocks degradation. A rules engine that encodes architectural decisions. A sensor that makes structural rot impossible to ignore.

Once you have a feedback loop that works, you don't go back to doing it by hand.

---

<div align="center">

<sub>AI agents write code at machine speed. Without structural governance, codebases decay at machine speed too.<br><b>sentrux is the governor.</b></sub>

</div>

<div align="center">

[MIT License](LICENSE)

</div>
