import tgbot_gpt_01 as tg
from loguru import logger

logger.add("Logs/bot_debug.log", format="{time} {level} {message}", level="DEBUG", rotation="100 KB", compression="zip")
import os

MANDATORY_ENV_VARS = ["TOKEN", "API_KEY"]

for var in MANDATORY_ENV_VARS:
    if var not in os.environ:
        logger.error(f'Failed because {var} is not set. Check .env file!')
        raise EnvironmentError(f'Failed because {var} is not set. Check .env file!')

tg.main() #Запуск бота