# ReverseLab Codex Profile

Follow `AGENTS.md` and `AI-USAGE.md` first. Route each task to the matching board before using tools or writing reports.

## CTF game

For authorized CTF game work, start from `boards/ctf-website/README.md`, read `kb/ctf-website/techniques/attack-network.md`, then use `scripts/ctf-website/kb_router.py` for every observed signal.

## Attack Workflow

1. Generate context with `python scripts/misc/ai_context.py "<task>" --save`.
2. Plan tools with `python scripts/misc/ai_tool.py plan "<task>"`.
3. Keep raw evidence in `exports/<board>/`, notes in `notes/<board>/`, and final writeups in `reports/<board>/`.
4. Prefer reusable scripts and templates from this repository over ad hoc notes.

## CVE

When a version, framework, dependency, or fingerprint appears, map it to the local CVE chain knowledge base and record evidence before drawing conclusions.
