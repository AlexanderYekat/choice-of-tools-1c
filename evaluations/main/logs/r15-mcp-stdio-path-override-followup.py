"""E4 follow-up: distinguish 'path overrides config' from 'whitelist merges
regardless' by using a DIFFERENT alias on --path than the config's [[paths]]
alias. If --path truly wins/config is ignored, the config's alias 'simple'
should NOT resolve and only 'other' (from --path) should.
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


def dump_json(name: str, value: Any) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


class StdioClient:
    def __init__(self, proc: subprocess.Popen[str]) -> None:
        self.proc = proc
        self._next_id = 1
        self._lines: queue.Queue[str | None] = queue.Queue()
        threading.Thread(target=self._pump, daemon=True).start()

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
        self.send({"jsonrpc": "2.0", "method": method, **({"params": params} if params is not None else {})})

    def request(self, method: str, params: dict[str, Any] | None, timeout: float) -> dict[str, Any]:
        req_id = self._next_id
        self._next_id += 1
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            payload["params"] = params
        self.send(payload)
        deadline = time.time() + timeout
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError(f"timed out waiting for id={req_id}")
            try:
                line = self._lines.get(timeout=remaining)
            except queue.Empty as exc:
                raise TimeoutError(f"timed out waiting for id={req_id}") from exc
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


def main() -> int:
    env = os.environ.copy()
    env["CODE_INDEX_HOME"] = str(HOME)
    env["RUST_LOG"] = "info"
    config = HOME / "daemon.toml"  # still the same config from the previous run: alias "simple", whitelist of 9

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
        run_daemon(["daemon", "stop"], WORK / "followup-stop-before.log", 30)
    except Exception:
        pass
    started = run_daemon(["daemon", "run"], WORK / "followup-daemon-run.log", 60)
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
    record("daemon online", "mentions online/ready", status_text.strip()[:300], online)

    # --path with a DIFFERENT alias "other" than config's "simple", same dump directory
    dump_posix = DUMP.resolve().as_posix()
    stderr_f = (WORK / "followup-session-stderr.log").open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(BINARY), "serve", "--transport", "stdio", "--config", str(config), "--path", f"other={dump_posix}"],
        cwd=str(WORK), env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_f,
        text=True, encoding="utf-8", bufsize=1,
    )
    client = StdioClient(proc)
    out: dict[str, Any] = {}
    try:
        init = client.request(
            "initialize",
            {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "e4-followup", "version": "0"}},
            timeout=30,
        )
        out["initialize"] = init
        client.notify("notifications/initialized", {})
        listed = client.request("tools/list", None, timeout=30)
        out["tools_list"] = listed
        tools = ((listed.get("result") or {}).get("tools")) or []
        names = sorted(str(t.get("name")) for t in tools if isinstance(t, dict))
        out["names"] = names
        record(
            "tools/list with --path other=... + --config (alias=simple)",
            "9 names (whitelist) or 13/33 (no whitelist) -- either way, decides the merge question",
            f"count={len(names)} names={names}",
            True,
        )

        # try alias "simple" (from config) -- does it resolve, or only "other" (from --path)?
        call_simple = client.request(
            "tools/call", {"name": "search_function", "arguments": {"repo": "simple", "query": "РассчитатьСумму"}}, timeout=30,
        )
        out["call_repo_simple"] = call_simple
        simple_text = json.dumps(call_simple, ensure_ascii=False)
        record(
            "repo=simple (config's alias) resolves?",
            "either resolves (config paths kept) or errors unknown-repo (config paths dropped)",
            simple_text[:300],
            True,
        )

        call_other = client.request(
            "tools/call", {"name": "search_function", "arguments": {"repo": "other", "query": "РассчитатьСумму"}}, timeout=30,
        )
        out["call_repo_other"] = call_other
        other_text = json.dumps(call_other, ensure_ascii=False)
        record(
            "repo=other (--path's alias) resolves?",
            "resolves (CLI --path always wins for path resolution)",
            other_text[:300],
            True,
        )
    except Exception as exc:
        out["exception"] = repr(exc)
        record("session exception", "none", repr(exc), False)
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

    dump_json("r15-mcp-stdio-path-override-followup.json", out)

    try:
        run_daemon(["daemon", "stop"], WORK / "followup-stop-after.log", 30)
    except Exception:
        pass

    failed = sum(1 for c in checks if not c["pass"])
    dump_json("r15-mcp-stdio-path-override-followup-checks.json", {"checks": checks, "failed": failed})
    print(f"RESULT failed={failed} total={len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
