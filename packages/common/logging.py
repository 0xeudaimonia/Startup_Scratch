from __future__ import annotations

import logging
import sys
from typing import Any


class _JsonLikeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key
            not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "taskName",
            }
            and not key.startswith("_")
        }
        extra_str = " ".join(f"{k}={v}" for k, v in extras.items())
        base = super().format(record)
        return f"{base} {extra_str}".strip() if extra_str else base


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        _JsonLikeFormatter(
            "%(asctime)s level=%(levelname)s logger=%(name)s message=%(message)s"
        )
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: str, **context: Any) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logging.getLogger(name), extra=context)
