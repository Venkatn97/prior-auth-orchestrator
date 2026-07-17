import structlog
import logging
from shared.config import settings

def configure_logging():
    logging.basicConfig(
        format="%(message)s",
        level=settings.log_level,

    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),

        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )

def get_logger(name:str):
    return structlog.get_logger(name)