"""Dump-only Unica apply dryRun + docs smoke on simple1CAiConf.

Never publishes (no dryRun:false with a real ifRev). Isolated provider-state.
"""
from __future__ import annotations

import hashlib
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BINARY = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01\target\debug\unica.exe")
DUMP = Path(os.environ.get("UNICA_SMOKE_DUMP", r"C:\MyProjects\choice-of-tools-1c\source-checkouts\simple1CAiConf"))
WORK = Path(os.environ.get("UNICA_SMOKE_WORK", r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01-apply"))
STATE = WORK / "provider-state"
LOGS_OUT = Path(r"C:\MyProjects\choice-of-tools-1c\evaluations\main\logs")
PLUGIN_ROOT = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01\unica-src\plugins\unica")
LOG_PREFIX = os.environ.get("UNICA_SMOKE_LOG_PREFIX", "r01-mcp-apply")

DOCUMENT_AT = "main:Document.ЗаказПокупателя"
COMMENT_PREVIEW = "r01-dryrun-preview-do-not-publish"
SKIP_DUMP_DIRS = {".build", ".code-index", ".git"}


def dump_json(name: str, value: Any) -> None:
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    path = LOGS_OUT / name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_envelope(rpc: dict[str, Any]) -> dict[str, Any]:
    result = rpc.get("result") or {}
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured
    for block in result.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text") or ""
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    if isinstance(rpc.get("error"), dict):
        return rpc["error"]
    return result if isinstance(result, dict) else {}


def envelope_blob(env: dict[str, Any]) -> str:
    return json.dumps(env, ensure_ascii=False)


def fingerprint_dump(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DUMP_DIRS for part in rel.parts):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files[rel.as_posix()] = digest
    return files


class UnicaClient:
    def __init__(self, proc: subprocess.Popen[str]) -> None:
        self.proc = proc
        self._next_id = 1
        self._lines: queue.Queue[str | None] = queue.Queue()
        self._reader = threading.Thread(target=self._pump, daemon=True)
        self._reader.start()

    def _pump(self) -> None:
        assert self.proc.stdout is not None
        try:
            for line in self.proc.stdout:
                self._lines.put(line)
        finally:
            self._lines.put(None)

    def send(self, payload: dict[str, Any]) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        msg: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self.send(msg)

    def request(self, method: str, params: dict[str, Any] | None, timeout: float) -> dict[str, Any]:
        req_id = self._next_id
        self._next_id += 1
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            payload["params"] = params
        self.send(payload)
        return self.recv(req_id, timeout)

    def recv(self, req_id: int, timeout: float) -> dict[str, Any]:
        deadline = time.time() + timeout
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError(f"timed out waiting for JSON-RPC id={req_id}")
            try:
                line = self._lines.get(timeout=remaining)
            except queue.Empty as exc:
                raise TimeoutError(f"timed out waiting for JSON-RPC id={req_id}") from exc
            if line is None:
                raise RuntimeError(f"unica stdout closed before id={req_id}; exit={self.proc.poll()}")
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"invalid JSON from unica: {line!r}") from exc
            if value.get("id") != req_id:
                continue
            return value


def call_tool(client: UnicaClient, name: str, arguments: dict[str, Any], timeout: float) -> dict[str, Any]:
    return client.request(
        "tools/call",
        {"name": name, "arguments": arguments},
        timeout,
    )


def kill_daemon(state_root: Path) -> list[int]:
    killed: list[int] = []
    for endpoint in state_root.rglob("endpoint.json"):
        try:
            data = json.loads(endpoint.read_text(encoding="utf-8"))
        except Exception:
            continue
        pid = data.get("pid")
        if not isinstance(pid, int) or pid <= 0:
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append(pid)
        except OSError:
            try:
                subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"], capture_output=True, check=False)
                killed.append(pid)
            except Exception:
                pass
    return killed


def main() -> int:
    if not BINARY.is_file():
        print(f"MISSING BINARY {BINARY}", file=sys.stderr)
        return 2
    if not (DUMP / "Configuration.xml").is_file():
        print(f"MISSING DUMP {DUMP}", file=sys.stderr)
        return 2

    STATE.mkdir(parents=True, exist_ok=True)
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    before = fingerprint_dump(DUMP)
    env = os.environ.copy()
    env["UNICA_PROVIDER_STATE_DIR"] = str(STATE)
    env["UNICA_DAEMON_IDLE_GRACE_MS"] = "8000"
    env["UNICA_PLUGIN_ROOT"] = str(PLUGIN_ROOT)

    stderr_path = WORK / "unica.stderr.log"
    stderr_f = stderr_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(BINARY)],
        cwd=str(DUMP),
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=stderr_f,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )
    client = UnicaClient(proc)
    checks: list[dict[str, Any]] = []
    failed = 0

    def record(name: str, expected: str, actual: str, ok: bool, extra: Any = None) -> None:
        nonlocal failed
        checks.append({"name": name, "expected": expected, "actual": actual, "pass": ok, "extra": extra})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {actual}")
        if not ok:
            failed += 1

    try:
        init = client.request(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "r01-apply-smoke", "version": "0"},
            },
            timeout=60,
        )
        dump_json(f"{LOG_PREFIX}-initialize-simple.json", init)
        server = ((init.get("result") or {}).get("serverInfo") or {})
        record(
            "initialize",
            "serverInfo.name=unica",
            f"name={server.get('name')} version={server.get('version')}",
            server.get("name") == "unica" and init.get("result") is not None,
        )
        client.notify("notifications/initialized", {})

        dry_args = {
            "at": DOCUMENT_AT,
            "dryRun": True,
            "ops": [
                {
                    "op": "props.set",
                    "args": {"values": {"Comment": COMMENT_PREVIEW}},
                }
            ],
        }
        apply_dry = call_tool(client, "unica.apply", dry_args, timeout=180)
        dump_json(f"{LOG_PREFIX}-dryrun-simple.json", apply_dry)
        env_dry = extract_envelope(apply_dry)
        blob_dry = envelope_blob(env_dry)
        # Tool must answer: preview plan, or a named structured refusal.
        # Transport crash / timeout is a fail. Publication must not happen.
        dry_answered = apply_dry.get("result") is not None or apply_dry.get("error") is not None
        dry_ok_preview = bool(env_dry.get("ok")) and (
            "rev" in env_dry or "plan" in blob_dry.lower() or "preview" in blob_dry.lower()
        )
        diagnostics = env_dry.get("diagnostics")
        dry_named_refusal = env_dry.get("ok") is False and (
            isinstance(diagnostics, list) and len(diagnostics) > 0
        )
        record(
            "unica.apply dryRun props.set Comment",
            "structured preview or named refusal; no publish",
            f"ok={env_dry.get('ok')} summary={env_dry.get('summary')} rpc_error={apply_dry.get('error') is not None}",
            dry_answered and (dry_ok_preview or dry_named_refusal),
            {"envelope_keys": list(env_dry.keys()), "diagnostics": diagnostics},
        )

        fence_args = {
            "at": DOCUMENT_AT,
            "ops": [
                {
                    "op": "props.set",
                    "args": {"values": {"Comment": COMMENT_PREVIEW}},
                }
            ],
        }
        apply_fence = call_tool(client, "unica.apply", fence_args, timeout=60)
        dump_json(f"{LOG_PREFIX}-fence-simple.json", apply_fence)
        env_fence = extract_envelope(apply_fence)
        blob_fence = envelope_blob(env_fence).lower()
        fence_ok = (
            env_fence.get("ok") is not True
            and ("ifrev" in blob_fence or "dryrun" in blob_fence)
        )
        record(
            "unica.apply without ifRev (publish fence)",
            "refusal naming ifRev / dryRun",
            f"ok={env_fence.get('ok')} summary={env_fence.get('summary')} rpc_error={apply_fence.get('error') is not None} blob={blob_fence[:240]}",
            fence_ok,
        )

        skip_docs = os.environ.get("UNICA_SMOKE_SKIP_DOCS") == "1"
        if not skip_docs:
            docs = call_tool(client, "unica.docs", {"query": "НаборЗаписей"}, timeout=120)
            dump_json("r01-mcp-docs-working-simple.json", docs)
            env_docs = extract_envelope(docs)
            data_docs = env_docs.get("data") if isinstance(env_docs.get("data"), dict) else {}
            task = data_docs.get("task") if isinstance(data_docs.get("task"), dict) else {}
            task_id = task.get("taskId")
            if isinstance(task_id, str) and task.get("status") == "working":
                deadline = time.time() + 35
                poll = 0
                while time.time() < deadline:
                    poll += 1
                    wait_ms = min(7000, max(100, int((deadline - time.time()) * 1000)))
                    docs = call_tool(
                        client,
                        "unica.task.result",
                        {"taskId": task_id, "waitMs": wait_ms},
                        timeout=max(15, wait_ms / 1000 + 5),
                    )
                    env_docs = extract_envelope(docs)
                    data_docs = env_docs.get("data") if isinstance(env_docs.get("data"), dict) else {}
                    task = data_docs.get("task") if isinstance(data_docs.get("task"), dict) else {}
                    if task.get("status") != "working":
                        break
                    if env_docs.get("summary") != "Task is still working" and "sections" in envelope_blob(env_docs):
                        break
                dump_json("r01-mcp-docs-simple.json", {"polls": poll, "rpc": docs})
            else:
                dump_json("r01-mcp-docs-simple.json", docs)

            sections = data_docs.get("sections") or env_docs.get("sections") or []
            n_hits = 0
            statuses: list[str] = []
            if isinstance(sections, list):
                for section in sections:
                    if isinstance(section, dict):
                        statuses.append(str(section.get("status")))
                        hits = section.get("hits") or []
                        if isinstance(hits, list):
                            n_hits += len(hits)
            docs_ok = docs.get("error") is None and (
                (isinstance(sections, list) and len(sections) > 0)
                or (bool(env_docs.get("ok")) and n_hits > 0)
            )
            record(
                "unica.docs query=НаборЗаписей",
                "completed docs result with sections (poll task.result if working)",
                f"ok={env_docs.get('ok')} task={task.get('status')} sections={len(sections) if isinstance(sections, list) else type(sections).__name__} statuses={statuses} hits={n_hits} summary={env_docs.get('summary')}",
                docs_ok,
                {"taskId": task_id, "task_status": task.get("status")},
            )

            docs_blank = call_tool(client, "unica.docs", {"query": "   "}, timeout=30)
            dump_json("r01-mcp-docs-blank-simple.json", docs_blank)
            env_blank = extract_envelope(docs_blank)
            blob_blank = envelope_blob(env_blank).lower()
            blank_ok = env_blank.get("ok") is not True and (
                "blank" in blob_blank or "non-blank" in blob_blank or "empty" in blob_blank or "query" in blob_blank
            )
            record(
                "unica.docs blank query",
                "refusal for blank query",
                f"ok={env_blank.get('ok')} summary={env_blank.get('summary')} rpc_error={docs_blank.get('error') is not None}",
                blank_ok,
            )
    except Exception as exc:
        record("smoke-exception", "no exception", repr(exc), False)
    finally:
        try:
            if proc.stdin:
                proc.stdin.close()
        except Exception:
            pass
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        stderr_f.close()
        killed = kill_daemon(STATE)
        after = fingerprint_dump(DUMP)
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        unchanged = not changed
        record(
            "dump fingerprint unchanged",
            "no files added/removed/modified under dump (excluding .build/.code-index)",
            f"changed={changed[:12]} count={len(changed)} files_before={len(before)}",
            unchanged,
        )
        dump_json(
            f"{LOG_PREFIX}-simple.json",
            {
                "binary": str(BINARY),
                "dump": str(DUMP),
                "state": str(STATE),
                "checks": checks,
                "failed": failed if unchanged else failed + (0 if any(c["name"] == "dump fingerprint unchanged" and c["pass"] for c in checks) else 0),
                "killed_daemon_pids": killed,
                "stderr_log": str(stderr_path),
                "changed_files": changed,
            },
        )

    print(f"RESULT failed={failed} total={len(checks)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
