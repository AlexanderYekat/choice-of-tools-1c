"""Answer42 dual live Test Client on two file infobases, one stdio MCP.

IB A is the stand .v8/ib/simple. IB B is a file copy under
.v8/work/r20-dual/ib-b. Isolated ONEC_MCP_DATA_DIR. No facade, no apply.
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
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
ANSWER42 = ROOT / r".v8\work\r20-mcp\venv\Scripts\answer42.exe"
WORK = ROOT / r".v8\work\r20-dual"
DATA = WORK / "data"
IB_A = ROOT / r".v8\ib\simple"
IB_B = WORK / "ib-b"
PLATFORM_BIN = Path(r"C:\Program Files\1cv8\8.3.27.1936\bin")
LOGS_OUT = Path(os.environ.get("R20_DUAL_LOG_DIR", str(ROOT / r"evaluations\main\logs")))
SID_A = "dual-a"
SID_B = "dual-b"
REQUIRED_TOOLS = ("start_session", "active_window", "stop_session", "sessions_list", "session_status")


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
    return isinstance(data, dict) and bool(data.get("isError") or data.get("is_error"))


def same_path(left: str, right: Path) -> bool:
    try:
        return Path(left).resolve().as_posix().lower() == right.resolve().as_posix().lower()
    except OSError:
        return False


def window_title(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, ensure_ascii=False)
    for key in ("title", "active_form_title"):
        if key in payload and isinstance(payload[key], str) and payload[key].strip():
            return payload[key]
    window = payload.get("window")
    if isinstance(window, dict) and isinstance(window.get("title"), str):
        return window["title"]
    if "Простая конфигурация" in blob:
        return "Простая конфигурация"
    return ""


def standalone_configs(root: Path) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    if not root.exists():
        return found
    for path in root.rglob("standalone.yaml"):
        text = path.read_text(encoding="utf-8", errors="replace")
        found.append({"path": str(path), "text": text})
    return found


def kill_leftovers() -> list[str]:
    markers = [str(IB_A), str(IB_B), SID_A, SID_B, "MCPTestManager", str(DATA), str(WORK)]
    killed: list[str] = []
    for proc_name in ("1cv8c.exe", "1cv8.exe", "ibsrv.exe", "ibcmd.exe"):
        try:
            listed = subprocess.run(
                ["wmic", "process", "where", f"name='{proc_name}'", "get", "ProcessId,CommandLine", "/FORMAT:LIST"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        except Exception:
            continue
        current_cmd = ""
        current_pid = ""
        blocks: list[tuple[str, str]] = []
        for raw in (listed.stdout or "").splitlines():
            line = raw.strip()
            if not line:
                if current_pid and current_cmd:
                    blocks.append((current_pid, current_cmd))
                current_cmd = ""
                current_pid = ""
                continue
            if line.lower().startswith("commandline="):
                current_cmd = line.split("=", 1)[1]
            elif line.lower().startswith("processid="):
                current_pid = line.split("=", 1)[1]
        if current_pid and current_cmd:
            blocks.append((current_pid, current_cmd))
        for pid, cmd in blocks:
            if any(marker.lower() in cmd.lower() for marker in markers):
                subprocess.run(["taskkill", "/PID", pid, "/T", "/F"], capture_output=True, check=False)
                killed.append(f"{proc_name}:{pid}")
    return killed


def copy_ib() -> None:
    if not (IB_A / "1Cv8.1CD").is_file():
        raise FileNotFoundError(f"MISSING IB {IB_A}")
    if IB_B.exists():
        shutil.rmtree(IB_B)
    shutil.copytree(IB_A, IB_B)
    if not (IB_B / "1Cv8.1CD").is_file():
        raise FileNotFoundError(f"COPY FAILED {IB_B}")


async def main_async() -> int:
    if not ANSWER42.is_file():
        print(f"MISSING BINARY {ANSWER42}", file=sys.stderr)
        return 2
    if not (PLATFORM_BIN / "1cv8c.exe").is_file():
        print(f"MISSING 1cv8c {PLATFORM_BIN}", file=sys.stderr)
        return 2

    DATA.mkdir(parents=True, exist_ok=True)
    LOGS_OUT.mkdir(parents=True, exist_ok=True)
    copy_ib()
    stderr_path = WORK / "answer42.stderr.log"
    stderr_f = stderr_path.open("w", encoding="utf-8")

    env = {
        "ONEC_MCP_DATA_DIR": str(DATA),
        "ONEC_PLATFORM_DIR": str(PLATFORM_BIN),
        "PYTHONUNBUFFERED": "1",
        "PYTHONUTF8": "1",
        "ONEC_MCP_LOG_LEVEL": "INFO",
        "ONEC_MCP_ACCOUNT_ID": "r20-dual",
    }
    params = StdioServerParameters(
        command=str(ANSWER42),
        args=["--disable-rag", "--disable-credential-store", "--tool-profile", "ui"],
        env=env,
        cwd=str(WORK),
    )

    checks: list[dict[str, Any]] = []
    failed = 0
    started: set[str] = set()
    client: Client | None = None

    def record(name: str, expected: str, actual: str, ok: bool, extra: Any = None) -> None:
        nonlocal failed
        checks.append({"name": name, "expected": expected, "actual": actual, "pass": ok, "extra": extra})
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {actual}")
        if not ok:
            failed += 1

    async def start(sid: str, ib: Path) -> dict[str, Any]:
        result = await client.call_tool(
            "start_session",
            {
                "session_id": sid,
                "base_url": str(ib),
                "idle_timeout_minutes": 20,
                "version": "8.3.27.1936",
                "include_timings": True,
            },
            read_timeout_seconds=900,
        )
        payload = extract_payload(result)
        dump_json(f"r20-mcp-dual-start-{sid}.json", {"result": to_dict(result), "payload": payload})
        test_client = payload.get("test_client") if isinstance(payload.get("test_client"), dict) else {}
        base = str(test_client.get("base_url") or "")
        conn = str(test_client.get("connection_value") or "")
        ok = (
            not is_error_result(result)
            and payload.get("session_id") == sid
            and bool(test_client.get("connected"))
            and same_path(base, ib)
            and conn.startswith("http://")
        )
        record(
            f"start_session {sid}",
            f"connected Test Client, base_url={ib}",
            f"isError={is_error_result(result)} base={base} conn={conn} port={test_client.get('port')}",
            ok,
        )
        if ok:
            started.add(sid)
        return payload

    async def stop(sid: str) -> None:
        result = await client.call_tool(
            "stop_session",
            {"session_id": sid, "clean_data": True},
            read_timeout_seconds=180,
        )
        payload = extract_payload(result)
        dump_json(f"r20-mcp-dual-stop-{sid}.json", {"result": to_dict(result), "payload": payload})
        ok = (not is_error_result(result)) and payload.get("stopped") is True
        record(f"stop_session {sid}", "stopped=true", json.dumps(payload, ensure_ascii=False)[:240], ok)
        started.discard(sid)

    try:
        old_err = sys.stderr
        sys.stderr = stderr_f
        try:
            client = Client(
                params,
                client_info=Implementation(name="r20-dual", version="0"),
                mode="legacy",
                read_timeout_seconds=900,
            )
            await client.__aenter__()
        finally:
            sys.stderr = old_err

        info = to_dict(client.server_info)
        dump_json("r20-mcp-dual-initialize.json", {"serverInfo": info, "protocolVersion": client.protocol_version})
        name = str(info.get("name") or "") if isinstance(info, dict) else ""
        record("initialize", "Answer42", f"name={name} protocol={client.protocol_version}", name == "Answer42")

        names: list[str] = []
        cursor = None
        while True:
            listed = await client.list_tools(cursor=cursor)
            for tool in getattr(listed, "tools", None) or []:
                tool_name = getattr(tool, "name", None)
                if isinstance(tool_name, str):
                    names.append(tool_name)
            cursor = getattr(listed, "nextCursor", None) or getattr(listed, "next_cursor", None)
            if not cursor:
                break
        missing = [n for n in REQUIRED_TOOLS if n not in names]
        record(
            "tools/list",
            "session tools present",
            f"count={len(names)} missing={missing}",
            not missing and "rag_query" not in names,
        )

        payload_a = await start(SID_A, IB_A)
        payload_b = await start(SID_B, IB_B)
        conn_a = str((payload_a.get("test_client") or {}).get("connection_value") or "")
        conn_b = str((payload_b.get("test_client") or {}).get("connection_value") or "")
        record(
            "distinct ibsrv urls",
            "two different http connection_value values",
            f"A={conn_a} B={conn_b}",
            bool(conn_a and conn_b and conn_a != conn_b),
        )

        listed_sessions = await client.call_tool("sessions_list", {}, read_timeout_seconds=60)
        sessions_payload = extract_payload(listed_sessions)
        dump_json("r20-mcp-dual-sessions-both.json", {"result": to_dict(listed_sessions), "payload": sessions_payload})
        items = sessions_payload.get("sessions") if isinstance(sessions_payload.get("sessions"), list) else []
        by_id = {str(item.get("session_id")): item for item in items if isinstance(item, dict)}
        both_listed = (
            SID_A in by_id
            and SID_B in by_id
            and by_id[SID_A].get("running") is True
            and by_id[SID_B].get("running") is True
            and same_path(str(by_id[SID_A].get("base_url") or ""), IB_A)
            and same_path(str(by_id[SID_B].get("base_url") or ""), IB_B)
            and by_id[SID_A].get("testclient_alive") is True
            and by_id[SID_B].get("testclient_alive") is True
        )
        record(
            "sessions_list both live",
            "two running sessions bound to their own file IB",
            f"count={sessions_payload.get('count')} A={by_id.get(SID_A, {}).get('base_url')} B={by_id.get(SID_B, {}).get('base_url')}",
            both_listed and not is_error_result(listed_sessions),
        )

        statuses: dict[str, dict[str, Any]] = {}
        for sid, ib in ((SID_A, IB_A), (SID_B, IB_B)):
            status = await client.call_tool("session_status", {"session_id": sid}, read_timeout_seconds=60)
            payload = extract_payload(status)
            statuses[sid] = payload
            dump_json(f"r20-mcp-dual-status-{sid}.json", {"result": to_dict(status), "payload": payload})
        test_a = statuses[SID_A].get("test_client") if isinstance(statuses[SID_A].get("test_client"), dict) else {}
        test_b = statuses[SID_B].get("test_client") if isinstance(statuses[SID_B].get("test_client"), dict) else {}
        key_a = str(test_a.get("shared_file_key") or "")
        key_b = str(test_b.get("shared_file_key") or "")
        port_a = int(test_a.get("file_client_ibsrv_port") or 0)
        port_b = int(test_b.get("file_client_ibsrv_port") or 0)
        status_ok = (
            same_path(str(statuses[SID_A].get("target_connection_value") or ""), IB_A)
            and same_path(str(statuses[SID_B].get("target_connection_value") or ""), IB_B)
            and key_a
            and key_b
            and key_a != key_b
            # Windows shared_file_key keeps backslashes. The 2026-09-21
            # run compared Path.as_posix() and false-failed; JSON already
            # showed both keys. That run was not repeated after this fix.
            and str(IB_A.resolve()).lower() in key_a.lower()
            and str(IB_B.resolve()).lower() in key_b.lower()
            and port_a > 0
            and port_b > 0
            and port_a != port_b
            and test_a.get("alive") is True
            and test_b.get("alive") is True
        )
        record(
            "session_status paths stay apart",
            "each session keeps its file path, shared key and ibsrv port",
            f"A={statuses[SID_A].get('target_connection_value')} port={port_a}; B={statuses[SID_B].get('target_connection_value')} port={port_b}",
            status_ok,
        )

        titles: dict[str, str] = {}
        for sid in (SID_A, SID_B):
            window = await client.call_tool("active_window", {"session_id": sid}, read_timeout_seconds=120)
            payload = extract_payload(window)
            dump_json(f"r20-mcp-dual-window-{sid}.json", {"result": to_dict(window), "payload": payload})
            titles[sid] = window_title(payload)
            record(
                f"active_window {sid}",
                "non-empty window while the other session is up",
                f"isError={is_error_result(window)} title={titles[sid]!r}",
                (not is_error_result(window)) and bool(titles[sid]),
            )

        configs = standalone_configs(DATA)
        dump_json("r20-mcp-dual-standalone.json", configs)
        config_blob = "\n".join(item["text"] for item in configs).lower()
        record(
            "standalone.yaml both db paths",
            "isolated data dir contains both file IB paths at once",
            f"yaml={len(configs)} hasA={str(IB_A.resolve()).lower() in config_blob} hasB={str(IB_B.resolve()).lower() in config_blob}",
            str(IB_A.resolve()).lower() in config_blob and str(IB_B.resolve()).lower() in config_blob,
        )

        if SID_A in started:
            await stop(SID_A)
        status_b = await client.call_tool("session_status", {"session_id": SID_B}, read_timeout_seconds=60)
        status_a = await client.call_tool("session_status", {"session_id": SID_A}, read_timeout_seconds=60)
        payload_status_b = extract_payload(status_b)
        payload_status_a = extract_payload(status_a)
        dump_json("r20-mcp-dual-status-after-stop-a.json", {"A": payload_status_a, "B": payload_status_b})
        window_b = await client.call_tool("active_window", {"session_id": SID_B}, read_timeout_seconds=120)
        window_a = await client.call_tool("active_window", {"session_id": SID_A}, read_timeout_seconds=60)
        payload_window_b = extract_payload(window_b)
        payload_window_a = extract_payload(window_a)
        dump_json(
            "r20-mcp-dual-window-after-stop-a.json",
            {"A": {"result": to_dict(window_a), "payload": payload_window_a}, "B": {"result": to_dict(window_b), "payload": payload_window_b}},
        )
        b_still = (
            payload_status_b.get("running") is True
            and same_path(str(payload_status_b.get("target_connection_value") or ""), IB_B)
            and not is_error_result(window_b)
            and bool(window_title(payload_window_b))
        )
        a_gone = payload_status_a.get("running") is not True or is_error_result(window_a)
        record(
            "stop A leaves B",
            "A is gone; B still answers active_window on its own IB",
            f"A.running={payload_status_a.get('running')} A.windowError={is_error_result(window_a)} B.running={payload_status_b.get('running')} B.path={payload_status_b.get('target_connection_value')} B.title={window_title(payload_window_b)!r} titles_while_both={titles}",
            b_still and a_gone,
        )
    except Exception as exc:
        record("dual-exception", "no exception", repr(exc), False)
    finally:
        if client is not None:
            for sid in list(started):
                try:
                    await client.call_tool(
                        "stop_session",
                        {"session_id": sid, "clean_data": True},
                        read_timeout_seconds=120,
                    )
                    started.discard(sid)
                except Exception:
                    pass
            try:
                await client.__aexit__(None, None, None)
            except Exception:
                pass
        stderr_f.close()
        killed = kill_leftovers()
        dump_json(
            "r20-mcp-dual.json",
            {
                "binary": str(ANSWER42),
                "package": "answer42==0.5.3",
                "ib_a": str(IB_A),
                "ib_b": str(IB_B),
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
