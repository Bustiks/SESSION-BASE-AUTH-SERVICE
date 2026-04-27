import logging
import logging.config
from pathlib import Path
from functools import wraps
from fastapi import HTTPException
import yaml
from colorama import Fore, Style, init

init(autoreset=True)

class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage().lower()
        blocked_words = ["password", "token", "secret"]
        return not any(word in message for word in blocked_words)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        original_msg = record.msg

        color = self.COLORS.get(record.levelno, "")
        if color:
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
            record.msg = f"{color}{record.msg}{Style.RESET_ALL}"

        formatted = super().format(record)

        record.levelname = original_levelname
        record.msg = original_msg

        return formatted


def setup_logging(config_path: str = "logging_config.yaml") -> None:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    logging.config.dictConfig(config)

def log_service(logger, log_result: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.debug("Calling %s", func.__name__)
            try:
                result = await func(*args, **kwargs)
                if log_result:
                    logger.debug("%s result=%s", func.__name__, result)
                return result

            except HTTPException as e:
                logger.warning(
                    "%s -> HTTP %s: %s",
                    func.__name__,
                    e.status_code,
                    e.detail,
                )
                raise

            except Exception:
                logger.exception("Unhandled error in %s", func.__name__)
                raise

        return wrapper
    return decorator