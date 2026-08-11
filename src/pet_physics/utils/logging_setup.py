"""Contains utilities for setup logging."""

import logging
from typing import Literal

import structlog


def setup_logging(level: Literal["debug", "info"] = "info") -> None:
    """Sets up logging for this package, i.e., configures the logging level and format.

    Args:
        level: The logging level to set up.
    """
    if level == "debug":
        logging_level = logging.DEBUG
    elif level == "info":
        logging_level = logging.INFO
    else:
        raise NotImplementedError(f"Setup of logging level '{level}' is not implemented.")

    logging.basicConfig(
        level=logging_level,
        format="",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    structlog.configure(wrapper_class=structlog.stdlib.BoundLogger, logger_factory=structlog.stdlib.LoggerFactory())
