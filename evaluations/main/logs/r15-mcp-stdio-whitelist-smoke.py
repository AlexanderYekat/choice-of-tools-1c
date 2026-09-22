"""E4: r15 bsl-indexer stdio transport -- [tools].enabled whitelist,
and whether --path + --config together makes --path win (config, and
its whitelist, ignored) as `serve --help` warns.

Isolated CODE_INDEX_HOME. Dump-only. No infobase, no facade.
"""
from __future__ import annotations

import json
import os
import queue
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
BINARY = Path(r"C:\Users\Enduro\Documents\1c\Tools\bsl-indexer\bsl-indexer.exe")
DUMP = ROOT / r"source-checkouts\simple1CAiConf"
WORK = ROOT / r".v8\work\r15-stdio-whitelist"
HOME = WORK / "home"
LOGS = ROOT / r"evaluations\main\logs"
ALIAS = "simple"

ALLOWED = [
    "search_function", "get_function", "get_callers", "read_file",
    "get_object_profile", "get_form_handlers", "get_event_subscriptions",
    "get_register_writers", "find_references",
]
TYPO = "not_a_real_tool"


def dump_json(name: str, value: Any) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


class StdioClient:
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
                raise RuntimeError(f"stdout closed before id={req_id}; exit={self.proc.poll()}")
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if value.get("id") != req_id:
                continue
            return value


def run_stdio_session(args: list[str], env: dict[str, str], label: str, log_path: Path) -> dict[str, Any]:
    stderr_f = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(BINARY), *args], cwd=str(WORK), env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_f,
        text=True, encoding="utf-8", bufsize=1,
    )
    client = StdioClient(proc)
    out: dict[str, Any] = {"label": label, "args": args}
    try:
        init = client.request(
            "initialize",
            {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": f"e4-{label}", "version": "0"}},
            timeout=30,
        )
        out["initialize"] = init
        client.notify("notifications/initialized", {})
        listed = client.request("tools/list", None, timeout=30)
        out["tools_list"] = listed
        tools = ((listed.get("result") or {}).get("tools")) or []
        names = sorted(str(t.get("name")) for t in tools if isinstance(t, dict))
        out["names"] = names
        out["count"] = len(names)

        # try calling one allowed and one disallowed tool for confirmation
        call_allowed = client.request(
            "tools/call",
            {"name": "search_function", "arguments": {"repo": ALIAS, "query": "РассчитатьСумму"}},
            timeout=30,
        )
        out["call_search_function"] = call_allowed

        call_denied = client.request(
            "tools/call",
            {"name": "grep_code", "arguments": {"repo": ALIAS, "pattern": "Сумма"}},
            timeout=30,
        )
        out["call_grep_code"] = call_denied
    except Exception as exc:
        out["exception"] = repr(exc)
    finally:
        try:
            if proc.stdin:
                proc.stdin.close()
        except Exception:
            pass
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        stderr_f.close()
    return out


def main() -> int:
    if not BINARY.is_file():
        print(f"missing binary {BINARY}")
        return 2
    HOME.mkdir(parents=True, exist_ok=True)
    dump_posix = DUMP.resolve().as_posix()
    enabled = ALLOWED + [TYPO]
    config = HOME / "daemon.toml"
    config.write_text(
        "\n".join([
            "[[paths]]", f'path = "{dump_posix}"', f'alias = "{ALIAS}"', 'language = "bsl"', "",
            "[tools]", "enabled = [", *[f'  "{name}",' for name in enabled], "]", "",
        ]),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["CODE_INDEX_HOME"] = str(HOME)
    env["RUST_LOG"] = "info"

    def run_daemon(args: list[str], log_path: Path, timeout: int) -> subprocess.CompletedProcess[str]:
        with log_path.open("w", encoding="utf-8") as handle:
            return subprocess.run(
                [str(BINARY), *args], cwd=str(WORK), env=env,
                stdout=handle, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", timeout=timeout,
            )

    checks: list[dict[str, Any]] = []

    def record(name: str, expected: str, actual: str, ok: bool) -> None:
        checks.append({"name": name, "expected": expected, "actual": actual, "pass": ok})
        print(f"{'PASS' if ok else 'FAIL'} {name}: {actual}")

    try:
        run_daemon(["daemon", "stop"], WORK / "daemon-stop-before.log", 30)
    except Exception:
        pass
    started = run_daemon(["daemon", "run"], WORK / "daemon-run.log", 60)
    record("daemon run", "exit 0/None", f"exit {started.returncode}", started.returncode in (0, None))

    online = False
    status_text = ""
    for _ in range(30):
        status = subprocess.run(
            [str(BINARY), "daemon", "status"], cwd=str(WORK), env=env,
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
        )
        status_text = (status.stdout or "") + (status.stderr or "")
        if "online" in status_text.lower() or "ready" in status_text.lower():
            online = True
            break
        time.sleep(0.5)
    record("daemon online", "status mentions online/ready", status_text.strip()[:300], online)

    # Session A: stdio, --config only (whitelist should apply)
    result_a = run_stdio_session(
        ["serve", "--transport", "stdio", "--config", str(config)],
        env, "config-only", WORK / "session-a-stderr.log",
    )
    dump_json("r15-mcp-stdio-whitelist-session-a.json", result_a)
    names_a = result_a.get("names") or []
    record(
        "A: stdio --config only -> whitelist applies (9 names)",
        "count=9, matches ALLOWED",
        f"count={result_a.get('count')} names={names_a}",
        sorted(names_a) == sorted(ALLOWED),
    )
    denied_a = result_a.get("call_grep_code") or {}
    denied_a_text = json.dumps(denied_a, ensure_ascii=False)
    record(
        "A: grep_code call refused by whitelist",
        "error mentioning disabled/whitelist",
        denied_a_text[:200],
        "disabled" in denied_a_text.lower() or "whitelist" in denied_a_text.lower() or "-32602" in denied_a_text,
    )

    # Session B: stdio, --config AND --path together (per --help, --path should win, config+whitelist ignored)
    result_b = run_stdio_session(
        ["serve", "--transport", "stdio", "--config", str(config), "--path", dump_posix],
        env, "config-and-path", WORK / "session-b-stderr.log",
    )
    dump_json("r15-mcp-stdio-whitelist-session-b.json", result_b)
    names_b = result_b.get("names") or []
    record(
        "B: stdio --config + --path -> --path wins, whitelist ignored (more than 9 names)",
        "count > 9 (full tool set, not the whitelist)",
        f"count={result_b.get('count')} names={names_b}",
        len(names_b) > len(ALLOWED),
    )
    denied_b = result_b.get("call_grep_code") or {}
    denied_b_text = json.dumps(denied_b, ensure_ascii=False)
    record(
        "B: grep_code call now succeeds (not whitelist-refused)",
        "no disabled/whitelist refusal",
        denied_b_text[:200],
        "disabled" not in denied_b_text.lower() and "whitelist" not in denied_b_text.lower(),
    )

    try:
        run_daemon(["daemon", "stop"], WORK / "daemon-stop-after.log", 30)
    except Exception:
        pass

    failed = sum(1 for c in checks if not c["pass"])
    dump_json("r15-mcp-stdio-whitelist-simple.json", {"checks": checks, "failed": failed})
    print(f"RESULT failed={failed} total={len(checks)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
