"""E3: docs / edit.view / edit.apply dryRun / static check via Unica, one process.

Measures raw response size (bytes, lines) per call for the context-budget table.
Read-only / dryRun only -- no publish.
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
WORK = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01-e3")
STATE = WORK / "provider-state"
LOGS_OUT = Path(r"C:\MyProjects\choice-of-tools-1c\evaluations\main\logs")
PLUGIN_ROOT = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01\unica-src\plugins\unica")
AT_DOC = "main:Document.ЗаказПокупателя"


def dump_json(name: str, value: Any) -> Path:
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    path = LOGS_OUT / name
    text = json.dumps(value, ensure_ascii=False, indent=2)
    path.write_text(text, encoding="utf-8")
    return path


def size_of(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    return len(text.encode("utf-8")), text.count("\n") + 1


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
    STATE.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["UNICA_PROVIDER_STATE_DIR"] = str(STATE)
    env["UNICA_DAEMON_IDLE_GRACE_MS"] = "8000"
    env["UNICA_PLUGIN_ROOT"] = str(PLUGIN_ROOT)

    stderr_path = WORK / "unica.stderr.log"
    stderr_f = stderr_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(BINARY)], cwd=str(DUMP), env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_f,
        text=True, encoding="utf-8", bufsize=1,
    )
    client = UnicaClient(proc)
    sizes: list[dict[str, Any]] = []

    def record_call(step: str, name: str, args: dict[str, Any], timeout: float, filename: str) -> dict[str, Any]:
        rpc = call_tool(client, name, args, timeout)
        path = dump_json(filename, rpc)
        b, lines = size_of(path)
        env_ = extract_envelope(rpc)
        entry = {"step": step, "tool": name, "args": args, "bytes": b, "lines": lines, "file": filename, "ok": env_.get("ok")}
        sizes.append(entry)
        print(f"[{step}] {name} bytes={b} lines={lines} ok={env_.get('ok')}")
        return rpc

    try:
        init = client.request(
            "initialize",
            {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "e3-chain", "version": "0"}},
            timeout=60,
        )
        dump_json("e3-00-initialize.json", init)
        client.notify("notifications/initialized", {})

        record_call("02-docs", "unica.docs", {"query": "НаборЗаписей"}, 120, "e3-02-docs.json")

        record_call("03-edit.view", "unica.view", {"at": AT_DOC}, 60, "e3-03-edit-view.json")

        record_call(
            "04-edit.apply-dryrun", "unica.apply",
            {"at": AT_DOC, "dryRun": True, "ops": [{"op": "props.set", "args": {"values": {"Comment": "e3-dryrun-preview-do-not-publish"}}}]},
            120, "e3-04-edit-apply-dryrun.json",
        )

        record_call("05-static-check", "unica.check", {"at": AT_DOC}, 60, "e3-05-static-check.json")
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
        dump_json("e3-unica-chain-sizes.json", {"sizes": sizes, "killed_daemon_pids": killed})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
