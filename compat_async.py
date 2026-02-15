"""Compatibility async/sync bridge utilities.

The legacy API surface in `compat.py` is synchronous, but the v3 system is async.
Python 3.11 tightened event loop semantics (no implicit default loop), so we
provide a deterministic bridge:

- If no running loop: run via `asyncio.run()`.
- If already inside a running loop: use a dedicated background loop thread and
  `run_coroutine_threadsafe`.

This avoids `RuntimeError: There is no current event loop in thread 'MainThread'.`
"""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import Future
from typing import Any, Coroutine, Optional, TypeVar

T = TypeVar("T")


_BG_LOOP: Optional[asyncio.AbstractEventLoop] = None
_BG_THREAD: Optional[threading.Thread] = None
_BG_LOCK = threading.Lock()


def _ensure_bg_loop() -> asyncio.AbstractEventLoop:
    global _BG_LOOP, _BG_THREAD
    with _BG_LOCK:
        if _BG_LOOP is not None and _BG_LOOP.is_running():
            return _BG_LOOP

        loop = asyncio.new_event_loop()

        def runner() -> None:
            asyncio.set_event_loop(loop)
            loop.run_forever()

        t = threading.Thread(target=runner, name="deepsea-nexus-bg-loop", daemon=True)
        t.start()
        _BG_LOOP = loop
        _BG_THREAD = t
        return loop


def run_coro_sync(coro: Coroutine[Any, Any, T], timeout: Optional[float] = None) -> T:
    """Run an async coroutine from sync code safely."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    loop = _ensure_bg_loop()
    fut: Future[T] = asyncio.run_coroutine_threadsafe(coro, loop)
    return fut.result(timeout=timeout)
