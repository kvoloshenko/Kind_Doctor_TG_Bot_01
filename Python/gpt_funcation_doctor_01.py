from config import *
import os
from dotenv import load_dotenv
from loguru import logger
from datetime import datetime, timedelta, timezone
import json
import pprint
import tools_01 as tls
import db_tools_01 as dbt
from langchain_openai import OpenAIEmbeddings
from chat_history_01 import set_user_history, get_user_history, reset_user_history
import openai
from openai import OpenAI
# from openai import AsyncOpenAI

# Get the current date and time
current_datetime = datetime.now(tz=timezone(timedelta(hours=3)))
# Format the date and time as a string
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
csvfilename = "Logs/" + formatted_datetime + "_answers.csv"

load_dotenv()

# Загрузка значений из .env
API_KEY = os.environ.get("API_KEY")
os.environ["OPENAI_API_KEY"] = API_KEY
openai.api_key = API_KEY

client = OpenAI(api_key=openai.api_key)    # Обычный клиент
# client = AsyncOpenAI(api_key=openai.api_key) # Асинхронный клиент

logger.debug(f'BA={BA}')
logger.debug(f'LL_MODEL = {LL_MODEL}')

# CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE")) # Количество токинов в  чанке
logger.debug(f'CHUNK_SIZE={CHUNK_SIZE}')

# NUMBER_RELEVANT_CHUNKS = int(os.environ.get("NUMBER_RELEVANT_CHUNKS"))   # Количество релевантных чанков
logger.debug(f'NUMBER_RELEVANT_CHUNKS={NUMBER_RELEVANT_CHUNKS}')

# TEMPERATURE = float(os.environ.get("TEMPERATURE")) # Температура модели
logger.debug(f'TEMPERATURE={TEMPERATURE}')
logger.debug(f'SYSTEM_DOC_URL = {SYSTEM_DOC_URL}')
logger.debug(f'KNOWLEDGE_BASE_URL = {KNOWLEDGE_BASE_URL}')
logger.debug(f'DATA_FILES = {DATA_FILES}')
logger.debug(f'DB_DIR_NAME = {DB_DIR_NAME}')
logger.debug(f'DATA_REGISTRATION_FILE={DATA_REGISTRATION_FILE}')

REGISTRATION_NUMBER = 0 # Номер регистрационной записи

# Записывам в файл заголовок
tls.write_to_file('user_id;user_name;question;answer', csvfilename)

HISTORY = {}  # Словарь для хранения памяти

def get_prompt_txt(type=DATA_FILES, ba=BA, SYSTEM_DOC_URL=SYSTEM_DOC_URL):
    """
    Getting the prompt text
    @param type:
    @param ba:
    @param system_doc_url:
    @return: The prompt text
    """
    prompt_file_name = dbt.get_prompt_file_name(ba, DB_DIR_NAME)
    logger.debug(f'prompt_file_name={prompt_file_name}')
    if type == 'local':
        system = tls.load_text(prompt_file_name)
        return system
    else:
        system_doc_url = tls.get_google_url(SYSTEM_DOC_URL)
        system = tls.load_document_text(system_doc_url)  # Загрузка файла с Промтом
        tls.write_to_file(system, prompt_file_name)
        return system

# Инструкция для GPT, которая будет подаваться в system
system = get_prompt_txt()
logger.debug(f'system={system}')

# Создание индексной базы знаний
embeddings = OpenAIEmbeddings()
db = dbt.load_db(BA, embeddings, DB_DIR_NAME, DATA_FILES, CHUNK_SIZE)

# Перезагрузка
def reload_data():
    global REGISTRATION_NUMBER
    global HISTORY
    system = get_prompt_txt(type='NotLocal', ba=BA)
    knowledge_base_text = dbt.get_knowledge_base_txt(type='NotLocal', ba=BA)
    db, db_file_name, chunk_num = dbt.create_db(knowledge_base_text=knowledge_base_text, ba=BA)
    REGISTRATION_NUMBER = 0  # Номер регистрационной записи
    HISTORY = {}
    return system, db


# Функция записи рагистрации вызова врача
def fillout_google_form(user_id,
                        last_name,
                        first_name,
                        patronymic,
                        phone_number,
                        age,
                        condition,
                        information,
                        data_registration_file = DATA_REGISTRATION_FILE):
    global REGISTRATION_NUMBER
    logger.debug(f'user_id={user_id}')
    logger.debug(f'last_name={last_name}')
    logger.debug(f'first_name={first_name}')
    logger.debug(f'patronymic={patronymic}')
    logger.debug(f'phone_number={phone_number}')
    logger.debug(f'age={age}')
    logger.debug(f'condition={condition}')
    logger.debug(f'information={information}')
    logger.debug(f'data_registration_file={data_registration_file}')

    if not os.path.exists(data_registration_file):
        logger.debug(f'Файл отсутствует')
        tls.write_to_file('user_id;registration_number;last_name;first_name;patronymic;phone_number;age;condition;information', data_registration_file)
    REGISTRATION_NUMBER += 1
    line_for_file = f'"{user_id}";"{REGISTRATION_NUMBER}";"{last_name}";"{first_name}";"{patronymic}";"{phone_number}";"{age}";"{condition}";"{information}"'
    tls.append_to_file(line_for_file, data_registration_file)
    logger.debug(f'Обращение зарегистрировано под номером {REGISTRATION_NUMBER}')
    reset_user_history(user_id) #Очистка истории чата для указанного пользователя
    return json.dumps({"registration_number": REGISTRATION_NUMBER})


# объявление функции для модели
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fillout_google_form",
            "description": "Get the current date and time,  user's last name, first name and  patronymic, information about his simptoms and write all these data for registration. ",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user id, e.g. 12345",
                    },
                    "last_name": {
                        "type": "string",
                        "description": "user's last name, e.g. Иванов",
                    },
                    "first_name": {
                        "type": "string",
                        "description": "user's first name, e.g. Иван",
                    },
                    "patronymic": {
                        "type": "string",
                        "description": "user's patronymic, e.g. Иванович",
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "user's phone number, e.g. +7021-777-77-77",
                    },
                    "age": {
                        "type": "string",
                        "description": "patient's age in years, e.g. 56, 77",
                    },
                    "condition": {
                        "type": "string",
                        "description": "patient's condition, e.g. острое или нормальное",
                    },
                    "information": {
                        "type": "string",
                        "description": "information about user's simptoms, e.g. высокая температура, рвота, голова болит",
                    },
                },
                "required": ["user_id", "last_name", "first_name", "patronymic", "phone_number", "age", "condition", "information"],
            },
        },
    }
]

# Запрос в ChatGPT с функцией
async def get_answer_gpt_func(system, topic, index_db, user_id, user_name, temp=TEMPERATURE, tools=TOOLS):
    # Get the current date and time
    current_datetime = datetime.now(tz=timezone(timedelta(hours=3)))
    # Format the date and time as a string
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    ch, memory = get_user_history(user_id) # читаем историю чата для указанного пользователя
    # logger.debug(f'The chat history before={ch}')
    # Поиск релевантных отрезков из базы знаний
    message_content = dbt.get_message_content(topic, index_db, NUMBER_RELEVANT_CHUNKS)
    # logger.debug(f'message_content={message_content}')
    user_content = f"user_id is {user_id}\n" \
                   f"Here is the document with information to respond to the client: " \
                   f"{message_content}\n\n " \
                   f"Here is the client's question: \n{topic}" \
                   f"Here is the chat history: \n {ch} \n" \
                   f"Here is current date and tyme: {formatted_datetime}"
    # logger.debug(f'user_content={user_content}')
    # Шаг 1. Инициализировать разговор с помощью сообщения пользователя.
    logger.debug(f'Шаг 1. Инициализировать разговор с помощью сообщения пользователя')
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content}
    ]

    # Шаг 2. Отправить в модель контекст разговора и доступные функции.
    logger.debug(f'Шаг 2. Отправить в модель контекст разговора и доступные функции')
    response = client.chat.completions.create(     # Обычный клиент
    # response = await client.chat.completions.create( # Асинхронный клиент
        model=LL_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_num = 1
    # Извлекаем ответ модели
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls  # Для провеки, хочет ли модель вызывать какую-либо функцию

    logger.debug(f'Шаг 3: Проверяем, есть ли какие-либо вызовы функций, выполненные моделью')
    # Шаг 3: Проверяем, есть ли какие-либо вызовы функций, выполненные моделью.
    if tool_calls:
        available_functions = {
            "fillout_google_form": fillout_google_form,
        }
        # Добавляем ответ модели в историю разговора
        messages.append(response_message)
        logger.debug(f'Шаг 4: Вызов функции, запрошенной моделью')
        # Шаг 4: Вызов функции, запрошенной моделью
        i4 = 0
        logger.debug(f'tool_calls = {tool_calls}')
         # for tool_call in tool_calls: # Так не делаем, т.к. бывает более одного срабатывания для той-же функции
        tool_call = tool_calls[0]
        logger.debug(f'tool_call = {tool_call}')
        i4 += 1
        logger.debug(f'Шаг 4: {i4}')
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)

        # Вызов функции с извлеченными аргументами
        function_response = function_to_call(
            user_id      = function_args.get("user_id"),
            last_name    = function_args.get("last_name"),
            first_name   = function_args.get("first_name"),
            patronymic   = function_args.get("patronymic"),
            phone_number = function_args.get("phone_number"),
            age          = function_args.get("age"),
            condition    = function_args.get("condition"),
            information  = function_args.get("information"),
        )

        # Добавляем ответ функции в историю разговора
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )
        logger.debug(f'Шаг 5: Продолжаем разговор с обновленной историей')
        # Шаг 5: Продолжаем разговор с обновленной историей
        second_response = client.chat.completions.create(     # Обычный клиент
        # second_response = await client.chat.completions.create( # Асинхронный клиент
            model=LL_MODEL,
            messages=messages,
        )  # Получаем новый ответ от модели, где она сможет увидеть ответ функции.

        response = second_response
        response_num = 2

    answer = response.choices[0].message.content

    if response_num == 1:
        logger.debug(f'response_num={response_num}')
        set_user_history(user_id, topic, answer) # Сохраняем историю чата для user_id
        ch, memory = get_user_history(user_id)
        logger.debug(f'The chat history after={ch}')

    line_for_file = '"' + user_id + '";"' + user_name + '";"' + topic + '";"' + answer + '"'
    tls.append_to_file(line_for_file, csvfilename)
    return answer, response

async def answer_user_question(topic, user_name, user_id):
    ans, completion = await get_answer_gpt_func(system, topic, db, user_id, user_name)  # получите ответ модели с функцие
    return ans




