"""트레이스 MD 파일들을 JSON으로 덤프.

실행: python -m snapshots.traces_dump
출력: snapshots/traces_snapshot.json

GitHub에서 에이전트 실행 트레이스를 확인할 수 있도록 스냅샷을 생성한다.
traces/*.md 는 gitignore 되어있으므로 이 파일로 GitHub에서 확인 가능.
"""

import json
import re
from pathlib import Path

TRACES_DIR = Path(__file__).parent.parent / "traces"
OUTPUT_PATH = Path(__file__).parent / "traces_snapshot.json"


def _parse_trace_header(content: str) -> dict:
    """트레이스 MD에서 시간, 사용자 입력, 최종 의도를 추출."""
    header = {}
    for line in content.split("\n")[:5]:
        if "**시간**" in line:
            m = re.search(r"\*\*시간\*\*:\s*(.+)", line)
            if m:
                header["timestamp"] = m.group(1).strip()
        elif "**사용자 입력**" in line:
            m = re.search(r"\*\*사용자 입력\*\*:\s*(.+)", line)
            if m:
                header["user_input"] = m.group(1).strip()
        elif "**최종 의도**" in line:
            m = re.search(r"\*\*최종 의도\*\*:\s*(.+)", line)
            if m:
                header["intent"] = m.group(1).strip()
    return header


def dump():
    trace_files = sorted(TRACES_DIR.glob("trace_*.md"))

    snapshot = {
        "_info": {
            "description": "에이전트 실행 트레이스 스냅샷",
            "note": "traces/*.md 는 gitignore라 Git에 안 올림. 이 파일로 GitHub에서 확인 가능",
            "regenerate": "python -m snapshots.traces_dump",
            "total_traces": len(trace_files),
        },
        "traces": {},
    }

    for tf in trace_files:
        content = tf.read_text(encoding="utf-8")
        header = _parse_trace_header(content)
        snapshot["traces"][tf.name] = {
            "header": header,
            "full_content": content,
        }

    OUTPUT_PATH.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"트레이스 스냅샷 저장: {OUTPUT_PATH}")
    print(f"  총 {len(trace_files)}건")
    for tf in trace_files:
        header = snapshot["traces"][tf.name]["header"]
        user_input = header.get("user_input", "?")
        print(f"  - {tf.name}: {user_input}")


if __name__ == "__main__":
    dump()
