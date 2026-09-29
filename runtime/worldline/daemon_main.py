from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal

from .app import WorldlineApplication
from .errors import WorldlineError
from .paths import WorldlinePaths, acquire_store_lock, close_gate_at, store_directories


async def _run(paths: WorldlinePaths) -> int:
    application = WorldlineApplication.build(paths)
    stopped = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(signum, stopped.set)
    await application.daemon.start()
    serving = asyncio.create_task(application.daemon.serve_forever())
    await stopped.wait()
    serving.cancel()
    await asyncio.gather(serving, return_exceptions=True)
    await application.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    # Before anything is built: building already creates files in the runtime directory, which
    # client mode opens to the client group. The unit's UMask is not relied on.
    os.umask(0o077)
    parser = argparse.ArgumentParser(prog="worldlined")
    parser.add_argument("--log-level", choices=("DEBUG", "INFO", "WARNING", "ERROR"), default="INFO")
    arguments = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, arguments.log_level), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    log = logging.getLogger("worldline.daemon")
    _raise_descriptor_limit()
    try:
        data, state = store_directories()
        # The store lock before anything is validated or built: building opens the database,
        # migrates it and sets directory modes, which a second daemon, or one started during a
        # relocation, must not do (review of 796cb02); and a configuration that refuses must still
        # be able to close the gate a previous run opened (review of 4490013).
        lock = acquire_store_lock(state, holder="worldlined")
    except WorldlineError as exc:
        log.error("%s", exc)
        return 1

    def close_gate() -> None:
        # This process holds the store lock, so no other 1.7.1 or later daemon serves this store:
        # a start that refused, or a daemon that failed, must not leave a previous run's gate
        # open. Only DAEMON_ALREADY_RUNNING (an older daemon's runtime lock) leaves it alone.
        try:
            close_gate_at(data)
        except OSError:
            log.exception("could not close the client gate")

    try:
        try:
            paths = WorldlinePaths.from_environment()
        except WorldlineError as exc:
            log.error("%s", exc)
            close_gate()
            return 1
        return asyncio.run(_run(paths))
    except WorldlineError as exc:
        log.error("%s", exc)
        if exc.code != "DAEMON_ALREADY_RUNNING":
            close_gate()
        return 1
    except BaseException:
        close_gate()
        raise
    finally:
        os.close(lock)


def _raise_descriptor_limit() -> None:
    """Removing a tree holds a descriptor per directory level; a candidate's tree can be deep,
    and systemd's default soft limit is 1024 (review of 4490013)."""
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    target = hard if hard != resource.RLIM_INFINITY else 1 << 20
    if soft != resource.RLIM_INFINITY and soft < target:
        resource.setrlimit(resource.RLIMIT_NOFILE, (min(target, 1 << 20), hard))


if __name__ == "__main__":
    raise SystemExit(main())
