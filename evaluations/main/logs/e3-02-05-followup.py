"""E3 follow-up: poll docs to completion; redo apply dryRun + check on cf220 (2.20)."""
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
LOGS_OUT = Path(r"C:\MyProjects\choice-of-tools-1c\evaluations\main\logs")
PLUGIN_ROOT = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01\unica-src\plugins\unica")


def dump_json(name: str, value: Any) -> Path:
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    path = LOGS_OUT / name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def size_of(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    return len(text.encode("utf-8")), text.count("\n") + 1


def extract_envelope(rpc: dict[str, Any]) -> dict[str, Any]:
    result = rpc.get("result") or {}
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured
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


def run_process(cwd: Path, work: Path, calls: list[tuple[str, str, dict, float, str]]) -> list[dict]:
    state = work / "provider-state"
    state.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["UNICA_PROVIDER_STATE_DIR"] = str(state)
    env["UNICA_DAEMON_IDLE_GRACE_MS"] = "8000"
    env["UNICA_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    stderr_path = work / "unica.stderr.log"
    stderr_f = stderr_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(BINARY)], cwd=str(cwd), env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_f,
        text=True, encoding="utf-8", bufsize=1,
    )
    client = UnicaClient(proc)
    sizes: list[dict[str, Any]] = []
    try:
        init = client.request(
            "initialize",
            {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "e3-followup", "version": "0"}},
            timeout=60,
        )
        client.notify("notifications/initialized", {})
        for step, tool, args, timeout, filename in calls:
            rpc = call_tool(client, tool, args, timeout)
            path = dump_json(filename, rpc)
            b, lines = size_of(path)
            env_ = extract_envelope(rpc)
            entry = {"step": step, "tool": tool, "bytes": b, "lines": lines, "file": filename, "ok": env_.get("ok"), "summary": env_.get("summary")}
            sizes.append(entry)
            print(f"[{step}] {tool} bytes={b} lines={lines} ok={env_.get('ok')} summary={env_.get('summary')}")
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
        kill_daemon(state)
    return sizes


def main() -> int:
    all_sizes: list[dict] = []

    # docs: poll to completion on main
    all_sizes += run_process(
        Path(r"C:\MyProjects\choice-of-tools-1c\source-checkouts\simple1CAiConf"),
        Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01-e3-docs"),
        [
            ("02-docs-start", "unica.docs", {"query": "НаборЗаписей"}, 60, "e3-02-docs-start.json"),
        ],
    )
    # Need the taskId from the start call to poll; redo inline with polling in one process.
    state = Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01-e3-docs2\provider-state")
    state.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["UNICA_PROVIDER_STATE_DIR"] = str(state)
    env["UNICA_DAEMON_IDLE_GRACE_MS"] = "8000"
    env["UNICA_PLUGIN_ROOT"] = str(PLUGIN_ROOT)
    stderr_f = (state.parent / "unica.stderr.log").open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(BINARY)], cwd=r"C:\MyProjects\choice-of-tools-1c\source-checkouts\simple1CAiConf", env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_f,
        text=True, encoding="utf-8", bufsize=1,
    )
    client = UnicaClient(proc)
    try:
        client.request("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "e3-docs-poll", "version": "0"}}, timeout=60)
        client.notify("notifications/initialized", {})
        docs = call_tool(client, "unica.docs", {"query": "НаборЗаписей"}, timeout=60)
        env_docs = extract_envelope(docs)
        data_docs = env_docs.get("data") if isinstance(env_docs.get("data"), dict) else {}
        task = data_docs.get("task") if isinstance(data_docs.get("task"), dict) else {}
        task_id = task.get("taskId")
        poll = 0
        deadline = time.time() + 35
        while isinstance(task_id, str) and task.get("status") == "working" and time.time() < deadline:
            poll += 1
            docs = call_tool(client, "unica.task.result", {"taskId": task_id, "waitMs": 5000}, timeout=15)
            env_docs = extract_envelope(docs)
            data_docs = env_docs.get("data") if isinstance(env_docs.get("data"), dict) else {}
            task = data_docs.get("task") if isinstance(data_docs.get("task"), dict) else {}
            if task.get("status") != "working":
                break
        # one more poll if still queued/working after initial deadline check
        while isinstance(task_id, str) and task.get("status") in ("queued", "working") and time.time() < deadline:
            poll += 1
            docs = call_tool(client, "unica.task.result", {"taskId": task_id, "waitMs": 5000}, timeout=15)
            env_docs = extract_envelope(docs)
            data_docs = env_docs.get("data") if isinstance(env_docs.get("data"), dict) else {}
            task = data_docs.get("task") if isinstance(data_docs.get("task"), dict) else {}
        path = dump_json("e3-02-docs-final.json", docs)
        b, lines = size_of(path)
        all_sizes.append({"step": "02-docs-final", "tool": "unica.docs(+poll)", "bytes": b, "lines": lines, "file": "e3-02-docs-final.json", "ok": env_docs.get("ok"), "polls": poll, "task_status": task.get("status")})
        print(f"[02-docs-final] polls={poll} bytes={b} lines={lines} ok={env_docs.get('ok')} status={task.get('status')}")
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
        kill_daemon(state)

    # apply dryRun + check on cf220 (2.20)
    all_sizes += run_process(
        Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\simple-cf-220"),
        Path(r"C:\MyProjects\choice-of-tools-1c\.v8\work\r01-e3-cf220"),
        [
            (
                "04-edit.apply-dryrun-cf220", "unica.apply",
                {"at": "main:Document.ЗаказПокупателя", "dryRun": True, "ops": [{"op": "props.set", "args": {"values": {"Comment": "e3-dryrun-preview-do-not-publish"}}}]},
                60, "e3-04-edit-apply-dryrun-cf220.json",
            ),
            ("05-static-check-cf220", "unica.check", {"at": "main:Document.ЗаказПокупателя"}, 60, "e3-05-static-check-cf220.json"),
        ],
    )

    dump_json("e3-followup-sizes.json", {"sizes": all_sizes})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
