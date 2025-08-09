"""
Anytime Fitness Bot – MCP Server (Python, stdio)

This server exposes a curated set of safe, high-utility tools for repository
automation: file operations, search/grep, git helpers, and controlled command
execution. It communicates over stdio so MCP-compatible clients can spawn it.

Safety:
- All write/exec/git-commit tools require confirmed=True.
- Path access is sandboxed to the repository root.
- Output is returned via the protocol; logs go to stderr.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    # Reference Python SDK for Model Context Protocol
    from mcp.server import Server, RequestContext, types, models as ms
    from mcp.server.stdio import stdio_server
except Exception as e:  # pragma: no cover
    # Provide a clear error on startup if dependency is missing
    sys.stderr.write(
        f"[MCP] Missing dependency 'mcp'. Install requirements and retry. Error: {e}\n"
    )
    raise


# ----------------------------------------------------------------------------
# Init
# ----------------------------------------------------------------------------

SERVER_NAME = "anytime-fitness-bot-mcp"
server = Server(SERVER_NAME)


def _project_root() -> Path:
    # services/mcp/server.py -> repo root is two parents up from 'services' dir
    # server.py -> mcp (0) -> services (1) -> repo root (2)
    return Path(__file__).resolve().parents[2]


REPO_ROOT = _project_root()


def _ensure_in_repo(path: Path) -> Path:
    """Ensure path resolves within repo root; prevent escaping via .."""
    resolved = (REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise ValueError("Path escapes repository root")
    return resolved


def _read_text_file(p: Path, max_bytes: int = 2_000_000) -> str:
    if not p.exists():
        raise FileNotFoundError(str(p))
    if p.is_dir():
        raise IsADirectoryError(str(p))
    size = p.stat().st_size
    if size > max_bytes:
        raise ValueError(f"File too large to read safely ({size} bytes > {max_bytes})")
    # Try utf-8, fallback latin-1
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="latin-1", errors="replace")


def _run(cmd: List[str], cwd: Optional[Path] = None, timeout: int = 120) -> Dict[str, Any]:
    """Run a subprocess and return structured result."""
    proc = subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        text=True,
        shell=False,
    )
    return {"code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def _git_available() -> bool:
    try:
        res = _run(["git", "--version"], timeout=10)
        return res["code"] == 0
    except Exception:
        return False


# ----------------------------------------------------------------------------
# Tool implementations (callable directly and via MCP)
# ----------------------------------------------------------------------------


async def ping() -> str:
    """Health check."""
    return "pong"


async def echo(message: str) -> str:
    """Echo back a message."""
    return message


async def repo_info() -> Dict[str, Any]:
    """Return basic repository info (root, branch if git)."""
    info: Dict[str, Any] = {"root": str(REPO_ROOT), "git": False}
    if _git_available():
        info["git"] = True
        try:
            branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])  # type: ignore[arg-type]
            info["branch"] = branch.get("stdout", "").strip()
        except Exception:
            info["branch"] = None
    return info


async def list_dir(path: str = ".", recursive: bool = False, max_entries: int = 500) -> List[Dict[str, Any]]:
    """List files under a path within the repo. Returns name, path, type, size."""
    p = _ensure_in_repo(Path(path))
    if not p.exists():
        raise FileNotFoundError(str(p))
    entries: List[Dict[str, Any]] = []

    def add_entry(fp: Path):
        try:
            st = fp.stat()
            entries.append(
                {
                    "name": fp.name,
                    "path": str(fp.relative_to(REPO_ROOT)),
                    "type": "dir" if fp.is_dir() else "file",
                    "size": st.st_size,
                }
            )
        except FileNotFoundError:
            pass

    if recursive and p.is_dir():
        for root, dirs, files in os.walk(p):
            for d in dirs:
                add_entry(Path(root) / d)
                if len(entries) >= max_entries:
                    return entries
            for f in files:
                add_entry(Path(root) / f)
                if len(entries) >= max_entries:
                    return entries
    else:
        for fp in p.iterdir():
            add_entry(fp)
            if len(entries) >= max_entries:
                break
    return entries


async def read_file(path: str, offset: int = 0, limit: int = 2000) -> Dict[str, Any]:
    """Read a text file with optional offset/limit (safe size cap)."""
    p = _ensure_in_repo(Path(path))
    content = _read_text_file(p)
    start = max(0, int(offset))
    end = start + max(0, int(limit)) if limit is not None else None
    sliced = content[start:end]
    return {"path": str(p.relative_to(REPO_ROOT)), "offset": start, "limit": limit, "content": sliced, "total_bytes": len(content.encode("utf-8", errors="ignore"))}


async def write_file(
    path: str,
    content: str,
    overwrite: bool = False,
    create_dirs: bool = False,
    confirmed: bool = False,
) -> Dict[str, Any]:
    """Write/overwrite a file. Requires confirmed=True. Creates dirs optionally."""
    if not confirmed:
        raise PermissionError("write_file requires confirmed=True")
    p = _ensure_in_repo(Path(path))
    if not p.parent.exists():
        if create_dirs:
            p.parent.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(f"Parent directory does not exist: {p.parent}")
    if p.exists() and not overwrite:
        raise FileExistsError(str(p))
    # Write using utf-8
    p.write_text(content, encoding="utf-8")
    return {"path": str(p.relative_to(REPO_ROOT)), "bytes": len(content.encode("utf-8"))}


async def append_file(path: str, content: str, confirmed: bool = False) -> Dict[str, Any]:
    """Append to a file. Requires confirmed=True."""
    if not confirmed:
        raise PermissionError("append_file requires confirmed=True")
    p = _ensure_in_repo(Path(path))
    if not p.exists():
        raise FileNotFoundError(str(p))
    with p.open("a", encoding="utf-8") as f:
        f.write(content)
    return {"path": str(p.relative_to(REPO_ROOT)), "appended": len(content.encode("utf-8"))}


async def grep(
    pattern: str,
    path_glob: str = "**/*",
    is_regex: bool = True,
    ignore_binary: bool = True,
    max_matches: int = 200,
) -> List[Dict[str, Any]]:
    """Search files by regex or plain substring and return matches with line numbers."""
    results: List[Dict[str, Any]] = []
    regex = re.compile(pattern, flags=re.IGNORECASE) if is_regex else None
    for fp in REPO_ROOT.glob(path_glob):
        if not fp.is_file():
            continue
        # Basic binary guard
        try:
            with fp.open("rb") as fb:
                head = fb.read(1024)
                if ignore_binary and b"\x00" in head:
                    continue
        except Exception:
            continue
        try:
            text = _read_text_file(fp)
        except Exception:
            continue

        for idx, line in enumerate(text.splitlines(), start=1):
            found = bool(regex.search(line) if regex else (pattern.lower() in line.lower()))
            if found:
                results.append(
                    {
                        "path": str(fp.relative_to(REPO_ROOT)),
                        "line": idx,
                        "text": line.strip(),
                    }
                )
                if len(results) >= max_matches:
                    return results
    return results


async def git_status() -> Dict[str, Any]:
    """Return `git status --porcelain=v1 -z` (if git available)."""
    if not _git_available():
        return {"git": False, "status": None}
    res = _run(["git", "status", "--porcelain=v1"], cwd=REPO_ROOT, timeout=30)
    return {"git": True, "code": res["code"], "stdout": res["stdout"], "stderr": res["stderr"]}


async def git_diff(path: Optional[str] = None, staged: bool = False) -> Dict[str, Any]:
    """Return `git diff` output, optionally for a path or staged changes."""
    if not _git_available():
        return {"git": False, "diff": None}
    args = ["git", "diff"]
    if staged:
        args.append("--staged")
    if path:
        p = _ensure_in_repo(Path(path))
        args.append(str(p))
    res = _run(args, cwd=REPO_ROOT, timeout=60)
    return {"git": True, "code": res["code"], "stdout": res["stdout"], "stderr": res["stderr"]}


async def git_commit(message: str, add_all: bool = True, confirmed: bool = False) -> Dict[str, Any]:
    """Stage and commit changes. Requires confirmed=True."""
    if not confirmed:
        raise PermissionError("git_commit requires confirmed=True")
    if not _git_available():
        return {"git": False, "committed": False, "reason": "git not available"}
    if add_all:
        _run(["git", "add", "-A"], cwd=REPO_ROOT, timeout=30)
    res = _run(["git", "commit", "-m", message], cwd=REPO_ROOT, timeout=60)
    return {"git": True, "code": res["code"], "stdout": res["stdout"], "stderr": res["stderr"]}


async def run_pytest(args: Optional[str] = None, timeout: int = 300, confirmed: bool = False) -> Dict[str, Any]:
    """Run pytest in the repo. Requires confirmed=True. Returns exit code and output."""
    if not confirmed:
        raise PermissionError("run_pytest requires confirmed=True")
    # Use the current Python to ensure venv tools resolve correctly on Windows
    cmd = [sys.executable, "-m", "pytest"]
    if args:
        cmd.extend(args.split())
    res = _run(cmd, cwd=REPO_ROOT, timeout=timeout)
    return {"code": res["code"], "stdout": res["stdout"], "stderr": res["stderr"]}


ALLOWED_PREFIXES = ("pytest", "python", "pip", "git", "ruff", "flake8")


async def run_command(cmd: str, timeout: int = 120, confirmed: bool = False) -> Dict[str, Any]:
    """Run a shell-less command with a restricted allowlist. Requires confirmed=True."""
    if not confirmed:
        raise PermissionError("run_command requires confirmed=True")
    stripped = cmd.strip()
    if not stripped.startswith(ALLOWED_PREFIXES):
        raise PermissionError(f"Command not allowed. Allowed prefixes: {ALLOWED_PREFIXES}")
    # Split minimally for common commands; for complex cases use run_pytest or specific tools
    parts = stripped.split()
    res = _run(parts, cwd=REPO_ROOT, timeout=timeout)
    return {"code": res["code"], "stdout": res["stdout"], "stderr": res["stderr"]}


async def search_glob(path_glob: str = "**/*", file_only: bool = True, max_results: int = 2000) -> List[str]:
    """Return paths matching a glob pattern within the repo."""
    results: List[str] = []
    for fp in REPO_ROOT.glob(path_glob):
        if file_only and not fp.is_file():
            continue
        try:
            rel = str(fp.relative_to(REPO_ROOT))
        except Exception:
            continue
        results.append(rel)
        if len(results) >= max_results:
            break
    return results


def _sub_once(text: str, pattern: str, repl: str, is_regex: bool) -> Tuple[str, int]:
    if is_regex:
        new_text, n = re.subn(pattern, repl, text)
        return new_text, n
    else:
        n = text.count(pattern)
        return text.replace(pattern, repl), n


async def replace_in_file(
    path: str,
    pattern: str,
    replacement: str,
    is_regex: bool = True,
    dry_run: bool = True,
    confirmed: bool = False,
) -> Dict[str, Any]:
    """Replace occurrences in a file. Use dry_run to preview first; requires confirmed=False for preview and confirmed=True to apply."""
    p = _ensure_in_repo(Path(path))
    text = _read_text_file(p)
    new_text, n = _sub_once(text, pattern, replacement, is_regex)
    if dry_run:
        return {"path": str(p.relative_to(REPO_ROOT)), "matches": n, "dry_run": True}
    if not confirmed:
        raise PermissionError("replace_in_file apply requires confirmed=True")
    if n > 0:
        p.write_text(new_text, encoding="utf-8")
    return {"path": str(p.relative_to(REPO_ROOT)), "replaced": n, "dry_run": False}


async def replace_in_repo(
    pattern: str,
    replacement: str,
    path_glob: str = "**/*",
    is_regex: bool = True,
    ignore_binary: bool = True,
    max_files: int = 200,
    dry_run: bool = True,
    confirmed: bool = False,
) -> Dict[str, Any]:
    """Replace across multiple files matched by glob. Preview via dry_run; apply requires confirmed=True."""
    changed: Dict[str, int] = {}
    processed = 0
    for fp in REPO_ROOT.glob(path_glob):
        if not fp.is_file():
            continue
        # binary guard
        try:
            with fp.open("rb") as fb:
                head = fb.read(1024)
                if ignore_binary and b"\x00" in head:
                    continue
        except Exception:
            continue
        try:
            text = _read_text_file(fp)
        except Exception:
            continue
        new_text, n = _sub_once(text, pattern, replacement, is_regex)
        if n > 0:
            changed[str(fp.relative_to(REPO_ROOT))] = n
            if not dry_run:
                if not confirmed:
                    raise PermissionError("replace_in_repo apply requires confirmed=True")
                fp.write_text(new_text, encoding="utf-8")
            processed += 1
            if processed >= max_files:
                break
    return {"changed": changed, "dry_run": dry_run}


async def create_directory(path: str, exist_ok: bool = True, confirmed: bool = False) -> Dict[str, Any]:
    """Create a directory (and parents). Requires confirmed=True."""
    if not confirmed:
        raise PermissionError("create_directory requires confirmed=True")
    p = _ensure_in_repo(Path(path))
    p.mkdir(parents=True, exist_ok=exist_ok)
    return {"path": str(p.relative_to(REPO_ROOT)), "created": True}


async def delete_file(path: str, confirmed: bool = False) -> Dict[str, Any]:
    """Delete a single file. Requires confirmed=True."""
    if not confirmed:
        raise PermissionError("delete_file requires confirmed=True")
    p = _ensure_in_repo(Path(path))
    if not p.exists():
        return {"path": str(p.relative_to(REPO_ROOT)), "deleted": False, "reason": "not found"}
    if p.is_dir():
        raise IsADirectoryError(str(p))
    p.unlink()
    return {"path": str(p.relative_to(REPO_ROOT)), "deleted": True}


async def delete_tree(path: str, confirmed: bool = False) -> Dict[str, Any]:
    """Delete a directory tree. Requires confirmed=True."""
    if not confirmed:
        raise PermissionError("delete_tree requires confirmed=True")
    p = _ensure_in_repo(Path(path))
    if not p.exists():
        return {"path": str(p.relative_to(REPO_ROOT)), "deleted": False, "reason": "not found"}
    if p.is_file():
        raise NotADirectoryError(str(p))
    # Safe recursive delete
    for root, dirs, files in os.walk(p, topdown=False):
        for f in files:
            Path(root, f).unlink(missing_ok=True)
        for d in dirs:
            Path(root, d).rmdir()
    p.rmdir()
    return {"path": str(p.relative_to(REPO_ROOT)), "deleted": True}


async def apply_patch_git(patch_text: str, confirmed: bool = False) -> Dict[str, Any]:
    """Apply a unified diff patch using `git apply --whitespace=nowarn`. Requires confirmed=True and git available."""
    if not confirmed:
        raise PermissionError("apply_patch_git requires confirmed=True")
    if not _git_available():
        return {"git": False, "applied": False, "reason": "git not available"}
    # Write to a temp file
    import tempfile

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".patch", encoding="utf-8") as tf:
        tf.write(patch_text)
        tmp_path = tf.name
    try:
        res = _run(["git", "apply", "--whitespace=nowarn", tmp_path], cwd=REPO_ROOT, timeout=120)
        ok = res["code"] == 0
        return {"git": True, "applied": ok, "code": res["code"], "stdout": res["stdout"], "stderr": res["stderr"]}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


async def format_code(target: str = ".", use_black: bool = True, use_ruff: bool = True, confirmed: bool = False) -> Dict[str, Any]:
    """Format code using ruff (fix) and/or black. Requires confirmed=True."""
    if not confirmed:
        raise PermissionError("format_code requires confirmed=True")
    results: Dict[str, Any] = {}
    p = _ensure_in_repo(Path(target))
    if use_ruff:
        results["ruff"] = _run([sys.executable, "-m", "ruff", "check", "--fix", str(p)], cwd=REPO_ROOT, timeout=300)
    if use_black:
        results["black"] = _run([sys.executable, "-m", "black", str(p)], cwd=REPO_ROOT, timeout=300)
    # Normalize outputs
    for k, v in list(results.items()):
        if isinstance(v, dict):
            results[k] = {"code": v.get("code"), "stdout": v.get("stdout"), "stderr": v.get("stderr")}
    return results


async def lint_check(target: str = ".", use_ruff: bool = True, use_flake8: bool = False) -> Dict[str, Any]:
    """Run linters (no writes)."""
    results: Dict[str, Any] = {}
    p = _ensure_in_repo(Path(target))
    if use_ruff:
        results["ruff"] = _run([sys.executable, "-m", "ruff", "check", str(p)], cwd=REPO_ROOT, timeout=300)
    if use_flake8:
        results["flake8"] = _run([sys.executable, "-m", "flake8", str(p)], cwd=REPO_ROOT, timeout=300)
    for k, v in list(results.items()):
        if isinstance(v, dict):
            results[k] = {"code": v.get("code"), "stdout": v.get("stdout"), "stderr": v.get("stderr")}
    return results


async def run_python(args: str, timeout: int = 600, confirmed: bool = False) -> Dict[str, Any]:
    """Run python with arguments, e.g., "-m pytest -q" or "path/to/script.py". Requires confirmed=True."""
    if not confirmed:
        raise PermissionError("run_python requires confirmed=True")
    # Use current interpreter for reliability (venv aware)
    parts = [sys.executable] + args.split()
    res = _run(parts, cwd=REPO_ROOT, timeout=timeout)
    return {"code": res["code"], "stdout": res["stdout"], "stderr": res["stderr"]}


# ----------------------------------------------------------------------------
# MCP registration: list_tools + call_tool
# ----------------------------------------------------------------------------


def _schema(obj_props: Dict[str, Any], required: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": obj_props,
        "required": required or [],
        "additionalProperties": False,
    }


TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "ping": {
        "func": ping,
        "desc": "Health check.",
        "schema": _schema({}, []),
    },
    "echo": {
        "func": echo,
        "desc": "Echo a message.",
        "schema": _schema({"message": {"type": "string"}}, ["message"]),
    },
    "repo_info": {"func": repo_info, "desc": "Repo root and git branch.", "schema": _schema({}, [])},
    "list_dir": {
        "func": list_dir,
        "desc": "List directory entries.",
        "schema": _schema({
            "path": {"type": "string", "default": "."},
            "recursive": {"type": "boolean", "default": False},
            "max_entries": {"type": "integer", "default": 500}
        }),
    },
    "read_file": {
        "func": read_file,
        "desc": "Read a text file slice.",
        "schema": _schema({
            "path": {"type": "string"},
            "offset": {"type": "integer", "default": 0},
            "limit": {"type": "integer", "default": 2000}
        }, ["path"]),
    },
    "write_file": {
        "func": write_file,
        "desc": "Write/overwrite a file (confirmed required).",
        "schema": _schema({
            "path": {"type": "string"},
            "content": {"type": "string"},
            "overwrite": {"type": "boolean", "default": False},
            "create_dirs": {"type": "boolean", "default": False},
            "confirmed": {"type": "boolean"}
        }, ["path", "content", "confirmed"]),
    },
    "append_file": {
        "func": append_file,
        "desc": "Append to a file (confirmed required).",
        "schema": _schema({
            "path": {"type": "string"},
            "content": {"type": "string"},
            "confirmed": {"type": "boolean"}
        }, ["path", "content", "confirmed"]),
    },
    "grep": {
        "func": grep,
        "desc": "Search files for a pattern.",
        "schema": _schema({
            "pattern": {"type": "string"},
            "path_glob": {"type": "string", "default": "**/*"},
            "is_regex": {"type": "boolean", "default": True},
            "ignore_binary": {"type": "boolean", "default": True},
            "max_matches": {"type": "integer", "default": 200}
        }, ["pattern"]),
    },
    "git_status": {"func": git_status, "desc": "Git status.", "schema": _schema({}, [])},
    "git_diff": {
        "func": git_diff,
        "desc": "Git diff (optionally staged or path).",
        "schema": _schema({
            "path": {"type": ["string", "null"], "default": None},
            "staged": {"type": "boolean", "default": False}
        }),
    },
    "git_commit": {
        "func": git_commit,
        "desc": "Git commit (confirmed required).",
        "schema": _schema({
            "message": {"type": "string"},
            "add_all": {"type": "boolean", "default": True},
            "confirmed": {"type": "boolean"}
        }, ["message", "confirmed"]),
    },
    "run_pytest": {
        "func": run_pytest,
        "desc": "Run pytest (confirmed required).",
        "schema": _schema({
            "args": {"type": ["string", "null"], "default": None},
            "timeout": {"type": "integer", "default": 300},
            "confirmed": {"type": "boolean"}
        }, ["confirmed"]),
    },
    "run_command": {
        "func": run_command,
        "desc": "Run allowlisted command (confirmed required).",
        "schema": _schema({
            "cmd": {"type": "string"},
            "timeout": {"type": "integer", "default": 120},
            "confirmed": {"type": "boolean"}
        }, ["cmd", "confirmed"]),
    },
    "search_glob": {
        "func": search_glob,
        "desc": "List paths matching glob.",
        "schema": _schema({
            "path_glob": {"type": "string", "default": "**/*"},
            "file_only": {"type": "boolean", "default": True},
            "max_results": {"type": "integer", "default": 2000}
        }),
    },
    "replace_in_file": {
        "func": replace_in_file,
        "desc": "Search/replace in a file (dry-run by default).",
        "schema": _schema({
            "path": {"type": "string"},
            "pattern": {"type": "string"},
            "replacement": {"type": "string"},
            "is_regex": {"type": "boolean", "default": True},
            "dry_run": {"type": "boolean", "default": True},
            "confirmed": {"type": "boolean", "default": False}
        }, ["path", "pattern", "replacement"]),
    },
    "replace_in_repo": {
        "func": replace_in_repo,
        "desc": "Search/replace across repo (dry-run by default).",
        "schema": _schema({
            "pattern": {"type": "string"},
            "replacement": {"type": "string"},
            "path_glob": {"type": "string", "default": "**/*"},
            "is_regex": {"type": "boolean", "default": True},
            "ignore_binary": {"type": "boolean", "default": True},
            "max_files": {"type": "integer", "default": 200},
            "dry_run": {"type": "boolean", "default": True},
            "confirmed": {"type": "boolean", "default": False}
        }, ["pattern", "replacement"]),
    },
    "create_directory": {
        "func": create_directory,
        "desc": "Create directory (confirmed required).",
        "schema": _schema({
            "path": {"type": "string"},
            "exist_ok": {"type": "boolean", "default": True},
            "confirmed": {"type": "boolean"}
        }, ["path", "confirmed"]),
    },
    "delete_file": {
        "func": delete_file,
        "desc": "Delete file (confirmed required).",
        "schema": _schema({
            "path": {"type": "string"},
            "confirmed": {"type": "boolean"}
        }, ["path", "confirmed"]),
    },
    "delete_tree": {
        "func": delete_tree,
        "desc": "Delete directory tree (confirmed required).",
        "schema": _schema({
            "path": {"type": "string"},
            "confirmed": {"type": "boolean"}
        }, ["path", "confirmed"]),
    },
    "apply_patch_git": {
        "func": apply_patch_git,
        "desc": "Apply unified diff via git (confirmed required).",
        "schema": _schema({
            "patch_text": {"type": "string"},
            "confirmed": {"type": "boolean"}
        }, ["patch_text", "confirmed"]),
    },
    "format_code": {
        "func": format_code,
        "desc": "Format code with ruff/black (confirmed required).",
        "schema": _schema({
            "target": {"type": "string", "default": "."},
            "use_black": {"type": "boolean", "default": True},
            "use_ruff": {"type": "boolean", "default": True},
            "confirmed": {"type": "boolean"}
        }, ["confirmed"]),
    },
    "lint_check": {
        "func": lint_check,
        "desc": "Run linters (no writes).",
        "schema": _schema({
            "target": {"type": "string", "default": "."},
            "use_ruff": {"type": "boolean", "default": True},
            "use_flake8": {"type": "boolean", "default": False}
        }),
    },
    "run_python": {
        "func": run_python,
        "desc": "Run python with args (confirmed required).",
        "schema": _schema({
            "args": {"type": "string"},
            "timeout": {"type": "integer", "default": 600},
            "confirmed": {"type": "boolean"}
        }, ["args", "confirmed"]),
    },
}


@server.list_tools()
async def _list_tools() -> List[types.Tool]:
    tools: List[types.Tool] = []
    for name, meta in TOOL_REGISTRY.items():
        tools.append(
            types.Tool(
                name=name,
                description=meta.get("desc", name),
                inputSchema=meta.get("schema", _schema({})),
            )
        )
    return tools


@server.call_tool()
async def _call_tool(name: str, arguments: Dict[str, Any], ctx: RequestContext) -> List[types.TextContent]:
    meta = TOOL_REGISTRY.get(name)
    if not meta:
        return [types.TextContent(type="text", text=json.dumps({"error": f"unknown tool: {name}"}))]
    func = meta["func"]
    # Ensure arguments is a dict
    if not isinstance(arguments, dict):
        arguments = {}
    try:
        result = await func(**arguments)
        if isinstance(result, (dict, list)):
            text = json.dumps(result, ensure_ascii=False)
        else:
            text = str(result)
        return [types.TextContent(type="text", text=text)]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]


# ----------------------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------------------


async def _main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    async with stdio_server() as (read, write):
        # Initialize with minimal capabilities: we expose tools via list_tools/call_tool
        init_opts = ms.InitializationOptions(
            server_name=SERVER_NAME,
            server_version="0.1.0",
            capabilities=ms.ServerCapabilities(tools={}),
        )
        await server.run(read, write, init_opts)


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(_main())
