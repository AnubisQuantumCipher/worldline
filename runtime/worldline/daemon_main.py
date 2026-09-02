from __future__ import annotations

import argparse
import asyncio
import logging
import signal

from .app import WorldlineApplication
from .errors import WorldlineError


async def _run() -> int:
    application = WorldlineApplication.build()
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
    parser = argparse.ArgumentParser(prog="worldlined")
    parser.add_argument("--log-level", choices=("DEBUG", "INFO", "WARNING", "ERROR"), default="INFO")
    arguments = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, arguments.log_level), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        return asyncio.run(_run())
    except WorldlineError as exc:
        logging.getLogger("worldline.daemon").error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
