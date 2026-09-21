"""Dump-only stdio MCP smoke for r01 Unica on simple1CAiConf.

Isolated UNICA_PROVIDER_STATE_DIR. No apply, no unica.run, no facade.
"""
from __future__ import annotations

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
DUMP = Path(r"C:\MyProjects\choice-of-tools-1c\source-checkouts\simple1CAiConf")
WORK = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01")
STATE = WORK / "provider-state"
LOGS_OUT = Path(r"C:\MyProjects\choice-of-tools-1c\evaluations\main\logs")
PLUGIN_ROOT = WORK / "unica-src" / "plugins" / "unica"

EXPECTED_TOOLS = [
    "unica.view",
    "unica.apply",
    "unica.resolve",
    "unica.search",
    "unica.check",
    "unica.diff",
    "unica.run",
    "unica.docs",
    "unica.task.get",
    "unica.task.result",
    "unica.task.cancel",
]

DOCUMENT_NAME = "ЗаказПокупателя"
ATTR = "СуммаДокумента"
TABLE = "Товары"


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
    return result if isinstance(result, dict) else {}


def envelope_blob(env: dict[str, Any]) -> str:
    return json.dumps(env, ensure_ascii=False)


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
                "clientInfo": {"name": "r01-smoke", "version": "0"},
            },
            timeout=60,
        )
        dump_json("r01-mcp-initialize-simple.json", init)
        server = ((init.get("result") or {}).get("serverInfo") or {})
        record(
            "initialize",
            "serverInfo.name=unica",
            f"name={server.get('name')} version={server.get('version')}",
            server.get("name") == "unica" and init.get("result") is not None,
            {"protocolVersion": (init.get("result") or {}).get("protocolVersion")},
        )
        client.notify("notifications/initialized", {})

        listed = client.request("tools/list", {}, timeout=30)
        dump_json("r01-mcp-tools-list-simple.json", listed)
        names = [
            tool.get("name")
            for tool in ((listed.get("result") or {}).get("tools") or [])
            if isinstance(tool, dict)
        ]
        missing = [n for n in EXPECTED_TOOLS if n not in names]
        unexpected = [n for n in names if n not in EXPECTED_TOOLS]
        record(
            "tools/list",
            "exactly 11 compatibility tools",
            f"count={len(names)} missing={missing} unexpected={unexpected}",
            names == EXPECTED_TOOLS or (not missing and not unexpected and len(names) == 11),
            {"names": names},
        )

        view_ws = call_tool(client, "unica.view", {}, timeout=120)
        dump_json("r01-mcp-view-workspace-simple.json", view_ws)
        env_ws = extract_envelope(view_ws)
        blob_ws = envelope_blob(env_ws)
        data = env_ws.get("data") if isinstance(env_ws.get("data"), dict) else {}
        config = data.get("config") if isinstance(data.get("config"), dict) else {}
        source_sets = data.get("sourceSets") or data.get("source_sets") or []
        config_state = config.get("state") or data.get("configState") or data.get("state")
        workspace_ok = bool(env_ws.get("ok")) and (
            config_state in {"autodetected", "configured"}
            or "autodetect" in blob_ws.lower()
            or bool(source_sets)
        )
        record(
            "unica.view {}",
            "ok workspace bootstrap; config.state autodetected|configured",
            f"ok={env_ws.get('ok')} configState={config_state} summary={env_ws.get('summary')}",
            workspace_ok,
            {"envelope_keys": list(env_ws.keys())},
        )

        source_set = None
        if isinstance(source_sets, list) and source_sets:
            first = source_sets[0]
            if isinstance(first, dict):
                source_set = first.get("name") or first.get("id")
            elif isinstance(first, str):
                source_set = first
        if not source_set:
            for key in ("effectiveSourceSet", "sourceSet", "selectedSourceSet"):
                if isinstance(data.get(key), str):
                    source_set = data[key]
                    break
        if not source_set:
            # Autodetected base configuration uses the reserved name `main`.
            source_set = "main"

        at_doc = f"{source_set}:Document.{DOCUMENT_NAME}"
        view_doc = call_tool(client, "unica.view", {"at": at_doc}, timeout=120)
        dump_json("r01-mcp-view-document-simple.json", view_doc)
        env_doc = extract_envelope(view_doc)
        blob_doc = envelope_blob(env_doc)
        record(
            f"unica.view at={at_doc}",
            f"readable document with {ATTR} and/or {TABLE}",
            f"ok={env_doc.get('ok')} summary={env_doc.get('summary')}",
            bool(env_doc.get("ok")) and (ATTR in blob_doc or TABLE in blob_doc or DOCUMENT_NAME in blob_doc),
        )

        check_doc = call_tool(client, "unica.check", {"at": at_doc}, timeout=180)
        dump_json("r01-mcp-check-document-simple.json", check_doc)
        env_chk = extract_envelope(check_doc)
        # Admission/readability of a known node: ok=true, or structured diagnostics
        # without a transport-level JSON-RPC error.
        check_ok = check_doc.get("error") is None and (
            env_chk.get("ok") is True or isinstance(env_chk.get("diagnostics"), list)
        )
        record(
            f"unica.check at={at_doc}",
            "node readable / validated (ok or diagnostics)",
            f"ok={env_chk.get('ok')} summary={env_chk.get('summary')} rpc_error={check_doc.get('error')}",
            check_ok,
        )

        bogus_at = f"{source_set}:Document.НесуществующийОбъектXYZ"
        view_bad = call_tool(client, "unica.view", {"at": bogus_at}, timeout=60)
        dump_json("r01-mcp-view-missing-simple.json", view_bad)
        env_bad = extract_envelope(view_bad)
        negative_ok = view_bad.get("error") is not None or env_bad.get("ok") is False
        record(
            f"unica.view at={bogus_at}",
            "refusal for missing object",
            f"ok={env_bad.get('ok')} rpc_error={view_bad.get('error') is not None} summary={env_bad.get('summary')}",
            negative_ok,
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
        dump_json(
            "r01-mcp-simple.json",
            {
                "binary": str(BINARY),
                "dump": str(DUMP),
                "state": str(STATE),
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
