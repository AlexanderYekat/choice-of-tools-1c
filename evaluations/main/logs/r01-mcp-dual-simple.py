"""Dual-workspace stdio MCP smoke for r01 Unica.

Two dump cwd values, one UNICA_PROVIDER_STATE_DIR. No apply, no unica.run,
no facade, no 1C client. Endpoint tokens are not written to logs.
"""
from __future__ import annotations

import hashlib
import json
import os
import queue
import signal
import struct
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

ROOT = Path(r"C:\MyProjects\choice-of-tools-1c")
BINARY = ROOT / ".v8" / "work" / "r01" / "target" / "debug" / "unica.exe"
DUMP_A = ROOT / "source-checkouts" / "simple1CAiConf"
DUMP_B = ROOT / ".v8" / "work" / "simple-cf-220"
WORK = ROOT / ".v8" / "work" / "r01-dual"
STATE = WORK / "provider-state"
LOGS_OUT = ROOT / "evaluations" / "main" / "logs"
PLUGIN_ROOT = ROOT / ".v8" / "work" / "r01" / "unica-src" / "plugins" / "unica"
DOC_REL = Path("Documents") / "ЗаказПокупателя.xml"
AT_DOC = "main:Document.ЗаказПокупателя"
COMMENT_B = "r01-publish-ifRev-20260921"


def dump_json(name: str, value: Any) -> None:
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    (LOGS_OUT / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


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
    return result if isinstance(result, dict) else {}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprints() -> dict[str, str]:
    return {
        "handwritten": file_sha256(DUMP_A / DOC_REL),
        "cf220": file_sha256(DUMP_B / DOC_REL),
    }


def same_path(left: str, right: Path) -> bool:
    try:
        return Path(left).resolve().as_posix().casefold() == right.resolve().as_posix().casefold()
    except OSError:
        return left.casefold() == str(right).casefold()


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
                raise RuntimeError(
                    f"unica stdout closed before id={req_id}; exit={self.proc.poll()}"
                )
            value = json.loads(line)
            if value.get("id") != req_id:
                continue
            return value


def call_tool(client: UnicaClient, name: str, arguments: dict[str, Any], timeout: float) -> dict[str, Any]:
    return client.request("tools/call", {"name": name, "arguments": arguments}, timeout)


def redact_endpoint(data: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(data)
    for key in ("token", "instance_id"):
        if key in redacted:
            redacted[key] = "<redacted>"
    return redacted


def read_endpoints(state_root: Path) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if not state_root.exists():
        return found
    for endpoint in state_root.rglob("endpoint.json"):
        try:
            data = json.loads(endpoint.read_text(encoding="utf-8"))
        except Exception as exc:
            found.append({"path": str(endpoint), "error": repr(exc)})
            continue
        if not isinstance(data, dict):
            found.append({"path": str(endpoint), "error": "not an object"})
            continue
        item = redact_endpoint(data)
        item["path"] = str(endpoint)
        found.append(item)
    return found


def unique_pids(endpoints: list[dict[str, Any]]) -> list[int]:
    pids: list[int] = []
    for item in endpoints:
        pid = item.get("pid")
        if isinstance(pid, int) and pid > 0 and pid not in pids:
            pids.append(pid)
    return pids


def request_scope_hash(workspace_hint: str) -> str:
    raw = workspace_hint.encode("utf-8")
    digest = hashlib.sha256()
    digest.update(b"unica.request-scope.v1\0")
    digest.update(struct.pack(">I", len(raw)))
    digest.update(raw)
    return digest.hexdigest()


def daemon_processes(state_root: Path) -> list[dict[str, Any]]:
    probe = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name = 'unica.exe'\" | "
            "Select-Object ProcessId, ParentProcessId, CommandLine | ConvertTo-Json -Compress",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    text = (probe.stdout or "").strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return [{"error": "process list was not JSON", "stdout": text[:500]}]
    rows = parsed if isinstance(parsed, list) else [parsed]
    needle = str(state_root).casefold()
    found: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        command = str(row.get("CommandLine") or "")
        if "--daemon" not in command or needle not in command.casefold():
            continue
        found.append(
            {
                "pid": row.get("ProcessId"),
                "parent": row.get("ParentProcessId"),
                "command": command,
            }
        )
    return found


def daemon_pids(state_root: Path) -> list[int]:
    pids: list[int] = []
    for item in daemon_processes(state_root):
        pid = item.get("pid")
        if isinstance(pid, int) and pid > 0 and pid not in pids:
            pids.append(pid)
    return pids


def receipt_scopes(state_root: Path) -> dict[str, Any]:
    identities: list[str] = []
    scopes: list[str] = []
    count = 0
    if not state_root.exists():
        return {"count": 0, "identities": [], "scopes": []}
    for path in state_root.rglob("receipts/active/*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        key = data.get("k") if isinstance(data, dict) else None
        if not isinstance(key, dict):
            continue
        count += 1
        identity = key.get("coreIdentityDigest")
        scope = key.get("requestScopeHash")
        if isinstance(identity, str) and identity not in identities:
            identities.append(identity)
        if isinstance(scope, str) and scope not in scopes:
            scopes.append(scope)
    return {"count": count, "identities": identities, "scopes": scopes}


def kill_daemon(state_root: Path) -> list[int]:
    killed: list[int] = []
    candidates = daemon_pids(state_root)
    for pid in unique_pids(read_endpoints(state_root)):
        if pid not in candidates:
            candidates.append(pid)
    for pid in candidates:
        if pid in killed:
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append(pid)
        except OSError:
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F", "/T"],
                    capture_output=True,
                    check=False,
                )
                killed.append(pid)
            except Exception:
                pass
    return killed


def close_proc(proc: subprocess.Popen[str] | None) -> None:
    if proc is None:
        return
    try:
        if proc.stdin:
            proc.stdin.close()
    except Exception:
        pass
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()


def start_client(cwd: Path, stderr_path: Path, env: dict[str, str]) -> tuple[subprocess.Popen[str], UnicaClient, Any]:
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_f = stderr_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(BINARY)],
        cwd=str(cwd),
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=stderr_f,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )
    return proc, UnicaClient(proc), stderr_f


def initialize(client: UnicaClient, timeout: float) -> dict[str, Any]:
    init = client.request(
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "r01-dual", "version": "0"},
        },
        timeout=timeout,
    )
    client.notify("notifications/initialized", {})
    return init


def props_comment(env: dict[str, Any]) -> Any:
    data = env.get("data") if isinstance(env.get("data"), dict) else {}
    props = data.get("props") if isinstance(data.get("props"), dict) else {}
    return props.get("Comment")


def workspace_root(env: dict[str, Any]) -> str:
    data = env.get("data") if isinstance(env.get("data"), dict) else {}
    root = data.get("workspaceRoot")
    return root if isinstance(root, str) else ""


def main() -> int:
    if not BINARY.is_file():
        print(f"MISSING BINARY {BINARY}", file=sys.stderr)
        return 2
    for dump in (DUMP_A, DUMP_B):
        if not (dump / "Configuration.xml").is_file() or not (dump / DOC_REL).is_file():
            print(f"MISSING DUMP {dump}", file=sys.stderr)
            return 2

    STATE.mkdir(parents=True, exist_ok=True)
    before = fingerprints()
    env = os.environ.copy()
    env["UNICA_PROVIDER_STATE_DIR"] = str(STATE)
    env["UNICA_DAEMON_IDLE_GRACE_MS"] = "120000"
    env["UNICA_PLUGIN_ROOT"] = str(PLUGIN_ROOT)

    checks: list[dict[str, Any]] = []
    failed = 0
    proc_a: subprocess.Popen[str] | None = None
    proc_b: subprocess.Popen[str] | None = None
    stderr_a = None
    stderr_b = None
    killed: list[int] = []

    def record(name: str, expected: str, actual: str, ok: bool, extra: Any = None) -> None:
        nonlocal failed
        checks.append({"name": name, "expected": expected, "actual": actual, "pass": ok, "extra": extra})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {actual}")
        if not ok:
            failed += 1

    try:
        proc_a, client_a, stderr_a = start_client(DUMP_A, WORK / "unica-a.stderr.log", env)
        try:
            init_a = initialize(client_a, 90)
        except TimeoutError:
            close_proc(proc_a)
            if stderr_a:
                stderr_a.close()
                stderr_a = None
            proc_a, client_a, stderr_a = start_client(DUMP_A, WORK / "unica-a-retry.stderr.log", env)
            init_a = initialize(client_a, 90)
        dump_json("r01-mcp-dual-initialize-a.json", init_a)
        server_a = ((init_a.get("result") or {}).get("serverInfo") or {})
        record(
            "initialize-a",
            "serverInfo.name=unica on handwritten dump",
            f"name={server_a.get('name')} version={server_a.get('version')} pid={proc_a.pid}",
            server_a.get("name") == "unica" and init_a.get("result") is not None,
        )

        time.sleep(0.5)
        daemons_a = daemon_processes(STATE)
        pids_a = daemon_pids(STATE)
        record(
            "daemon-after-a",
            "exactly one --daemon process for this state root",
            f"pids={pids_a}",
            len(pids_a) == 1,
            {"daemons": daemons_a},
        )

        proc_b, client_b, stderr_b = start_client(DUMP_B, WORK / "unica-b.stderr.log", env)
        init_b = initialize(client_b, 60)
        dump_json("r01-mcp-dual-initialize-b.json", init_b)
        server_b = ((init_b.get("result") or {}).get("serverInfo") or {})
        record(
            "initialize-b",
            "serverInfo.name=unica on cf220 while A is still connected",
            f"name={server_b.get('name')} version={server_b.get('version')} pid={proc_b.pid}",
            server_b.get("name") == "unica" and init_b.get("result") is not None,
        )

        time.sleep(0.5)
        daemons_b = daemon_processes(STATE)
        pids_b = daemon_pids(STATE)
        same_daemon = (
            pids_a == pids_b
            and len(pids_b) == 1
            and proc_a.pid != pids_b[0]
            and proc_b.pid != pids_b[0]
        )
        record(
            "daemon-shared",
            "same single daemon pid; both stdio pids differ from it",
            f"before={pids_a} after={pids_b} stdio=[{proc_a.pid},{proc_b.pid}]",
            same_daemon,
            {"daemons": daemons_b},
        )

        view_a = call_tool(client_a, "unica.view", {}, timeout=120)
        dump_json("r01-mcp-dual-view-a.json", view_a)
        env_a = extract_envelope(view_a)
        root_a = workspace_root(env_a)
        record(
            "view-workspace-a",
            "workspaceRoot is handwritten simple1CAiConf",
            f"ok={env_a.get('ok')} root={root_a}",
            bool(env_a.get("ok")) and same_path(root_a, DUMP_A),
        )

        view_b = call_tool(client_b, "unica.view", {}, timeout=120)
        dump_json("r01-mcp-dual-view-b.json", view_b)
        env_b = extract_envelope(view_b)
        root_b = workspace_root(env_b)
        record(
            "view-workspace-b",
            "workspaceRoot is simple-cf-220",
            f"ok={env_b.get('ok')} root={root_b}",
            bool(env_b.get("ok")) and same_path(root_b, DUMP_B),
        )

        doc_a = call_tool(client_a, "unica.view", {"at": AT_DOC}, timeout=120)
        dump_json("r01-mcp-dual-doc-a.json", doc_a)
        env_doc_a = extract_envelope(doc_a)
        comment_a = props_comment(env_doc_a)
        rev_a = env_doc_a.get("rev")
        record(
            "view-comment-a",
            "handwritten document Comment is empty",
            f"ok={env_doc_a.get('ok')} comment={comment_a!r} rev={rev_a}",
            bool(env_doc_a.get("ok")) and comment_a == "",
        )

        doc_b = call_tool(client_b, "unica.view", {"at": AT_DOC}, timeout=120)
        dump_json("r01-mcp-dual-doc-b.json", doc_b)
        env_doc_b = extract_envelope(doc_b)
        comment_b = props_comment(env_doc_b)
        rev_b = env_doc_b.get("rev")
        record(
            "view-comment-b",
            f"cf220 document Comment is {COMMENT_B}",
            f"ok={env_doc_b.get('ok')} comment={comment_b!r} rev={rev_b}",
            bool(env_doc_b.get("ok")) and comment_b == COMMENT_B and rev_a != rev_b,
        )

        doc_a2 = call_tool(client_a, "unica.view", {"at": AT_DOC}, timeout=120)
        dump_json("r01-mcp-dual-doc-a-again.json", doc_a2)
        env_doc_a2 = extract_envelope(doc_a2)
        comment_a2 = props_comment(env_doc_a2)
        record(
            "view-comment-a-again",
            "handwritten Comment stays empty after cf220 view",
            f"ok={env_doc_a2.get('ok')} comment={comment_a2!r} rev={env_doc_a2.get('rev')}",
            bool(env_doc_a2.get("ok")) and comment_a2 == "" and env_doc_a2.get("rev") == rev_a,
        )

        scopes = receipt_scopes(STATE)
        expected_scopes = {request_scope_hash(str(DUMP_A)), request_scope_hash(str(DUMP_B))}
        observed_scopes = set(scopes["scopes"])
        record(
            "receipt-scopes",
            "one core identity and two requestScopeHash values, one per cwd",
            f"identities={scopes['identities']} scopes={scopes['scopes']} receipts={scopes['count']}",
            len(scopes["identities"]) == 1 and observed_scopes == expected_scopes,
            {"expected_scopes": sorted(expected_scopes)},
        )
    except Exception as exc:
        record("smoke-exception", "no exception", repr(exc), False)
    finally:
        close_proc(proc_b)
        close_proc(proc_a)
        if stderr_b:
            stderr_b.close()
        if stderr_a:
            stderr_a.close()
        after = fingerprints()
        unchanged = before == after
        record(
            "dumps-unchanged",
            "both document XML sha256 unchanged",
            f"before={before} after={after}",
            unchanged,
        )
        killed = kill_daemon(STATE)
        dump_json(
            "r01-mcp-dual-simple.json",
            {
                "binary": str(BINARY),
                "dump_a": str(DUMP_A),
                "dump_b": str(DUMP_B),
                "state": str(STATE),
                "checks": checks,
                "failed": failed,
                "killed_daemon_pids": killed,
                "fingerprints_before": before,
                "fingerprints_after": after,
            },
        )

    print(f"RESULT failed={failed} total={len(checks)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
