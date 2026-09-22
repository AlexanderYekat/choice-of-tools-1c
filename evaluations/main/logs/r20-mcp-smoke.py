"""Answer42 stdio MCP smoke on stand simple.

Isolated ONEC_MCP_DATA_DIR. --tool-profile ui --disable-rag
--disable-credential-store. No facade, no apply, no Vanessa.
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from mcp import Client, Implementation, StdioServerParameters

ROOT = Path(r"C:\MyProjects\choice-of-tools-1c")
VENV_PY = ROOT / r".v8\work\r20-mcp\venv\Scripts\python.exe"
ANSWER42 = ROOT / r".v8\work\r20-mcp\venv\Scripts\answer42.exe"
WORK = ROOT / r".v8\work\r20-mcp"
DATA = WORK / "data"
IB = ROOT / r".v8\ib\simple"
PLATFORM_BIN = Path(r"C:\Program Files\1cv8\8.3.27.1936\bin")
LOGS_OUT = Path(os.environ.get("R20_SMOKE_LOG_DIR", str(ROOT / r"evaluations\main\logs")))
SESSION_ID = os.environ.get("R20_SMOKE_SESSION_ID", "simple-smoke")
PAUSE_SECONDS = int(os.environ.get("R20_SMOKE_PAUSE", "0"))
REQUIRED_TOOLS = ("start_session", "active_window", "stop_session", "screenshot")
FORBIDDEN_TOOLS = ("rag_query", "rag_index_build", "metadata_objects_from_catalog")


def dump_json(name: str, value: Any) -> None:
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    (LOGS_OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def to_dict(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    if isinstance(value, dict):
        return value
    return {"repr": repr(value)}


def extract_payload(result: Any) -> dict[str, Any]:
    data = to_dict(result)
    if not isinstance(data, dict):
        return {"value": data}
    structured = data.get("structuredContent") or data.get("structured_content")
    if isinstance(structured, dict):
        return structured
    for block in data.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text") or ""
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                return {"text": text}
            if isinstance(parsed, dict):
                return parsed
            return {"parsed": parsed}
    return data


def is_error_result(result: Any) -> bool:
    data = to_dict(result)
    if isinstance(data, dict) and (data.get("isError") or data.get("is_error")):
        return True
    return False


def kill_leftovers() -> list[str]:
    markers = [str(IB), SESSION_ID, "MCPTestManager", str(DATA)]
    killed: list[str] = []
    for proc_name in ("1cv8c.exe", "1cv8.exe", "ibsrv.exe", "ibcmd.exe"):
        try:
            listed = subprocess.run(
                ["wmic", "process", "where", f"name='{proc_name}'", "get", "ProcessId,CommandLine", "/FORMAT:LIST"],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except Exception:
            continue
        current_cmd = ""
        current_pid = ""
        for raw in (listed.stdout or "").splitlines():
            line = raw.strip()
            if not line:
                if current_pid and current_cmd and any(marker.lower() in current_cmd.lower() for marker in markers):
                    subprocess.run(["taskkill", "/PID", current_pid, "/T", "/F"], capture_output=True, check=False)
                    killed.append(f"{proc_name}:{current_pid}")
                current_cmd = ""
                current_pid = ""
                continue
            if line.lower().startswith("commandline="):
                current_cmd = line.split("=", 1)[1]
            elif line.lower().startswith("processid="):
                current_pid = line.split("=", 1)[1]
        if current_pid and current_cmd and any(marker.lower() in current_cmd.lower() for marker in markers):
            subprocess.run(["taskkill", "/PID", current_pid, "/T", "/F"], capture_output=True, check=False)
            killed.append(f"{proc_name}:{current_pid}")
    return killed


async def main_async() -> int:
    if not ANSWER42.is_file():
        print(f"MISSING BINARY {ANSWER42}", file=sys.stderr)
        return 2
    if not (IB / "1Cv8.1CD").is_file():
        print(f"MISSING IB {IB}", file=sys.stderr)
        return 2
    if not (PLATFORM_BIN / "1cv8c.exe").is_file():
        print(f"MISSING 1cv8c {PLATFORM_BIN}", file=sys.stderr)
        return 2

    DATA.mkdir(parents=True, exist_ok=True)
    (WORK / "screenshots").mkdir(parents=True, exist_ok=True)
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    stderr_path = WORK / "answer42.stderr.log"
    stderr_f = stderr_path.open("w", encoding="utf-8")

    env = {
        "ONEC_MCP_DATA_DIR": str(DATA),
        "ONEC_PLATFORM_DIR": str(PLATFORM_BIN),
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1",
        "ONEC_MCP_LOG_LEVEL": "INFO",
        "ONEC_MCP_ACCOUNT_ID": "r20-smoke",
    }

    params = StdioServerParameters(
        command=str(ANSWER42),
        args=["--disable-rag", "--disable-credential-store", "--tool-profile", "ui"],
        env=env,
        cwd=str(WORK),
    )

    checks: list[dict[str, Any]] = []
    failed = 0
    started = False
    killed: list[str] = []

    def record(name: str, expected: str, actual: str, ok: bool, extra: Any = None) -> None:
        nonlocal failed
        checks.append({"name": name, "expected": expected, "actual": actual, "pass": ok, "extra": extra})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {actual}")
        if not ok:
            failed += 1

    client: Client | None = None
    try:
        # stdio_client writes server logs to the Client process stderr; keep ours on stdout.
        old_err = sys.stderr
        sys.stderr = stderr_f
        try:
            client = Client(
                params,
                client_info=Implementation(name="r20-smoke", version="0"),
                mode="legacy",
                read_timeout_seconds=900,
            )
            await client.__aenter__()
        finally:
            sys.stderr = old_err

        info = to_dict(client.server_info)
        dump_json("r20-mcp-initialize-simple.json", {"serverInfo": info, "protocolVersion": client.protocol_version})
        name = ""
        version = ""
        if isinstance(info, dict):
            name = str(info.get("name") or "")
            version = str(info.get("version") or "")
        record(
            "initialize",
            "serverInfo.name contains Answer42",
            f"name={name} version={version} protocol={client.protocol_version}",
            "answer42" in name.lower() or name == "Answer42",
            {"serverInfo": info},
        )

        names: list[str] = []
        cursor = None
        listed_raw: list[Any] = []
        while True:
            listed = await client.list_tools(cursor=cursor)
            listed_raw.append(to_dict(listed))
            tools = getattr(listed, "tools", None) or []
            for tool in tools:
                tool_name = getattr(tool, "name", None)
                if isinstance(tool_name, str):
                    names.append(tool_name)
            cursor = getattr(listed, "nextCursor", None) or getattr(listed, "next_cursor", None)
            if not cursor:
                break
        dump_json("r20-mcp-tools-list-simple.json", {"names": names, "pages": listed_raw})
        missing = [n for n in REQUIRED_TOOLS if n not in names]
        leaked = [n for n in FORBIDDEN_TOOLS if n in names]
        count_ok = 20 < len(names) < 122 and not missing and not leaked
        record(
            "tools/list ui --disable-rag",
            "ui subset: required present, RAG absent, count < 122",
            f"count={len(names)} missing={missing} leaked_rag={leaked}",
            count_ok,
            {"names": names},
        )

        start = await client.call_tool(
            "start_session",
            {
                "session_id": SESSION_ID,
                "base_url": str(IB),
                "idle_timeout_minutes": 15,
                "version": "8.3.27.1936",
                "include_timings": True,
            },
            read_timeout_seconds=900,
        )
        start_payload = extract_payload(start)
        dump_json("r20-mcp-start-session-simple.json", {"result": to_dict(start), "payload": start_payload})
        start_blob = json.dumps(start_payload, ensure_ascii=False)
        start_ok = (not is_error_result(start)) and (
            SESSION_ID in start_blob
            or "session" in start_blob.lower()
            or bool(start_payload.get("session_id") == SESSION_ID)
            or bool(start_payload.get("ok") is True)
        )
        # A structured error dict from FastMCP is still a successful RPC.
        if is_error_result(start):
            start_ok = False
        if "already exists" in start_blob.lower():
            start_ok = False
        record(
            f"start_session session_id={SESSION_ID}",
            "session started against file IB simple",
            f"isError={is_error_result(start)} keys={list(start_payload)[:12]} snippet={start_blob[:240]}",
            start_ok,
        )
        started = start_ok

        if started:
            window = await client.call_tool(
                "active_window",
                {"session_id": SESSION_ID},
                read_timeout_seconds=120,
            )
            window_payload = extract_payload(window)
            dump_json("r20-mcp-active-window-simple.json", {"result": to_dict(window), "payload": window_payload})
            window_blob = json.dumps(window_payload, ensure_ascii=False)
            window_ok = (not is_error_result(window)) and bool(window_blob.strip("{} "))
            record(
                "active_window",
                "non-empty window descriptor",
                f"isError={is_error_result(window)} snippet={window_blob[:240]}",
                window_ok,
            )

            shot_path = WORK / "screenshots" / "simple-smoke.png"
            shot = await client.call_tool(
                "screenshot",
                {"session_id": SESSION_ID, "path": str(shot_path), "window": True},
                read_timeout_seconds=120,
            )
            shot_payload = extract_payload(shot)
            dump_json("r20-mcp-screenshot-simple.json", {"result": to_dict(shot), "payload": shot_payload})
            returned_path = str(shot_payload.get("path") or shot_payload.get("output_path") or "")
            exists = Path(returned_path).is_file() if returned_path else shot_path.is_file()
            has_b64 = "base64" in json.dumps(shot_payload, ensure_ascii=False).lower() and len(json.dumps(shot_payload)) > 4000
            record(
                "screenshot",
                "PNG path in result, no large base64",
                f"isError={is_error_result(shot)} path={returned_path or shot_path} exists={exists} large_b64={has_b64}",
                (not is_error_result(shot)) and exists and not has_b64,
            )

            if PAUSE_SECONDS > 0:
                print(f"WATCH: 1C windows stay open {PAUSE_SECONDS}s; firewall prompt is ibsrv")
                await asyncio.sleep(PAUSE_SECONDS)

            dup = await client.call_tool(
                "start_session",
                {
                    "session_id": SESSION_ID,
                    "base_url": str(IB),
                    "idle_timeout_minutes": 15,
                },
                read_timeout_seconds=60,
            )
            dup_payload = extract_payload(dup)
            dump_json("r20-mcp-start-session-duplicate-simple.json", {"result": to_dict(dup), "payload": dup_payload})
            dup_blob = json.dumps(dup_payload, ensure_ascii=False)
            dup_ok = is_error_result(dup) or "already exists" in dup_blob.lower() or dup_payload.get("ok") is False
            record(
                "start_session duplicate session_id",
                "refusal for existing session",
                f"isError={is_error_result(dup)} snippet={dup_blob[:240]}",
                dup_ok,
            )

        stop = await client.call_tool(
            "stop_session",
            {"session_id": SESSION_ID, "clean_data": True},
            read_timeout_seconds=180,
        )
        stop_payload = extract_payload(stop)
        dump_json("r20-mcp-stop-session-simple.json", {"result": to_dict(stop), "payload": stop_payload})
        if started:
            stop_ok = not is_error_result(stop)
        else:
            stop_ok = True
        record(
            "stop_session",
            "session stopped" if started else "best-effort stop after failed start",
            f"isError={is_error_result(stop)} snippet={json.dumps(stop_payload, ensure_ascii=False)[:240]}",
            stop_ok,
        )
        started = False
    except Exception as exc:
        record("smoke-exception", "no exception", repr(exc), False)
    finally:
        if client is not None and started:
            try:
                await client.call_tool(
                    "stop_session",
                    {"session_id": SESSION_ID, "clean_data": True},
                    read_timeout_seconds=120,
                )
            except Exception:
                pass
        if client is not None:
            try:
                await client.__aexit__(None, None, None)
            except Exception:
                pass
        stderr_f.close()
        killed = kill_leftovers()
        dump_json(
            "r20-mcp-simple.json",
            {
                "binary": str(ANSWER42),
                "package": "answer42==0.5.3",
                "ib": str(IB),
                "data": str(DATA),
                "platform": str(PLATFORM_BIN),
                "checks": checks,
                "failed": failed,
                "killed_leftovers": killed,
                "stderr_log": str(stderr_path),
            },
        )

    print(f"RESULT failed={failed} total={len(checks)}")
    return 0 if failed == 0 else 1


def main() -> int:
    os.environ.setdefault("PYTHONUTF8", "1")
    return asyncio.run(main_async())


if __name__ == "__main__":
    raise SystemExit(main())
