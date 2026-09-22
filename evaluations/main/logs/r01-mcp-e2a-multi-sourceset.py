"""E2a: two source-sets (main, cf220) in one v8project.yaml, one Unica process.

Read-only (view only, no apply). Confirms:
- unica.view {} lists both source-sets from a single cwd/process.
- at="main:..." and at="cf220:..." resolve to their own dump, distinctly.
- at="bogus:..." gives a named refusal, not a silent default to "main".
- neither dump's files change (sha256 fingerprint before/after).
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
CWD = Path(r"C:\MyProjects\choice-of-tools-1c")
MAIN_DUMP = Path(r"C:\MyProjects\choice-of-tools-1c\source-checkouts\simple1CAiConf")
CF220_DUMP = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\simple-cf-220")
WORK = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01-e2a")
STATE = WORK / "provider-state"
LOGS_OUT = Path(r"C:\MyProjects\choice-of-tools-1c\evaluations\main\logs")
PLUGIN_ROOT = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01\unica-src\plugins\unica")
LOG_PREFIX = "r01-mcp-e2a"
SKIP_DUMP_DIRS = {".build", ".code-index", ".git"}


def dump_json(name: str, value: Any) -> None:
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    (LOGS_OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


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
        files[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
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
    return client.request("tools/call", {"name": name, "arguments": arguments}, timeout)


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
    if not (CWD / "v8project.yaml").is_file():
        print(f"MISSING CONFIG {CWD / 'v8project.yaml'}", file=sys.stderr)
        return 2

    STATE.mkdir(parents=True, exist_ok=True)
    before_main = fingerprint_dump(MAIN_DUMP)
    before_cf220 = fingerprint_dump(CF220_DUMP)

    env = os.environ.copy()
    env["UNICA_PROVIDER_STATE_DIR"] = str(STATE)
    env["UNICA_DAEMON_IDLE_GRACE_MS"] = "8000"
    env["UNICA_PLUGIN_ROOT"] = str(PLUGIN_ROOT)

    stderr_path = WORK / "unica.stderr.log"
    stderr_f = stderr_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(BINARY)],
        cwd=str(CWD),
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
            {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "r01-e2a", "version": "0"}},
            timeout=60,
        )
        dump_json(f"{LOG_PREFIX}-initialize.json", init)
        server = ((init.get("result") or {}).get("serverInfo") or {})
        record("initialize", "serverInfo.name=unica", f"name={server.get('name')}", server.get("name") == "unica")
        client.notify("notifications/initialized", {})

        root = call_tool(client, "unica.view", {}, timeout=120)
        dump_json(f"{LOG_PREFIX}-view-root.json", root)
        env_root = extract_envelope(root)
        blob_root = envelope_blob(env_root)
        has_both = "main" in blob_root and "cf220" in blob_root
        record(
            "unica.view {} lists both source-sets from one process",
            "response mentions both 'main' and 'cf220'",
            f"has_main_and_cf220={has_both} keys={list(env_root.keys())}",
            has_both,
            env_root,
        )

        doc_main = call_tool(client, "unica.view", {"at": "main:Document.ЗаказПокупателя"}, timeout=120)
        dump_json(f"{LOG_PREFIX}-view-main-doc.json", doc_main)
        env_main = extract_envelope(doc_main)
        main_ok = doc_main.get("error") is None and bool(env_main)
        record(
            "unica.view at=main:Document.ЗаказПокупателя",
            "resolves within main source-set",
            f"ok={env_main.get('ok')} error={doc_main.get('error')}",
            main_ok,
        )

        doc_cf220 = call_tool(client, "unica.view", {"at": "cf220:Document.ЗаказПокупателя"}, timeout=120)
        dump_json(f"{LOG_PREFIX}-view-cf220-doc.json", doc_cf220)
        env_cf220 = extract_envelope(doc_cf220)
        cf220_ok = doc_cf220.get("error") is None and bool(env_cf220)
        record(
            "unica.view at=cf220:Document.ЗаказПокупателя",
            "resolves within cf220 source-set, distinct dump",
            f"ok={env_cf220.get('ok')} error={doc_cf220.get('error')}",
            cf220_ok,
        )

        distinct = envelope_blob(env_main) != envelope_blob(env_cf220)
        record(
            "main and cf220 views are distinct payloads",
            "not byte-identical (different dumps, same logical address)",
            f"distinct={distinct}",
            distinct,
        )

        bogus = call_tool(client, "unica.view", {"at": "bogus:Document.ЗаказПокупателя"}, timeout=60)
        dump_json(f"{LOG_PREFIX}-view-bogus.json", bogus)
        env_bogus = extract_envelope(bogus)
        blob_bogus = envelope_blob(env_bogus).lower()
        bogus_named_refusal = (
            env_bogus.get("ok") is not True
            and ("bogus" in blob_bogus or "source" in blob_bogus or "not found" in blob_bogus or "unknown" in blob_bogus)
        )
        record(
            "unica.view at=bogus:... (unknown source-set)",
            "named refusal, not a silent default to 'main'",
            f"ok={env_bogus.get('ok')} summary={env_bogus.get('summary')} blob={blob_bogus[:200]}",
            bogus_named_refusal,
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
        after_main = fingerprint_dump(MAIN_DUMP)
        after_cf220 = fingerprint_dump(CF220_DUMP)
        changed_main = sorted(k for k in set(before_main) | set(after_main) if before_main.get(k) != after_main.get(k))
        changed_cf220 = sorted(k for k in set(before_cf220) | set(after_cf220) if before_cf220.get(k) != after_cf220.get(k))
        record(
            "main dump fingerprint unchanged",
            "no files added/removed/modified",
            f"changed={changed_main[:12]} count={len(changed_main)}",
            not changed_main,
        )
        record(
            "cf220 dump fingerprint unchanged",
            "no files added/removed/modified",
            f"changed={changed_cf220[:12]} count={len(changed_cf220)}",
            not changed_cf220,
        )
        dump_json(
            f"{LOG_PREFIX}-simple.json",
            {
                "binary": str(BINARY),
                "cwd": str(CWD),
                "checks": checks,
                "failed": failed,
                "killed_daemon_pids": killed,
                "stderr_log": str(stderr_path),
            },
        )

    print(f"RESULT failed={failed} total={len(checks)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
