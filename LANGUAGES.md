# Using it in your language

Fourteen people had reported problems with non-English text by November 2026, and the code fixes are merged. This page says what works today and which setup stays on the tested path.

## Notes in Brazilian Portuguese (the `contabil` preset)

Vaults built with `--preset contabil` declare Portuguese in their `_CLAUDE.md`. The agent writes note bodies in Portuguese and does not translate them to English. Machine literals stay as they are: frontmatter keys, `ai-first: true`, the `## For future agent` heading. Search ignores accents, so "legislacao" finds "Legislação" and the other way around.

## The other path: talk in your language, keep the vault in English

For a vault that does not declare a language, you can still talk to your agent in your own language and keep the notes in English. The agent translates before it writes a note, replies in your language, and searches with English queries. Search quality is measured on English notes, so this is the most tested path outside the `contabil` preset.

Put the rule in `<vault>/.claude/CLAUDE.md`, not `_CLAUDE.md`, so an `/obsidian-init` re-run keeps it. [andreanovix](https://github.com/andreanovix) shared a working block in [discussion #307](https://github.com/eugeniughelbur/obsidian-second-brain/discussions/307).

## Notes in Chinese, Japanese or Korean

Notes in these languages work too:

- **Search** finds short words of one or two characters (#159).
- **The write-time check** accepts Chinese dashes, quotes and the ellipsis on any line with Chinese, Japanese or Korean text (#271).
- **To turn that check off** for a whole vault, add `AI_FIRST_SKIP_CHECKS=5` to the toolkit `.env`.

## Command phrases in your language

The [command reference](https://eugeniughelbur.github.io/obsidian-second-brain/) lists the phrases that start each command in English, German, Spanish, Portuguese and Simplified Chinese. You can say "speichere das" or "保存这段对话" instead of typing `/obsidian-save`.

## Encoding

Every script reads and writes UTF-8. On Windows, old notes saved in the cp1252 code page need one re-save. See [Windows setup](WINDOWS.md#text-encoding).

## Add your language

Trigger phrases for more languages are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and open a PR.
