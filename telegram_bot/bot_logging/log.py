import logging
from functools import wraps

# Налаштування логера
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("BotLogger")


# Декоратор для логування виклику функцій
def log_function_call(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Виклик функції: {func.__name__}")
        return await func(*args, **kwargs)

    return wrapper