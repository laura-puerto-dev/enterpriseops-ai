import logging
from typing import Any

import structlog
from structlog.typing import EventDict

from enterpriseops_ai.observability.context import (
    agent_run_id_var,
    request_id_var,
)


def add_correlation_context(
    logger: Any,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    request_id = request_id_var.get()
    agent_run_id = agent_run_id_var.get()

    if request_id is not None:
        event_dict["request_id"] = request_id

    if agent_run_id is not None:
        event_dict["agent_run_id"] = agent_run_id

    return event_dict


def configure_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            add_correlation_context,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
