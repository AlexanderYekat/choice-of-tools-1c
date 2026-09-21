"""Dump-only [tools].enabled whitelist smoke for r15 bsl-indexer 1.4.0.

Isolated CODE_INDEX_HOME. HTTP serve --config only (no --path, or the
config including [tools] is ignored). No infobase, no Unica, no facade.
Does not edit the Designer dump.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(r"C:\MyProjects\choice-of-tools-1c")
BINARY = Path(r"C:\Users\Enduro\Documents\1c\Tools\bsl-indexer\bsl-indexer.exe")
DUMP = ROOT / r"source-checkouts\simple1CAiConf"
WORK = ROOT / r".v8\work\r15-whitelist"
HOME = WORK / "home"
LOGS = ROOT / r"evaluations\main\logs"
ALIAS = "simple"

ALLOWED = [
    "search_function",
    "get_function",
    "get_callers",
    "read_file",
    "get_object_profile",
    "get_form_handlers",
    "get_event_subscriptions",
    "get_register_writers",
    "find_references",
]
TYPO = "not_a_real_tool"


def dump_json(name: str, value: Any) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def parse_body(body: str, content_type: str) -> dict[str, Any]:
    text = body.strip()
    if not text:
        return {}
    if "text/event-stream" in content_type or text.startswith("event:") or text.startswith("data:"):
        data_lines = []
        for line in text.splitlines():
            if line.startswith("data:"):
                data_lines.append(line[5:].strip())
        if not data_lines:
            return {"raw": text}
        parsed = json.loads(data_lines[-1])
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    parsed = json.loads(text)
    return parsed if isinstance(parsed, dict) else {"value": parsed}


class McpHttp:
    def __init__(self, base: str) -> None:
        self.base = base.rstrip("/")
        self.session: str | None = None
        self.url = ""
        self._id = 0

    def _post(self, url: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None, int]:
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                sid = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
                ctype = resp.headers.get("Content-Type", "")
                return parse_body(body, ctype), sid, resp.status
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            ctype = exc.headers.get("Content-Type", "") if exc.headers else ""
            try:
                parsed = parse_body(body, ctype)
            except json.JSONDecodeError:
                parsed = {"http_status": exc.code, "raw": body[:2000]}
            return parsed, None, exc.code

    def start(self) -> dict[str, Any]:
        init = {
            "jsonrpc": "2.0",
            "id": self.next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "r15-whitelist-smoke", "version": "0"},
            },
        }
        last: dict[str, Any] = {}
        for suffix in ("/mcp", ""):
            url = self.base + suffix
            parsed, sid, status = self._post(url, init)
            last = {"url": url, "status": status, "body": parsed, "session": sid}
            if status < 400 and "result" in parsed:
                self.url = url
                self.session = sid
                note = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                }
                self._post(url, note)
                return last
        raise RuntimeError(f"initialize failed: {last}")

    def next_id(self) -> int:
        self._id += 1
        return self._id

    def rpc(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": self.next_id(),
            "method": method,
        }
        if params is not None:
            payload["params"] = params
        parsed, sid, status = self._post(self.url, payload)
        if sid:
            self.session = sid
        parsed["_http_status"] = status
        return parsed


def tool_text(rpc: dict[str, Any]) -> str:
    result = rpc.get("result")
    if not isinstance(result, dict):
        return json.dumps(rpc, ensure_ascii=False)
    chunks: list[str] = []
    for block in result.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            chunks.append(str(block.get("text") or ""))
    structured = result.get("structuredContent") or result.get("structured_content")
    if isinstance(structured, dict):
        chunks.append(json.dumps(structured, ensure_ascii=False))
    return "\n".join(chunks) if chunks else json.dumps(result, ensure_ascii=False)


def main() -> int:
    if not BINARY.is_file():
        print(f"missing binary {BINARY}")
        return 2
    HOME.mkdir(parents=True, exist_ok=True)
    dump_posix = DUMP.resolve().as_posix()
    enabled = ALLOWED + [TYPO]
    config = HOME / "daemon.toml"
    config.write_text(
        "\n".join(
            [
                "[[paths]]",
                f'path = "{dump_posix}"',
                f'alias = "{ALIAS}"',
                'language = "bsl"',
                "",
                "[tools]",
                "enabled = [",
                *[f'  "{name}",' for name in enabled],
                "]",
                "",
            ]
        ),
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["CODE_INDEX_HOME"] = str(HOME)
    env["RUST_LOG"] = "info"
    port = free_port()
    serve_log = WORK / "serve.log"
    daemon_log = WORK / "daemon-run.log"

    def run_daemon(args: list[str], log_path: Path, timeout: int) -> subprocess.CompletedProcess[str]:
        with log_path.open("w", encoding="utf-8") as handle:
            return subprocess.run(
                [str(BINARY), *args],
                cwd=str(WORK),
                env=env,
                stdout=handle,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )

    serve: subprocess.Popen[str] | None = None
    serve_handle = None
    checks: list[dict[str, Any]] = []

    def record(name: str, expected: str, actual: str, ok: bool) -> None:
        checks.append({"name": name, "expected": expected, "actual": actual, "pass": ok})
        print(f"{'PASS' if ok else 'FAIL'} {name}: {actual}")

    try:
        run_daemon(["daemon", "stop"], WORK / "daemon-stop-before.log", 30)
        started = run_daemon(["daemon", "run"], daemon_log, 60)
        if started.returncode not in (0, None):
            record("daemon run", "exit 0", f"exit {started.returncode}", False)
        online = False
        status_text = ""
        for _ in range(30):
            status = subprocess.run(
                [str(BINARY), "daemon", "status"],
                cwd=str(WORK),
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
            )
            status_text = (status.stdout or "") + (status.stderr or "")
            if "online" in status_text.lower() or "ready" in status_text.lower():
                online = True
                break
            time.sleep(0.5)
        (WORK / "daemon-status.txt").write_text(status_text, encoding="utf-8")
        record("daemon online", "status mentions online or ready", status_text.strip()[:400], online)

        serve_handle = serve_log.open("w", encoding="utf-8")
        serve = subprocess.Popen(
            [
                str(BINARY),
                "serve",
                "--transport",
                "http",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--config",
                str(config),
            ],
            cwd=str(WORK),
            env=env,
            stdout=serve_handle,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        ready = False
        for _ in range(40):
            if serve.poll() is not None:
                break
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    ready = True
                    break
            except OSError:
                time.sleep(0.25)
        record("serve listening", f"127.0.0.1:{port}", f"ready={ready} exit={serve.poll()}", ready)
        if not ready:
            raise RuntimeError("serve did not listen")

        client = McpHttp(f"http://127.0.0.1:{port}")
        init = client.start()
        dump_json("r15-mcp-whitelist-initialize.json", init)
        listed = client.rpc("tools/list")
        dump_json("r15-mcp-whitelist-tools-list.json", listed)
        tools = ((listed.get("result") or {}).get("tools")) or []
        names = sorted(str(tool.get("name")) for tool in tools if isinstance(tool, dict))
        extra = sorted(set(names) - set(ALLOWED))
        missing = sorted(set(ALLOWED) - set(names))
        record(
            "tools/list whitelist",
            f"exactly {len(ALLOWED)} names, no extras",
            f"count={len(names)} missing={missing} extra={extra}",
            names == sorted(ALLOWED),
        )

        time.sleep(0.3)
        serve_text = serve_log.read_text(encoding="utf-8", errors="replace")
        warn_ok = TYPO in serve_text and ("неизвестн" in serve_text or "опечатк" in serve_text)
        record(
            "typo warning",
            f"stderr names {TYPO} as unknown",
            "warning present" if warn_ok else serve_text[-800:],
            warn_ok,
        )

        handlers = client.rpc(
            "tools/call",
            {
                "name": "get_form_handlers",
                "arguments": {
                    "repo": ALIAS,
                    "owner_full_name": "Documents.ЗаказПокупателя",
                    "form_name": "ФормаДокумента",
                },
            },
        )
        dump_json("r15-mcp-whitelist-form-handlers.json", handlers)
        handler_text = tool_text(handlers)
        handler_ok = (
            "error" not in handlers
            and "ТоварыКоличествоПриИзменении" in handler_text
            and "ТоварыЦенаПриИзменении" in handler_text
        )
        record(
            "allowed get_form_handlers",
            "both OnChange handlers",
            handler_text[:500],
            handler_ok,
        )

        denied_payloads: dict[str, Any] = {}
        denied_ok = True
        for denied_name in ("grep_code", "get_object_structure"):
            denied = client.rpc(
                "tools/call",
                {"name": denied_name, "arguments": {"repo": ALIAS}},
            )
            denied_payloads[denied_name] = denied
            err = denied.get("error") if isinstance(denied.get("error"), dict) else {}
            message = str(err.get("message") or "")
            ok = err.get("code") == -32602 and "disabled by [tools].enabled" in message and denied_name in message
            denied_ok = denied_ok and ok
            record(
                f"denied {denied_name}",
                "-32602 whitelist",
                f"code={err.get('code')} message={message[:240]}",
                ok,
            )
        dump_json("r15-mcp-whitelist-denied.json", denied_payloads)
    except Exception as exc:
        record("smoke exception", "no exception", repr(exc), False)
        print(f"exception: {exc}")
    finally:
        if serve is not None and serve.poll() is None:
            serve.terminate()
            try:
                serve.wait(timeout=10)
            except subprocess.TimeoutExpired:
                serve.kill()
        if serve_handle is not None:
            serve_handle.close()
        try:
            run_daemon(["daemon", "stop"], WORK / "daemon-stop-after.log", 30)
        except Exception as exc:
            print(f"daemon stop failed: {exc}")

    passed = sum(1 for item in checks if item["pass"])
    summary = {
        "binary": str(BINARY),
        "version": "1.4.0",
        "commit": "4bde72b60a09187c0667d451a02c7be5e0169835",
        "dump": str(DUMP),
        "home": str(HOME),
        "port": port,
        "allowed": ALLOWED,
        "typo": TYPO,
        "checks": checks,
        "passed": passed,
        "failed": len(checks) - passed,
    }
    dump_json("r15-mcp-whitelist-simple.json", summary)
    print(f"passed={passed} failed={summary['failed']}")
    return 0 if summary["failed"] == 0 and passed > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
