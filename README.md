<h1 align="center">obsidian-second-brain-contabil: persistent memory for Claude Code and Codex, in an Obsidian vault</h1>

<p align="center">
  <em>A slimmed fork of <a href="https://github.com/eugeniughelbur/obsidian-second-brain">obsidian-second-brain</a> by Eugeniu Ghelbur (MIT), prepared for accounting offices. Everything that sends vault or conversation content to a third-party service was removed.</em>
</p>

<p align="center">
  <b>Your AI second brain for <a href="https://obsidian.md">Obsidian</a>. Free, open source, and plain Markdown you own.</b><br />
  Talk to Claude as usual. It saves what matters to your vault and remembers it next time.
</p>

<p align="center">
  <a href="#quick-start">Install</a> &middot;
  <a href="#see-it-work">See it work</a> &middot;
  <a href="#38-commands">All commands</a> &middot;
  <a href="#crew-one-logbook-for-all-your-agents">Crew</a> &middot;
  <a href="#faq">FAQ</a> &middot;
  <a href="CHANGELOG.md">Changelog</a>
</p>

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/Claude_Code-plugin-D97757?logo=anthropic&logoColor=white" alt="Claude Code plugin" /></a>
  <a href="#codex-cli--opencode"><img src="https://img.shields.io/badge/also-Codex_%C2%B7_OpenCode-555" alt="Also runs in Codex and OpenCode" /></a>
  <img src="https://img.shields.io/github/v/release/Mouraovicente/obsidian-second-brain-contabil?color=green" alt="Release" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT" />
  <img src="https://img.shields.io/github/stars/Mouraovicente/obsidian-second-brain-contabil?color=yellow" alt="Stars" />
</p>

**Claude forgets you when a chat ends. Your Obsidian vault doesn't.** This skill connects the two, so every chat adds to one set of linked notes that the next chat reads.

- **Save.** `/obsidian-save` turns a chat into linked notes: people, projects, decisions and tasks.
- **Feed it.** `/obsidian-ingest` takes a link, PDF, Word file, voice memo or screenshot. It updates the notes you already have instead of piling up new ones.
- **Find.** `/obsidian-find` answers from your own notes, with the context around each hit.
- **Push back.** `/obsidian-challenge` checks a plan against your past decisions.
- **Keep it tidy.** `/obsidian-health` and `/obsidian-reconcile` find contradictions and lonely notes. An optional background agent updates the vault after context compaction.

Your notes stay as Markdown files on your computer. No command needs an API key, and the scripts make no network calls by default.

## Quick start

Inside any Claude Code session, run:

```
/plugin marketplace add Mouraovicente/obsidian-second-brain-contabil
/plugin install obsidian-second-brain@obsidian-second-brain-contabil
```

Then tell Claude where your vault is. Add this to the `env` section of `~/.claude/settings.json`:

```json
"env": { "OBSIDIAN_VAULT_PATH": "/path/to/your/vault" }
```

Restart Claude Code and run `/obsidian-second-brain:obsidian-init` inside your vault. Start with three commands: `obsidian-init` to set up, `obsidian-save` to capture and `obsidian-find` to recall.

No vault yet, another AI tool, or bare command names? See the [full install guide](#install).

<p align="center">
  <strong>An evolution of <a href="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f">Karpathy's LLM Wiki pattern</a>: a vault that rewrites itself.</strong>
  <br />
  <em>Every source updates the pages you already have, not only adds new ones. <a href="#how-this-extends-karpathys-llm-wiki">How it differs &rarr;</a></em>
  <br /><br />
  <strong>Powered by <a href="references/freshness-policy.md">Open Knowledge Metabolism (OKM)</a>:</strong> <em>each fact is timeless, dated, or a pointer. Your notes never fill with facts that used to be true.</em>
</p>

---

## The Problem

You use Claude every day. Every session starts from scratch. You re-explain everything. The conversation ends. Everything disappears. Claude Code has no persistent memory across sessions - and neither does Codex or any of the other agents.

You take notes in Obsidian. Hundreds of files. They just sit there. You make the same decision twice because you forgot you made it six months ago. Ideas rot in daily notes. Nobody connects the dots.

**Two powerful tools. Completely disconnected.** You already have the long-term memory. The thing doing the thinking cannot reach it.

---

## How this extends Karpathy's LLM Wiki

Karpathy's pattern is brilliant. Drop sources, LLM creates wiki pages, ask questions. This skill takes it further:

| | Karpathy's LLM Wiki | obsidian-second-brain |
|---|---|---|
| **New sources** | Append new pages, cross-reference | **Rewrite existing pages.** People get updated, claims revised, stale facts replaced. |
| **Contradictions** | Flagged, you resolve manually | `/obsidian-reconcile` resolves them automatically |
| **Patterns** | Surface when you ask | `/obsidian-synthesize` finds unnamed patterns and writes synthesis pages on its own |
| **When it runs** | On demand, when you prompt | On demand, plus an optional background agent after each context compaction |
| **Note format** | Human-readable wiki pages | AI-first: `## For future agent` preamble + frontmatter for LLM retrieval, not human review |

If Karpathy's wiki is a knowledge base you maintain with an LLM, this is a knowledge base that maintains itself.

---

## What Happens When You Install This

**After a meeting:** `/obsidian-save`
Claude pulls out every decision, person, task, and idea and saves each one to the right note. You do nothing.

**You recorded a voice memo:** `/obsidian-ingest meeting.m4a`
Claude transcribes it with a local Whisper install, attributes speakers where the transcript makes them identifiable, extracts every promise and action item, and distributes across entity pages, task boards, and the daily note.

**You screenshot a whiteboard:** `/obsidian-ingest photo.png`
Claude reads the image, extracts text and structure, creates concept notes, links to related projects. A photo becomes knowledge.

**You have a finished text document:** `/obsidian-ingest report.docx`
Word (`.docx`, `.doc`) and OpenDocument (`.odt`) files uploaded or copied into the vault follow the same local-source rules as PDFs and Markdown. The helper converts a private copy to a temporary PDF, then ingestion uses the existing PDF path. Text and figures use that path; comments and revision markup are excluded. The original stays unchanged and remains the source under the existing provenance rules. Requires Python 3.10+ and [LibreOffice 26.2+](https://www.libreoffice.org/download/download-libreoffice/), installed separately. Run `python scripts/document_to_pdf.py "path/to/report.docx"`; it prints the PDF path. Put `soffice` on PATH or add `--soffice` with its executable path (Windows: `C:/Program Files/LibreOffice/program/soffice.com`; macOS: `/Applications/LibreOffice.app/Contents/MacOS/soffice`). Remove the generated PDF and its temporary parent folder after capture. No additional Python packages are needed. See [the ingest command](commands/obsidian-ingest.md). Presentation and spreadsheet formats remain outside scope.

**You find a great article:** `/obsidian-ingest https://example.com/article`
Claude doesn't summarize into one note. It REWRITES your existing pages. People get updated. Contradictions get resolved. Patterns trigger new synthesis pages. One URL in. The vault is smarter.

**Before a big decision:** `/obsidian-challenge`
Claude searches your vault for past failures and reversed decisions on the same topic. Pushes back with your own words. Your vault holds you accountable.

**You want to see the big picture:** `/obsidian-visualize`
Claude generates a visual canvas of your entire vault. Hub nodes centered, color-coded by type, orphans highlighted. Open it in Obsidian and see the shape of your knowledge.

**You start a new day:** `/obsidian-daily`
Claude pulls your overdue tasks and recent changes into today's note. Your morning starts informed.

**You never open Obsidian.** Everything happens through Claude.

---

## Before & After

| | Without this skill | With this skill |
|---|---|---|
| Saving decisions | Copy-paste or lose them | Auto-saved to the right project note |
| Daily notes | Write it yourself, forget half the time | Created automatically |
| Finding patterns | Re-read dozens of notes | `/obsidian-emerge` finds them for you |
| Challenging yourself | Nobody pushes back | `/obsidian-challenge` uses your own history against you |
| Session continuity | Re-explain every time | `/obsidian-world` loads full context in 10 seconds |
| Ingesting content | Read it, forget it | `/obsidian-ingest` rewrites 5-15 vault pages from 1 source (web articles, PDFs, Word/OpenDocument text files, audio, screenshots) |
| Contradictions | You don't know they exist | `/obsidian-reconcile` resolves them automatically |
| Synthesis | You connect dots manually | `/obsidian-synthesize` finds patterns across sources on its own |
| Sharing vault data | Only Claude can read it | `/obsidian-export` gives any AI tool a clean snapshot |
| Facts change over time | Old info gets overwritten | Bi-temporal facts track when it was true AND when the vault learned it |
| Starting a new session | Re-explain who you are | `CRITICAL_FACTS.md` loads your identity in ~120 tokens |
| Vault notes for future agent | Notes for human reading | AI-first rule: every note has "For future agent" preamble + recency markers + citations |

## Crew: one logbook for all your agents

**Crew works without Obsidian.** Claude Code, Codex, Cursor, and Grok Bot share job records in any plain folder.
Each agent sees what the others finished and can leave a lesson for review.

- Grok Bot joins the same team through its existing runner.
- A lesson becomes a rule only when a human runs `keep`.
- Crew runs no background loop.

```bash
curl -fsSL https://raw.githubusercontent.com/Mouraovicente/obsidian-second-brain-contabil/main/scripts/quick-install.sh | bash
```

Restart Claude Code, then type `/crew setup`. Pick `~/crew` or `wiki/team/` inside your Obsidian vault.
Codex users run `/hooks` once to trust Crew's hooks. Setup prints a Grok Bot profile block to paste.

```text
18:40 | codex | brand | Astra pass, 0 errors
```

[Setup, exact commands, and limits](references/crew.md). Python 3.10 or later; no extra packages for Crew.
Shared agent memory isn't new. What Crew adds is the three parts above.

## More from the author

*The product is above. This is where it came from and where it goes next.*

<p align="center">
  <strong>From the blog</strong> &middot; <a href="https://theaioperator.io/?utm_source=github&utm_medium=readme&utm_campaign=blog-section">The AI Operator &rarr;</a>
</p>

<p align="center">
  <strong>Deep dive:</strong> <a href="https://theaioperator.io/p/i-rebuilt-karpathys-llm-wiki-heres">"I rebuilt Karpathy's LLM Wiki. Here's what's missing from the original."</a><br />
  <em>Why append-only breaks at scale &middot; the AI-First Vault Principle &middot; three bugs in v1</em>
</p>

<p align="center">
  <strong>Origin story:</strong> <a href="https://theaioperator.io/p/i-built-this-for-myself-then-1374">"I built this for myself. Then 1,374 strangers cloned it."</a><br />
  <em>Two disconnected tools &middot; the institutional-amnesia problem &middot; 1,000+ stars in 7 weeks</em>
</p>

<p align="center">
  <em>Two posts a week, Tuesday and Thursday, on Obsidian + AI workflows and bringing AI into real work.</em>
</p>

<p align="center">
  Built by <a href="https://github.com/eugeniughelbur"><strong>Eugeniu Ghelbur</strong></a> &middot; AI Automation Engineer, AI Tooling Engineer, AI Educator<br />
  <em>building in public &middot; sharing what works</em>
</p>

<div align="center">

<table>
<tr>
<td align="center" width="700">

### Follow along

*Two posts a week on AI second-brain systems, vault patterns, and what works in practice.*

<a href="https://x.com/eugeniu_ghelbur"><img src="https://img.shields.io/badge/Follow_on_X-000?style=for-the-badge&logo=x&logoColor=white" alt="Follow on X" /></a>
<a href="https://www.linkedin.com/in/eugeniu-ghelbur/"><img src="https://img.shields.io/badge/Connect_on_LinkedIn-0A66C2?style=for-the-badge&logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0yMC40NDcgMjAuNDUyaC0zLjU1NHYtNS41NjljMC0xLjMyOC0uMDI3LTMuMDM3LTEuODUyLTMuMDM3LTEuODUzIDAtMi4xMzYgMS40NDUtMi4xMzYgMi45Mzl2NS42NjdIOS4zNTFWOWgzLjQxNHYxLjU2MWguMDQ2Yy40NzctLjkgMS42MzctMS44NSAzLjM3LTEuODUgMy42MDEgMCA0LjI2NyAyLjM3IDQuMjY3IDUuNDU1djYuMjg2ek01LjMzNyA3LjQzM2MtMS4xNDQgMC0yLjA2My0uOTI2LTIuMDYzLTIuMDY1IDAtMS4xMzguOTItMi4wNjMgMi4wNjMtMi4wNjMgMS4xNCAwIDIuMDY0LjkyNSAyLjA2NCAyLjA2MyAwIDEuMTM5LS45MjUgMi4wNjUtMi4wNjQgMi4wNjV6bTEuNzgyIDEzLjAxOUgzLjU1NVY5aDMuNTY0djExLjQ1MnpNMjIuMjI1IDBIMS43NzFDLjc5MiAwIDAgLjc3NCAwIDEuNzI5djIwLjU0MkMwIDIzLjIyNy43OTIgMjQgMS43NzEgMjRoMjAuNDUxQzIzLjIgMjQgMjQgMjMuMjI3IDI0IDIyLjI3MVYxLjcyOUMyNCAuNzc0IDIzLjIgMCAyMi4yMjIgMGguMDAzeiIvPjwvc3ZnPg%3D%3D" alt="Connect on LinkedIn" /></a>
<a href="https://theaioperator.io/subscribe?utm_source=github&utm_medium=readme&utm_campaign=middle-badge"><img src="https://img.shields.io/badge/Subscribe_on_Substack-FF6719?style=for-the-badge&logo=substack&logoColor=white" alt="Subscribe on Substack" /></a>
<a href="https://github.com/eugeniughelbur"><img src="https://img.shields.io/badge/Follow_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="Follow on GitHub" /></a>

</td>
</tr>
</table>

</div>

---


---

## How It Works

```
  +------------------------------------------+
  |                                          |
  |   LAYER 1: Operations (28 commands)      |
  |   Claude remembers everything            |
  |                                          |
  +------------------------------------------+
  |                                          |
  |   LAYER 2: Thinking Tools (9 commands)   |
  |   Claude thinks with you                 |
  |                                          |
  +------------------------------------------+
  |                                          |
  |   LAYER 3: Context Engine (1 command)    |
  |   Claude knows who you are               |
  |                                          |
  +------------------------------------------+
  |                                          |
  |   ALWAYS ON                              |
  |   Optional background agent              |
  |   Auto-synthesis + save reminders        |
  |                                          |
  +------------------------------------------+
```

38 commands total.

**Layer 1** saves, organizes, ingests, reconciles, exports, and maintains your vault.
**Layer 2** challenges your ideas, surfaces hidden patterns, bridges unrelated domains, and graduates ideas into projects.
**Layer 3** loads your identity and current state so every session picks up where the last one ended.
**Always On** keeps the vault alive without you lifting a finger.

---

## 38 Commands

### Operations -- Claude remembers

| Command | What it does |
|---|---|
| `/obsidian-save` | Saves everything from the conversation -- decisions, tasks, people, ideas |
| `/obsidian-ingest` | Ingest a URL, file, or resumable folder batch (text, PDFs, `.docx`/`.doc`/`.odt` via LibreOffice, audio, images). The vault REWRITES itself. 5-15 pages touched per source. |
| `/obsidian-synthesize` | Auto-finds patterns across sources and writes synthesis pages |
| `/obsidian-reconcile` | Finds contradictions and resolves them. The vault maintains its own truth. |
| `/obsidian-checkin` | Asks you whether old people and project notes still hold. Shows what each says, re-asks until you answer, saves the news. |
| `/obsidian-export` | Clean JSON/markdown snapshot any AI tool can read |
| `/obsidian-daily` | Creates or updates today's daily note |
| `/obsidian-recurring` | Tracks a recurring obligation with a cadence and a computed next-due date |
| `/obsidian-log` | Logs a work session, links it everywhere |
| `/obsidian-task` | Adds task to the right board with priority and due date |
| `/obsidian-person` | Creates or updates a person note |
| `/obsidian-capture` | Zero-friction idea capture |
| `/obsidian-find` | Smart search with context |
| `/obsidian-recap` | Summary of a day, week, or month |
| `/obsidian-review` | Structured weekly or monthly review |
| `/obsidian-board` | Kanban board view and updates |
| `/obsidian-board-hygiene` | Bulk-triage a board -- surface stale/overdue items, then archive / reschedule / mark-Done in one pass |
| `/obsidian-project` | Project note with board and daily links |
| `/obsidian-health` | Vault audit -- contradictions, gaps, stale claims, orphans, freshness violations (the [freshness policy](references/freshness-policy.md): every fact timeless, dated, or a pointer), typed-edge lint (unknown types, dangling targets, contradiction cycles in the `relations:` graph), and a tag taxonomy audit ([opt-in](references/taxonomy-format.md) via `_meta/taxonomy.md`) |
| `/obsidian-merge` | Merge two near-duplicate notes from `/obsidian-health` into one -- dry run by default, frontmatter union, retired note becomes a redirect (never deleted) |
| `/obsidian-reindex` | Refreshes the incremental semantic index and reports coverage before and after, with clear embedding-backend failures |
| `/obsidian-retrieval-eval` | Measures vault search quality -- recall@k + MRR on natural-language questions, with the concrete failures and ranked fixes |
| `/obsidian-decide [--formal]` | Logs decisions to the right project notes; `--formal` writes a full ADR record (the vault knows why it's structured this way) |
| `/obsidian-visualize` | Generates a visual canvas map of your second brain |
| `/obsidian-learn` | Reviews vault learnings, prunes stale ones, surfaces patterns to promote into rules |
| `/obsidian-init` | Generates `_CLAUDE.md`, `index.md`, `log.md` |
| `/crew setup` | Shared job log and lessons with a human keep decision; works without Obsidian |
| `/create-command` | Interview flow that scaffolds a new command into `commands/<name>.md`, no markdown editing |

### Thinking -- Claude thinks with you

| Command | What it does |
|---|---|
| `/obsidian-brainstorm [topic]` | Multi-turn Socratic interview - one question per turn until the idea converges, then a design note with named alternatives |
| `/obsidian-challenge` | Your vault argues against your idea using your own history |
| `/obsidian-panel` | Convenes a panel of distinct perspectives on a decision, one verdict each + synthesis |
| `/obsidian-emerge` | Surfaces patterns from 30 days of notes you never named |
| `/obsidian-connect [A] [B]` | Bridges two unrelated domains to spark new ideas |
| `/vault-deep-synthesis [topic]` | Cross-references every note on a topic: agreements, contradictions, stale claims, gaps |
| `/obsidian-distill [note or source]` | Condenses a long note/source into key claims, each tagged with provenance back to the exact source block |
| `/idea-discovery` | Ranks 3-5 next-direction candidates from ideas, open questions, and orphan research |
| `/obsidian-graduate` | Turns an idea fragment into a full project with tasks |

### Context -- Claude knows you

| Command | What it does |
|---|---|
| `/obsidian-world` | Loads identity + state with progressive token budgets (L0-L3) |

<details>
<summary><strong>See the thinking tools in action</strong></summary>

<br />

**`/obsidian-challenge`**

You: *"I want to rewrite the API in Rust."*

Claude finds your 2025 post-mortem where the Rust rewrite failed. Finds your decision log committing to TypeScript for 2 years. Says: *"Your own notes say this failed. Still want to proceed?"*

---

**`/obsidian-emerge`**

Claude scans 30 daily notes. You mentioned "onboarding friction" in 4 unrelated projects.

*"Onboarding is your bottleneck across projects. You never named it."*

---

**`/obsidian-connect "distributed systems" "cooking"`**

Traces both clusters in your link graph. Finds shared concepts: preparation and load distribution. Generates 3 actionable ideas at the intersection.

---

**`/obsidian-graduate`**

An idea from 3 weeks ago. Claude reads it, finds related projects and people, generates a full spec with goals, phases, tasks, and board entries. The idea gets tagged `graduated`.

</details>

<details>
<summary><strong>See /obsidian-ingest in action</strong></summary>

<br />

```
/obsidian-ingest https://example.com/article
```

1. Saves original to `raw/articles/` (immutable)
2. REWRITES entity pages with new context
3. REWRITES concept pages if the source adds depth or contradicts them
4. Creates synthesis pages when patterns emerge
5. Resolves contradictions and documents why
6. Updates `index.md`, `log.md`, daily note

**One source in. The vault rewrites itself.**

</details>

---

## The Vault is Alive

Traditional vaults are filing cabinets. You put things in. They sit there.

This vault rewrites itself with every input:

- **Ingest a source** -- existing pages get rewritten, contradictions resolved, patterns synthesized
- **Save a conversation** -- entities, concepts, and decisions distribute across the vault
- **Ask a question** -- the Two-Output Rule means every answer also updates pages
- **A fact changes** -- bi-temporal facts track when it was true AND when the vault learned it. "You believed X on Tuesday. After ingesting Y on Wednesday, you shifted to Z." Full audit trail.
- **Do nothing** -- the optional background agent keeps notes current after each context compaction
- **Wait a week** -- auto-synthesis finds cross-source patterns and writes connection pages

The vault after a week is fundamentally different from the vault you started with.

**The maintenance layer has a name: OKM (Open Knowledge Metabolism).** Storage is the easy half; keeping stored knowledge *true* is the hard half, and it is where this project spends its effort. OKM is the open spec behind that: **every stored fact must be timeless, dated, or a pointer.** Slow-changing knowledge (how things work, decisions, ownership) is stored; fast-changing facts (counts, statuses, balances) are linked to where they live with an `as of` stamp, never copied in to rot. The rule is a one-page spec ([references/freshness-policy.md](references/freshness-policy.md)), enforced by a linter ([scripts/freshness_lint.py](scripts/freshness_lint.py)) that `/obsidian-health` runs. It is the companion to OKF (Google's Open Knowledge Format), and the division is sharper than format-versus-freshness: OKF v0.2 added fields for recording that something went stale (`status`, `stale_after`, `verified`), but a field cannot stop a note claiming "the pipeline has 13 deals" with no stamp on it. OKM is the *rule* about what may be stored bare at all, and a linter that fails the build when it is not. One spec, one reference linter, no second implementation yet. It is storage-agnostic: any folder of markdown an AI maintains, not just Obsidian vaults.

---

## Choose Your Preset

Pick your role at bootstrap. Each preset creates tailored folder structures, templates, and kanban boards.

| Preset | Who it's for | Kanban style |
|---|---|---|
| **executive** | Founders, operators, managers | OKRs / Quarterly / Weekly |
| **builder** | Developers, engineers, architects | Backlog / Sprint / Done |
| **creator** | Writers, marketers | Ideas / Drafts / Published |
| **researcher** | Academics, analysts, deep-divers | Reading / Processing / Synthesized |
| **contabil** | Accounting offices (notes in Brazilian Portuguese) | A fazer / Em andamento / Aguardando / Feito |

```bash
uv run python scripts/bootstrap_vault.py --path ~/my-vault --name "Your Name" --preset builder
```

No preset? You get a general-purpose vault that works for everyone.

Every preset builds the Obsidian-style layout (`Daily/`, `People/`, `Projects/`, ...). Add `--style wiki` for the wiki-style layout described under [Vault Architecture](#vault-architecture):

```bash
uv run python scripts/bootstrap_vault.py --path ~/my-vault --name "Your Name" --preset builder --style wiki
```

---

## Background Agent

**Background:** fires after every context compaction. You keep working. The vault updates itself.

```
PostCompact -> obsidian-bg-agent.sh -> claude -p (headless) -> vault updated
```

**What arming it costs.** The headless run uses `--dangerously-skip-permissions`, because nobody is there to approve each write. That is why the agent ships inert and stays opt-in. Its tool surface is restricted with `--tools "Read,Write,Edit,Glob,Grep"` (the flag that removes every other built-in tool, not just pre-approves these) and no MCP servers are loaded, so it cannot run shell commands or reach the network, and it only adds and updates - it never deletes or merges. If that trade is not one you want, leave it off; every other command works without it.

**Save reminders:** Claude nudges you to `/obsidian-save` after 10+ exchanges or when you say "done" or "thanks". No lost conversations.

**Bounded recall (opt-in):** on every prompt, a `UserPromptSubmit` hook injects a small brief of the most relevant vault notes - max 4 notes, ~900 chars - or **nothing at all** when confidence is low (abstention beats noise). Read-only, fail-closed, and every inject/abstain decision is logged to `<vault>/.claude-runs/` for audit. Ships inert; arm it with `OBSIDIAN_RECALL_ENABLED=1` per [hooks/recall.hook.example.json](hooks/recall.hook.example.json).

---

## Vault Architecture

**Starting with personal notes?** `/obsidian-init` offers an optional [First-Brain wiki-style variant](references/vault-schema.md#first-brain-wiki-style-variant) for an existing, evolving collection of human notes. Human notes live in the `First-Brain/` folder, immutable ingestion captures in `raw/`, and AI-maintained knowledge in `wiki/`. Initialization ensures the `First-Brain/` source folder exists and configures ownership and routing; it does not move or ingest notes. Then use `/obsidian-ingest` on an individual First Brain file or the collection. Original notes stay in place under instruction-based protection, not a filesystem sandbox. See [the initialization command](commands/obsidian-init.md) for the full procedure.

**Importing a collection?** `/obsidian-ingest Sources/ --preview` discovers eligible text files, PDFs, audio, and images without reading source bodies or writing progress. `/obsidian-ingest Sources/ --batch-size 10` processes up to ten sources sequentially through the existing ingestion workflow. Repeat the same command for the next batch or after an interrupted session has stopped; completed unchanged sources are skipped, and unfinished sources reuse their raw captures. Sensitive-content rules and rewrite approvals still apply. Required pending or declined approvals never count as completion.

Progress uses one hidden completion comment per processed source version in existing `Logs/YYYY-MM-DD.md` files, or legacy `log.md`; there is no separate state file or additional readable status line. The comment contains the source path, byte hash, raw reference, and timestamp. Each source finishes its catalog, daily-note, and normal log updates before the comment is written. Unfinished work has no completion comment and is retried on the next run; errors and pending approvals appear in the normal report. Removing completion history requires reprocessing, with raw deduplication retained. Run only one folder ingestion per vault at a time; this minimal helper does not track active sessions, enforce locking, or validate semantic extraction quality. See [the ingestion procedure](commands/obsidian-ingest.md#directory-ingestion) for supported extensions, provenance hashes, custom routing, and recovery. First Brain warm start is simply `/obsidian-ingest First-Brain/`; other layouts and source collections use the same workflow. Binary originals remain untouched; captures retain existing transcripts, PDF extracts, or image descriptions rather than archive binaries.

Two layouts are supported. `scripts/bootstrap_vault.py` builds the Obsidian-style layout by default: `Daily/`, `People/`, `Projects/` and the preset's topic folders such as `Goals/` and `Mentions/`, as laid out in [references/vault-schema.md](references/vault-schema.md). Pass `--style wiki` for the wiki-style layout below. A preset folder the wiki layout renames moves to that name (`People/` to `wiki/entities/`, `Ideas/` and `Knowledge/` to `wiki/concepts/`); one it does not rename keeps its own name under `wiki/` (`Goals/` to `wiki/goals/`, `Sources/` to `wiki/sources/`), so a preset builds the same vault in either layout.

### Wiki-style -- LLM-first

Claude is the reader and writer. The vault is a database.

```
vault/
+-- _CLAUDE.md          # Operating manual
+-- index.md            # Page catalog (Claude reads FIRST)
+-- log.md              # Activity timeline
+-- SOUL.md             # Your identity
+-- CRITICAL_FACTS.md   # ~120 tokens, always loaded (timezone, manager, location)
+-- raw/                # IMMUTABLE source material
+-- wiki/               # Claude's workspace
|   +-- entities/       # People, companies, tools
|   +-- concepts/       # Ideas, frameworks, synthesis
|   +-- projects/       # Project notes
|   +-- daily/          # Daily notes
|   +-- logs/           # Work session logs
|   +-- reviews/        # Weekly/monthly reviews
|   +-- tasks/          # Task notes
|   +-- decisions/      # ADRs
+-- boards/             # Kanban boards
+-- templates/          # Note templates
```

---

## Install

> **One codebase, four builds.** Pick yours below. The vault behavior is identical across all of them; only the install path and the dispatcher file (`CLAUDE.md` / `AGENTS.md` / `.agents/skills/`) differ.

Rather than ask you to take that on faith, here is what each build currently passes:

<!-- conformance:start -->
| Build | Emits a real tree | Script paths resolved | Docs reachable | Toolkit runnable |
|---|---|---|---|---|
| Agent Skills | pass | pass | pass | pass |
| Claude Code | pass | pass | pass | pass |
| Codex CLI | pass | pass | pass | pass |
| OpenCode | pass | pass | pass | pass |

*Generated by `scripts/conformance_report.py`, verified in CI on every push. Each build is compiled from the same source tree, then checked for a non-empty output, a resolved script root, reference paths that actually exist in that build, and a Python project shipped beside the scripts. A red cell here is a real red cell, not a missing test.*
<!-- conformance:end -->



**Prerequisites:** [Claude Code](https://claude.com/claude-code) (or one of the other platforms below), `git`, and [`uv`](https://docs.astral.sh/uv/) for the Python helpers (health check, bootstrap). `jq` is **required for the classic script install** - `scripts/setup.sh` uses it to edit `~/.claude/settings.json` safely and exits if it is missing. Not needed on the plugin path. Optional: [Ollama](https://ollama.com) for local semantic search, `openai-whisper` (installed on first audio ingest, pulls in PyTorch). No API keys needed for the core vault commands.

### Crew only (no vault)

Want the shared logbook without Obsidian? Run the quick install above, restart Claude Code, and type `/crew setup`. Pick a plain folder such as `~/crew`. Or run the helper directly:

```bash
python3 ~/.claude/skills/obsidian-second-brain/scripts/crew.py --dir ~/crew setup
```

Codex users then run `/hooks` once to trust the hooks. Restart Cursor after setup. Full guide: [references/crew.md](references/crew.md).

### Claude Code (default)

**Native plugin install (recommended).** Inside any Claude Code session:

```
/plugin marketplace add Mouraovicente/obsidian-second-brain-contabil
/plugin install obsidian-second-brain@obsidian-second-brain-contabil
```

That ships all 38 commands, the skill manual, the session-context hook, the opt-in background agent (inert until you arm it - see [hooks/postcompact.hook.example.json](hooks/postcompact.hook.example.json)), and the vault MCP server. Then tell Claude where your vault lives by adding to the `env` section of `~/.claude/settings.json`:

```json
"env": { "OBSIDIAN_VAULT_PATH": "/path/to/your/vault" }
```

Restart Claude Code, then run `/obsidian-second-brain:obsidian-init` inside your vault. Plugin commands are namespaced, so every command is `/obsidian-second-brain:<name>` (type `/obsidian-second-brain:` to see all 38). Update later with `/plugin update obsidian-second-brain`.

**Classic install (script).** Use this if you want the commands as bare names (`/obsidian-init`, `/obsidian-save`, ...) or you are developing the skill and want live edits. One line (clones the skill, installs the slash commands, and registers the session-context hook):

```bash
curl -fsSL https://raw.githubusercontent.com/Mouraovicente/obsidian-second-brain-contabil/main/scripts/quick-install.sh | bash
```

Or step by step:

```bash
git clone https://github.com/Mouraovicente/obsidian-second-brain-contabil ~/.claude/skills/obsidian-second-brain
bash ~/.claude/skills/obsidian-second-brain/install.sh
bash ~/.claude/skills/obsidian-second-brain/scripts/setup.sh "/path/to/your/vault"
```

**No vault yet?** Create a ready-to-use one first (folders, templates, boards, dashboards - passes its own health check out of the box):

```bash
cd ~/.claude/skills/obsidian-second-brain
uv run python scripts/bootstrap_vault.py --path ~/Documents/MyVault --name "Your Name"
bash scripts/setup.sh ~/Documents/MyVault
```

Then open Claude Code and run `/obsidian-init` inside your vault.

### Codex CLI / OpenCode

> **Codex and OpenCode users: prefer the [Agent Skills build](#google-antigravity-and-any-agentsskills-harness) below.** The standalone `codex-cli` and `opencode` builds are deprecated and superseded by it; both print that notice in their own `INSTALL.md`. They still work, and will until they are removed.

```bash
git clone https://github.com/Mouraovicente/obsidian-second-brain-contabil
cd obsidian-second-brain
bash scripts/build.sh --platform codex-cli   # or opencode
cp -R dist/codex-cli/. /path/to/your/vault/   # or dist/opencode/.
```

Then start your CLI from the vault root.

The **Codex build emits native [Codex Agent Skills](https://developers.openai.com/codex/skills)**: one skill per command under `.agents/skills/<name>/SKILL.md`. Codex discovers them automatically with progressive disclosure (only each skill's name + description load until it's selected), and they run **in your current session** - invoke one with `$<name>`, pick it from `/skills`, or just describe the task and let Codex match it implicitly. `AGENTS.md` stays as a thin always-on manual (vault conventions + the AI-first rule); there is no routing table to maintain because the skill list is the router. The OpenCode build still emits an `AGENTS.md` dispatcher with an auto-generated routing table to command files under `.opencode/`.

Run `bash scripts/build.sh` with no arguments to build every platform at once. See [`dist/<platform>/INSTALL.md`](scripts/build.sh) after building for platform-specific notes.

### Google Antigravity (and any `.agents/skills/` harness)

Antigravity, Codex CLI, OpenCode, and GitHub Copilot CLI have all converged on the open [Agent Skills](https://github.com/vercel-labs/skills) standard: workspace skills at `.agents/skills/<name>/SKILL.md`. The `agent-skills` build emits one spec-compliant tree they all read - and any future harness on the same standard works with zero repo changes.

```bash
git clone https://github.com/Mouraovicente/obsidian-second-brain-contabil
cd obsidian-second-brain
bash scripts/build.sh --platform agent-skills

# install with skills.sh (writes one shared .agents/skills/ tree), from your vault root:
npx skills add /path/to/obsidian-second-brain/dist/agent-skills -a antigravity -a codex -a opencode
# or copy manually, no skills.sh required:
cp -R dist/agent-skills/skills/. /path/to/your/vault/.agents/skills/
```

Each command becomes a skill under `.agents/skills/`; a shared `obsidian-core` skill carries the Python toolkit and the AI-first write spec the others call into. The skills are self-sufficient (they resolve the vault root from `$OBSIDIAN_VAULT_PATH` or the working directory and embed the write spec), so they need no session-start hook. This is the recommended path for **Google Antigravity**, which only detects active skills under `.agents/skills/`. See [`dist/agent-skills/INSTALL.md`](scripts/build.sh) for the full story (skills.sh, manual copy, per-harness notes, and the optional always-on vault-routing rule).

### Local settings (optional)

Nothing needs a settings file: `OBSIDIAN_VAULT_PATH` in the `env` block of `~/.claude/settings.json` is enough. If you want one, `.env.example` lists the few knobs (vault path, validator checks, semantic search). Copy it to `~/.config/obsidian-second-brain/.env` (on Windows `%USERPROFILE%\.config\obsidian-second-brain\.env`) and `chmod 600` it. `OBSIDIAN_ENV_FILE` points every reader (the scripts, the MCP server, the write-time hook, `install.sh`, `scripts/setup.sh`) at another path; on Windows give it a native path such as `C:/Users/me/osb.env`.

### Semantic search (optional, off by default)

Search (`/obsidian-find` and the MCP connector) works out of the box as fast keyword search - **no setup, no model, nothing to install.** You can optionally add a meaning-based layer that finds notes even when your query shares no words with them. It is opt-in by setup and, when present, leads the ranking with keyword search as tiebreak and freshness signals on top (measured on a ~2,350-note vault: keyword recall@10 1.0, paraphrased-question recall@10 77%, and non-English queries went from 13% to 63% recall@5, a 5x gain, with the multilingual default model - full reference in scripts/eval/BASELINE.md). If the model is ever unreachable, search silently falls back to keyword - it never breaks or hangs.

Two ways to provide the embedding model:

- **Local + private (recommended), via [Ollama](https://ollama.com):** install Ollama, `ollama pull bge-m3`, then build the index: `uv run python scripts/eval/semantic_search.py --path "<vault>" --build`. Your notes never leave the machine. Re-run it as you write - see below.
- **No Ollama? Any OpenAI-compatible endpoint.** Set `OBSIDIAN_EMBED_BACKEND=openai`, `OBSIDIAN_EMBED_URL=<base url>`, `OBSIDIAN_EMBED_MODEL=<model>`, and `OBSIDIAN_EMBED_KEY=<key if needed>`. This covers other local runtimes (LM Studio, llama.cpp's server) for free/private use, **or** a cloud API (OpenAI, a gateway) for top quality - note a cloud endpoint means note text leaves your machine, so use `OBSIDIAN_EMBED_EXCLUDE=<folder prefixes>` to keep private folders local-only.

**Keep it current.** The index does not update itself, and a note that is not in it can only be found by literal word match - which on a query in another language means it cannot be found at all. Re-run `--build` regularly; it is incremental, so only new and changed notes re-embed. `/obsidian-health` reports coverage, and search warns on stderr once the index falls more than 5% behind (tune with `OBSIDIAN_INDEX_STALE_WARN_PCT`).

Knobs: `OBSIDIAN_SEARCH_SEMANTIC=0` disables the layer entirely. `OBSIDIAN_EMBED_MAX_CHUNKS=<n>` raises the per-note embedding cap from the default 8 chunks (~9,600 characters); a long-form vault of research dossiers or book-length notes embeds more of each note at the cost of a slower build, and text past the cap is not embedded. A value below 1 or one that is not a number falls back to 8 and says so on stderr, because the cap is applied as a slice: `0` would embed nothing and drop the note from the index. `OBSIDIAN_RRF_LEX_DEPTH=<n>` caps how many lexical results get a vote in the hybrid fusion (default 25, which caps nothing); lower it to 5-10 when a tail of term-frequency matches pushes an exact match out of the top results (#262). The index file is large and regenerable - gitignore it.

---

## FAQ

### Can I search without an agent?
Run `uv run python scripts/vault_search.py "query" --limit 6 --lexical` for a JSON result array.
The script uses `OBSIDIAN_VAULT_PATH` from the environment or toolkit config; omit `--lexical` to follow the existing semantic-search environment setting.

### Codex vs Claude Code: do I have to pick one?
No. Crew lets Claude Code, Codex and Cursor work as one team. After every job, each agent writes one line to a shared logbook, and the others read it before they answer. Run `/crew setup` once. See [Crew](#crew-one-logbook-for-all-your-agents).

### How do Claude Code, Codex and Cursor share memory?
Through Crew's logbook: plain markdown files in `~/crew` or in `wiki/team/` inside your vault. Claude Code and Codex read new lines through their `SessionStart` and `UserPromptSubmit` hooks. Cursor reads through `sessionStart` and `postToolUse`.

### Does Crew need Obsidian?
No. Crew is one standard-library Python file and a folder of markdown files. Point it at `~/crew` and it never touches a vault. Pick a vault only if you want the log next to your notes.

### Can a log line give my agent orders?
Every read starts with a header that says the lines are records, not instructions, and each field is cleaned to one line. That framing helps a model separate data from orders; it can't guarantee it. Crew runs no background loop, so nothing acts on a line by itself. A lesson changes an agent's rules only after you run `keep`.

### What is a Claude Code skill?
A Claude Code skill is a reusable behavior package for Anthropic's Claude Code CLI. It bundles slash commands, scripts, references, and operating instructions that Claude loads automatically. Skills give Claude domain expertise without prompt-engineering each session.

### Is this an Obsidian plugin or a Claude Code skill?
This is a Claude Code skill, not an Obsidian plugin. An Obsidian plugin lives inside Obsidian and adds UI features there. A Claude Code skill lives inside Claude Code (Anthropic's terminal AI coding agent) and gives Claude the ability to read, write, and reason over your Obsidian vault from outside Obsidian. You install this skill into Claude Code, not into Obsidian. Your vault is unchanged, just better-leveraged.

### What's the difference between an Obsidian Claude Code skill and a regular Obsidian plugin?
An Obsidian plugin runs inside Obsidian and is written in TypeScript against Obsidian's plugin API. A Claude Code skill for Obsidian runs inside Claude Code and is written as a set of markdown command files plus optional Python scripts. Plugins are constrained to what Obsidian's API exposes. Skills are constrained only by what Claude can do in your shell, which is why this skill can do things plugins can't: run an opt-in background agent that updates your vault, and synthesize knowledge across years of notes using Anthropic's Claude.

### How do I add this Obsidian Claude skill to Claude Code?
Run the one-line installer from the [Install](#install) section above. It clones the repo to `~/.claude/skills/obsidian-second-brain` and symlinks the slash commands into `~/.claude/commands/` so Claude Code picks them up automatically. Restart Claude Code after install. The skill loads on every session that touches an Obsidian vault.

### Does this work with Codex CLI or OpenCode?
Yes. The repo ships a build script that compiles the platform-neutral source into four outputs: Claude Code (slash commands + `CLAUDE.md`), Codex CLI (native Agent Skills), OpenCode (`AGENTS.md` + `.opencode/commands/`), and a unified Agent Skills build (one `.agents/skills/` tree for Antigravity / Codex / OpenCode and any other Agent Skills harness). Run `bash scripts/build.sh --platform codex-cli` (or another platform name), then copy the resulting `dist/<platform>/` tree into your vault.

### Does this work with Obsidian Sync?
Yes. The skill writes to your vault as standard markdown files. Obsidian Sync, iCloud, Syncthing, and Git-based sync all work without modification.

### Can I use it in a language other than English?
Yes. For the `contabil` preset the default is notes in Brazilian Portuguese: the vault's `_CLAUDE.md` declares the language and the agent writes in it without translating. For any other vault, you can still keep the vault in English: talk to your agent in your own language, and the agent translates what you say before it writes a note, replies in your language, and searches with English queries (the tested path, since search quality is measured on English notes). Put that rule in `<vault>/.claude/CLAUDE.md`, not `_CLAUDE.md`, so an `/obsidian-init` re-run keeps it. Notes in Chinese, Japanese or Korean, command phrases in five languages, and encoding: see [LANGUAGES.md](LANGUAGES.md).

### Do I need API keys to use this?
No. None of the 38 commands needs an API key, and the scripts make no network calls by default. The one optional exception is semantic search: the default backend is Ollama on your own machine, and the `openai` backend sends note text to whatever endpoint you configure.

### How is this different from Notion AI or Mem?
Notion AI and Mem are closed-source SaaS products that own your data. This skill stores everything as plain markdown in your local Obsidian vault, with no vendor lock-in. The AI is on top of your data, not behind it. You can switch tools or stop using the skill at any point and still have your full vault.

### What is the AI-first vault rule?
The principle that vault notes are written for future agent to retrieve and reason over, not for human reading. Notes have machine-readable structure, recency markers per claim, mandatory `[[wikilinks]]`, source URLs preserved verbatim, and confidence levels. See [`references/ai-first-rules.md`](references/ai-first-rules.md) for the full specification with frontmatter schemas per note type.

### Is this safe to run on my existing vault?
Yes. The skill never deletes or modifies notes destructively without explicit confirmation. Existing notes stay as-is. New notes follow the AI-first rule. `/obsidian-health` flags pre-AI-first notes so you can update them on your own schedule.

### What is OKM (Open Knowledge Metabolism)?
The maintenance layer, given a name. Its one rule: every stored fact must be timeless, dated, or a pointer - so a knowledge folder can never quietly fill with facts that used to be true. Slow knowledge is stored; fast facts are linked to their live source with an `as of` stamp instead of copied in. It ships as a one-page spec ([`references/freshness-policy.md`](references/freshness-policy.md)) and a stdlib-only linter ([`scripts/freshness_lint.py`](scripts/freshness_lint.py)) that `/obsidian-health` runs, and it is storage-agnostic (any markdown folder an AI maintains). Think of it as the companion to OKF (Open Knowledge Format). OKF v0.2 gives you fields for recording staleness (`status`, `stale_after`, `verified`); OKM is the rule about what may be stored bare in the first place, plus the linter that fails the build when it is not.

### Can I use this on Windows or Linux?
Yes. Windows users: follow [WINDOWS.md](WINDOWS.md), one page with the setup steps and fixes for the traps earlier users hit. The core vault commands work anywhere Claude Code runs. `install.sh` supports Linux, macOS, and Windows (MSYS2/Git Bash): on Linux/macOS slash commands are symlinked so `git pull` keeps them current; on Windows they are copied and `update.sh` refreshes them. On Windows the config file and Claude Code state hang off `%USERPROFILE%` (see Local settings); `OBSIDIAN_ENV_FILE` relocates the config file.

### Can I have a separate vault per project (multi-repo workflows)?
Yes. The default `scripts/setup.sh` writes `OBSIDIAN_VAULT_PATH` globally to `~/.claude/settings.json`, but every hook in this skill reads that env var at fire-time. Claude Code merges per-project `.claude/settings.json` on top of the global one, so you can put `{"env": {"OBSIDIAN_VAULT_PATH": "/path/to/repo-vault"}}` in each repo's `.claude/settings.json` and Claude will use that repo's vault whenever you launch a session from that directory. The slash commands and hooks remain globally installed; only the vault path changes. Full recipe in [`SKILL.md`](SKILL.md#per-project-vaults-multi-repo-workflows). One thing this does NOT give you: isolation within a single vault (no `--scope` on commands yet).

### Can I run this alongside another Obsidian plugin?
Yes, and nothing breaks at the hook level. Claude Code merges hook entries instead of replacing them, and "All matching hooks run in parallel" ([docs](https://code.claude.com/docs/en/hooks)). Both SessionStart hooks fire and both outputs reach your context.

The cost is a schema clash, not a crash. Each plugin states its own folder map and frontmatter fields for the same vault, so a note can land under either one. Since #300 this skill detects the other hook and opens its injected context with a precedence note naming what it found, and the vault's own `_CLAUDE.md` governs every write. It detects only. Your other plugin is never edited, disabled or unregistered.

To see what a session would find, run `python scripts/vault_plugin_scan.py`. To run only one system, remove the other plugin or its hook entry yourself.

### How do I update to the latest version?
```bash
cd ~/.claude/skills/obsidian-second-brain && git pull
```
On Linux/macOS: nothing else to run - slash commands are symlinked so they pick up the new files automatically. On Windows: also run `bash update.sh` to refresh the copied command files. Restart Claude Code after either path. See [CHANGELOG.md](CHANGELOG.md) for what's in each release.

### Where do I file issues or feature requests?
Command reference: https://eugeniughelbur.github.io/obsidian-second-brain/ - every command, with the plain-language phrases that trigger it in English, German, Spanish, Portuguese and Simplified Chinese.

Retrieval benchmark: [scripts/eval/BENCHMARK.md](scripts/eval/BENCHMARK.md) - a reproducible 300-note synthetic corpus and three query sets, so the search numbers are something you can run yourself rather than something this README claims.

The rule on its own: [AI-FIRST.md](AI-FIRST.md) - the note spec as a 50-line block you can paste into any `CLAUDE.md` or `AGENTS.md`. Installs nothing, works without this project, keep the attribution line.

GitHub Issues: https://github.com/Mouraovicente/obsidian-second-brain-contabil/issues. PRs welcome, see Contributing below.

---

## Philosophy

Most second brain tools make you the janitor.

This skill inverts that. You think, work, and talk. Claude handles the memory. Then it uses that memory to make you think better -- surfacing what you'd miss, challenging what you'd assume, connecting what you'd never link, and synthesizing patterns you didn't ask for.

The vault doesn't grow. It evolves.

**Your notes are the moat.**

Inspired by [Andrey Karpathy's LLM-Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

---

## Contributing

**Want a specific place to start?** [Good first issues](https://github.com/Mouraovicente/obsidian-second-brain-contabil/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) are scoped to name the exact files and lines, what to watch out for, and how big the change is. They range from adding trigger phrases in a language you speak (no Python at all) to a one-command lint fix to a new slash command. Comment on one to claim it.

PRs welcome more generally:
- New thinking tools
- Note type schemas (habits, books, investments)
- Alternative vault structures
- VS Code / Cursor setup guides

**Own a platform.** Four builds, one maintainer who can test two. [adapters/OWNERS.md](adapters/OWNERS.md) has the open list; using the platform is the whole qualification, and your handle ships inside that build.

Customizing your own fork? Copy [`references/DELTAS.template.md`](references/DELTAS.template.md) to a `DELTAS.md` at your fork root and record your local deviations there. Upstream never touches that file, so you can keep merging `upstream/main` cleanly instead of fighting conflicts in stock commands.

### Contributors

This project is maintained by one person but built with many. Close to 50 people have landed merged PRs: security fixes, platform ports, Windows compatibility, translations, and the first automated test. Ideas from closed or stalled PRs get reimplemented with the original author credited as co-author rather than dropped.

Thank you to everyone below, and to the nearly 100 people who filed issues or PRs by November 2026. Every report made the tool better.

<a href="https://github.com/eugeniughelbur/obsidian-second-brain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=eugeniughelbur/obsidian-second-brain" alt="Avatars of obsidian-second-brain contributors" />
</a>

If your PR goes quiet mid-review, that is normal life - the idea stays on the table, and if it lands later you stay on the commit.

---

## Sponsors

obsidian-second-brain is free and MIT-licensed. If it saves you time, a paid subscription to The AI Operator is the best way to support it. That is where I write about building it, and paid readers also get a monthly no-code guide and a monthly Q&A.

[![Support on Substack](https://img.shields.io/badge/Support_on_Substack-EA4AAA?style=for-the-badge&logo=substack&logoColor=white)](https://theaioperator.io/subscribe?utm_source=github&utm_medium=readme&utm_campaign=sponsors-section)

Prefer GitHub? [GitHub Sponsors](https://github.com/sponsors/eugeniughelbur) works too.

---

## Author

<div align="center">

<table>
<tr>
<td align="center" width="700">

Built by **Eugeniu Ghelbur**, AI Automation Engineer, AI Tooling Engineer, AI Educator

*If this skill helped you, the best thanks is following along.*

<a href="https://x.com/eugeniu_ghelbur"><img src="https://img.shields.io/badge/Follow_on_X-000?style=for-the-badge&logo=x&logoColor=white" alt="Follow on X" /></a>
<a href="https://www.linkedin.com/in/eugeniu-ghelbur/"><img src="https://img.shields.io/badge/Connect_on_LinkedIn-0A66C2?style=for-the-badge&logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0yMC40NDcgMjAuNDUyaC0zLjU1NHYtNS41NjljMC0xLjMyOC0uMDI3LTMuMDM3LTEuODUyLTMuMDM3LTEuODUzIDAtMi4xMzYgMS40NDUtMi4xMzYgMi45Mzl2NS42NjdIOS4zNTFWOWgzLjQxNHYxLjU2MWguMDQ2Yy40NzctLjkgMS42MzctMS44NSAzLjM3LTEuODUgMy42MDEgMCA0LjI2NyAyLjM3IDQuMjY3IDUuNDU1djYuMjg2ek01LjMzNyA3LjQzM2MtMS4xNDQgMC0yLjA2My0uOTI2LTIuMDYzLTIuMDY1IDAtMS4xMzguOTItMi4wNjMgMi4wNjMtMi4wNjMgMS4xNCAwIDIuMDY0LjkyNSAyLjA2NCAyLjA2MyAwIDEuMTM5LS45MjUgMi4wNjUtMi4wNjQgMi4wNjV6bTEuNzgyIDEzLjAxOUgzLjU1NVY5aDMuNTY0djExLjQ1MnpNMjIuMjI1IDBIMS43NzFDLjc5MiAwIDAgLjc3NCAwIDEuNzI5djIwLjU0MkMwIDIzLjIyNy43OTIgMjQgMS43NzEgMjRoMjAuNDUxQzIzLjIgMjQgMjQgMjMuMjI3IDI0IDIyLjI3MVYxLjcyOUMyNCAuNzc0IDIzLjIgMCAyMi4yMjIgMGguMDAzeiIvPjwvc3ZnPg%3D%3D" alt="Connect on LinkedIn" /></a>
<a href="https://theaioperator.io/subscribe?utm_source=github&utm_medium=readme&utm_campaign=footer"><img src="https://img.shields.io/badge/Subscribe_on_Substack-FF6719?style=for-the-badge&logo=substack&logoColor=white" alt="Subscribe on Substack" /></a>
<a href="https://github.com/eugeniughelbur"><img src="https://img.shields.io/badge/Follow_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="Follow on GitHub" /></a>

</td>
</tr>
</table>

</div>

---

## License

MIT
