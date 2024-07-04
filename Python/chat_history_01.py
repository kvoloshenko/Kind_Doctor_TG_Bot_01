from langchain.memory import ConversationBufferMemory
from loguru import logger
import pprint

HISTORY = {} # Словарь для хранения памяти

# Функция чтения истории чата для указанного пользователя
def get_user_history(user_id):
  global HISTORY
  m = HISTORY.get(user_id, '*')
  if m == '*':
    logger.debug(f'Для пользователя {user_id} отсутствует история чата')
    question = '####'
    answer = '####'
    memory = ConversationBufferMemory()
    memory.chat_memory.add_user_message(question)
    memory.chat_memory.add_ai_message(answer)
    c = memory.load_memory_variables({})
  else:
    c = m.load_memory_variables({})
    pprint.pprint(c)
    memory = m
  return c, memory

# Функция записи истории чата для указанного пользователя
def set_user_history(user_id, question, answer):
  global HISTORY
  c, memory = get_user_history(user_id)
  # memory = ConversationBufferMemory()
  memory.chat_memory.add_user_message(question)
  memory.chat_memory.add_ai_message(answer)
  HISTORY.update({user_id: memory})

# Очистка истории чата для указанного пользователя
def reset_user_history(user_id):
  global HISTORY
  del HISTORY[user_id]
  logger.debug(f'Для пользователя {user_id} очищена история чата')
