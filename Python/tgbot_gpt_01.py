from config import *
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from tools_01 import split_text
import os
# import gpt_funcation_doctor_01 as chat_gpt
from loguru import logger

# возьмем переменные окружения из .env
load_dotenv()
# загружаем значеняи из файла .env
TOKEN = os.environ.get("TOKEN")
logger.debug(f'TEXT_BEGINNING = {TEXT_BEGINNING}')
logger.debug(f'BOT_START_REPLY={BOT_START_REPLY}')
print('Команда для обновления данных: ##reload##')
logger.debug(f'TEXT_END = {TEXT_END}')

if QUESTION_FILTER is None:
    QUESTION_FILTER = ""

# функция команды /start
async def start(update, context):
    logger.debug(f'{BOT_START_REPLY}')
    await update.message.reply_text(BOT_START_REPLY)

# функция для текстовых сообщений
async def text(update, context):
    # использование update
    logger.debug(f'message.date={update.message.date}')
    logger.debug(f'message.message_id={update.message.message_id}')
    logger.debug(f'message.from_user.first_name={update.message.from_user.first_name}')
    logger.debug(f'message.from_user.id={update.message.from_user.id}')
    logger.debug(f'message.text={update.message.text}')
    logger.debug('-------------------')
    user_name = update.message.from_user.first_name
    user_id = update.message.from_user.id
    topic = update.message.text
    topic_splited = split_text(topic, 40) # Разбиени строки переводом коретки
    logger.debug(f'text: {topic_splited}')

    question_filter_len = len (QUESTION_FILTER)
    topic_first_n = topic[:question_filter_len]

    chat_type = update.message.chat.type

    if (QUESTION_FILTER == topic_first_n) or (chat_type == 'private'):
        if topic=='##reload##':
            # обновление промта и базы знаний
            # TODO
            # chat_gpt.system, chat_gpt.db = chat_gpt.reload_data()
            reply_text = 'Данные обновлены!'
        else:
            # TODO
            reply_text = "The answer is a stub"
            # reply_text = chat_gpt.answer_user_question(topic, user_name, str(user_id))

        response = TEXT_BEGINNING + '\n'
        response = response + reply_text + '\n' + TEXT_END
        await update.message.reply_text(f'{response}')
        reply_text_splited = split_text(reply_text, 40) # Разбиени строки переводом каретки
        logger.debug(f'reply_text_splited={reply_text_splited}')
        logger.debug('-------------------')


def main():

    # точка входа в приложение
    application = Application.builder().token(TOKEN).build()
    logger.debug('Бот запущен..!')

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # запуск приложения (для остановки нужно нажать Ctrl-C)
    application.run_polling()

    logger.debug('Бот остановлен..!')


if __name__ == "__main__":
    main()