import tgbot_gpt_01 as tg
from loguru import logger

logger.add("Logs/bot_debug.log", format="{time} {level} {message}", level="DEBUG", rotation="100 KB", compression="zip")


tg.main() #Запуск бота