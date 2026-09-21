"""Publish Unica apply (dryRun:false + ifRev) on Designer dump 2.20.

Writes only under .v8/work/simple-cf-220. Isolated provider-state.
Does not touch source-checkouts/simple1CAiConf or the IB.
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

ROOT = Path(r"C:\MyProjects\choice-of-tools-1c")
BINARY = ROOT / r".v8\work\r01\target\debug\unica.exe"
DUMP = Path(os.environ.get("UNICA_SMOKE_DUMP", str(ROOT / r".v8\work\simple-cf-220")))
WORK = Path(os.environ.get("UNICA_SMOKE_WORK", str(ROOT / r".v8\work\r01-apply-publish")))
STATE = WORK / "provider-state"
LOGS_OUT = Path(os.environ.get("UNICA_SMOKE_LOG_DIR", str(ROOT / r"evaluations\main\logs")))
PLUGIN_ROOT = ROOT / r".v8\work\r01\unica-src\plugins\unica"
LOG_PREFIX = os.environ.get("UNICA_SMOKE_LOG_PREFIX", "r01-mcp-apply-publish")

DOCUMENT_AT = "main:Document.ЗаказПокупателя"
COMMENT_PUBLISH = os.environ.get("UNICA_SMOKE_COMMENT", "r01-publish-ifRev-20260921")
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
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files[rel.as_posix()] = digest
    return files


def files_containing(root: Path, needle: str) -> list[str]:
    hits: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DUMP_DIRS for part in rel.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if needle in text:
            hits.append(rel.as_posix())
    return hits


def apply_ops(comment: str) -> list[dict[str, Any]]:
    return [{"op": "props.set", "args": {"values": {"Comment": comment}}}]


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
    handwritten = ROOT / "source-checkouts" / "simple1CAiConf"
    if DUMP.resolve() == handwritten.resolve():
        print("REFUSING to publish into source-checkouts/simple1CAiConf", file=sys.stderr)
        return 2

    STATE.mkdir(parents=True, exist_ok=True)
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    before = fingerprint_dump(DUMP)
    comment_before = files_containing(DUMP, COMMENT_PUBLISH)
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
    preview_rev: str | None = None

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
                "clientInfo": {"name": "r01-apply-publish-smoke", "version": "0"},
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
            "ops": apply_ops(COMMENT_PUBLISH),
        }
        apply_dry = call_tool(client, "unica.apply", dry_args, timeout=180)
        dump_json(f"{LOG_PREFIX}-dryrun-simple.json", apply_dry)
        env_dry = extract_envelope(apply_dry)
        data_dry = env_dry.get("data") if isinstance(env_dry.get("data"), dict) else {}
        preview_rev = env_dry.get("rev") if isinstance(env_dry.get("rev"), str) else None
        dry_ok = (
            bool(env_dry.get("ok"))
            and bool(preview_rev)
            and data_dry.get("mode") == "preview"
            and data_dry.get("executable") is True
        )
        record(
            "unica.apply dryRun props.set Comment",
            "preview plan with rev",
            f"ok={env_dry.get('ok')} mode={data_dry.get('mode')} executable={data_dry.get('executable')} rev={preview_rev} summary={env_dry.get('summary')}",
            dry_ok,
            {"envelope_keys": list(env_dry.keys()), "rev": preview_rev},
        )

        mid = fingerprint_dump(DUMP)
        mid_changed = sorted(k for k in set(before) | set(mid) if before.get(k) != mid.get(k))
        record(
            "dump unchanged after dryRun",
            "no dump files changed before publication",
            f"changed={mid_changed[:12]} count={len(mid_changed)}",
            not mid_changed,
        )

        pub_args = {
            "at": DOCUMENT_AT,
            "dryRun": False,
            "ifRev": preview_rev or "",
            "ops": apply_ops(COMMENT_PUBLISH),
        }
        apply_pub = call_tool(client, "unica.apply", pub_args, timeout=180)
        dump_json(f"{LOG_PREFIX}-publish-simple.json", apply_pub)
        env_pub = extract_envelope(apply_pub)
        data_pub = env_pub.get("data") if isinstance(env_pub.get("data"), dict) else {}
        blob_pub = envelope_blob(env_pub).lower()
        pub_ok = bool(env_pub.get("ok")) and data_pub.get("mode") != "preview"
        record(
            "unica.apply publish dryRun:false + ifRev",
            "ok publication, not preview",
            f"ok={env_pub.get('ok')} mode={data_pub.get('mode')} summary={env_pub.get('summary')} rpc_error={apply_pub.get('error') is not None} blob={blob_pub[:240]}",
            pub_ok,
            {"envelope_keys": list(env_pub.keys()), "rev": env_pub.get("rev")},
        )

        after = fingerprint_dump(DUMP)
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        comment_after = files_containing(DUMP, COMMENT_PUBLISH)
        write_ok = bool(changed) and bool(comment_after) and not comment_before
        record(
            "dump Comment published",
            "Document XML contains marker; fingerprint changed",
            f"changed={changed[:12]} count={len(changed)} comment_files={comment_after} before_hits={comment_before}",
            write_ok,
        )

        stale_args = {
            "at": DOCUMENT_AT,
            "dryRun": False,
            "ifRev": preview_rev or "",
            "ops": apply_ops(COMMENT_PUBLISH + "-stale"),
        }
        apply_stale = call_tool(client, "unica.apply", stale_args, timeout=60)
        dump_json(f"{LOG_PREFIX}-stale-simple.json", apply_stale)
        env_stale = extract_envelope(apply_stale)
        blob_stale = envelope_blob(env_stale).lower()
        stale_ok = env_stale.get("ok") is not True and (
            "ifrev" in blob_stale or "rev" in blob_stale or "stale" in blob_stale or "mismatch" in blob_stale
        )
        record(
            "unica.apply stale ifRev after publish",
            "refusal naming ifRev / rev",
            f"ok={env_stale.get('ok')} summary={env_stale.get('summary')} rpc_error={apply_stale.get('error') is not None} blob={blob_stale[:240]}",
            stale_ok,
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
            f"{LOG_PREFIX}-simple.json",
            {
                "binary": str(BINARY),
                "dump": str(DUMP),
                "state": str(STATE),
                "comment": COMMENT_PUBLISH,
                "preview_rev": preview_rev,
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
