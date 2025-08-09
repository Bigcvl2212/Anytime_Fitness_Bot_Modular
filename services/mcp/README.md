# MCP Server for Anytime_Fitness_Bot_Modular

This module provides a robust Model Context Protocol (MCP) server exposing safe, high-utility tools for repository automation. It is designed to help the assistant build, refactor, test, and commit reliably in this repo.

## Tools exposed
- ping: health check
- echo: echo message
- repo_info: repo root, current git branch
- list_dir: list files/dirs with size and type
- read_file: read text files with offset/limit
- write_file: write/overwrite files (confirmed required)
- append_file: append to files (confirmed required)
- grep: regex/substring search across repo with line numbers
- git_status: porcelain status output
- git_diff: get diffs (optionally staged or file-scoped)
- git_commit: stage (optional) and commit (confirmed required)
- run_pytest: run tests with args (confirmed required)
- run_command: restricted allowlist runner for common dev cmds (confirmed required)

All write/exec actions are gated by `confirmed: true` and sandboxed to the repo root.

## Run (Windows PowerShell)
1. Ensure Python 3.10+ is available on PATH.
2. Create and activate a venv, then install deps:
   ```powershell
   python -m venv .venv; .venv\Scripts\Activate.ps1
   pip install -r services\mcp\requirements.txt
   ```
3. Start the server (stdio transport):
   ```powershell
   python services\mcp\server.py
   ```

Notes:
- The server uses stdio (stdin/stdout) so an MCP client should spawn it; manual run shows no output until a client connects.
- Logs go to stderr; protocol responses go to stdout.

## Next steps
- Add authenticated tools that call into `services/api/clubhub_api_client.py`, ClubOS modules, and key workflows.
- Keep destructive operations behind `confirmed: true` and add role/owner checks if exposing publicly.
