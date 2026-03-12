import os
import sqlite3
import queue
import threading
from config import DB_PATH

# 커넥션 풀 설정 (환경변수로 조정 가능)
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))

_pool: queue.Queue[sqlite3.Connection] = queue.Queue(maxsize=POOL_SIZE)
_pool_lock = threading.Lock()
_pool_initialized = False


def _create_connection() -> sqlite3.Connection:
    """새 SQLite 커넥션 생성."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _init_pool() -> None:
    """커넥션 풀 초기화 — 최초 1회만 실행."""
    global _pool_initialized
    with _pool_lock:
        if _pool_initialized:
            return
        for _ in range(POOL_SIZE):
            _pool.put(_create_connection())
        _pool_initialized = True


def get_connection() -> sqlite3.Connection:
    """풀에서 커넥션을 꺼낸다. 풀이 비면 대기."""
    _init_pool()
    return _pool.get()


def release_connection(conn: sqlite3.Connection) -> None:
    """커넥션을 풀에 반환."""
    try:
        _pool.put_nowait(conn)
    except queue.Full:
        conn.close()


def query(sql: str, params: tuple | dict = ()) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        release_connection(conn)


def execute(sql: str, params: tuple | dict = ()) -> None:
    conn = get_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        release_connection(conn)


def execute_script(script: str) -> None:
    conn = get_connection()
    try:
        conn.executescript(script)
    finally:
        release_connection(conn)
