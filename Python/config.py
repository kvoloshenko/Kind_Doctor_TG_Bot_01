SYSTEM_DOC_URL = '***'            # Промпт
KNOWLEDGE_BASE_URL = '***'        # База Знаний
# SYSTEM_DOC_LOCAL = '/content/drive/MyDrive/_AI/Signs_Symptoms/Doc/SYSTEM_DOC.txt'
# KNOWLEDGE_BASE_LOCAL = '/content/drive/MyDrive/_AI/Signs_Symptoms/Doc/KNOWLEDGE_BASE.txt'
TEMPERATURE = 0.8                 # Температура модели
NUMBER_RELEVANT_CHUNKS = 5        # Количество релевантных чанков
CHUNK_SIZE = 2048                 # Количество токинов в  чанке
LL_MODEL = 'gpt-4o-2024-05-13'    # Модель shapshot
# LL_MODEL = 'gpt-4o'             # Модель
# LL_MODEL = "gpt-3.5-turbo-0301" # Модель
# LL_MODEL = "gpt-4"              # Модель
# LL_MODEL = "gpt-3.5-turbo-0613" # Модель
# LL_MODEL = "gpt-3.5-turbo-16k"  # Модель
# LL_MODEL = "gpt-3.5-turbo"      # Модель
TEXT_BEGINNING = '*** С Вами общается автоматический бот: ***'
TEXT_END = '*** Уточняйте информацию у Вашего врача! ***'
QUESTION_FILTER = '@userVccTest01bot'
DB_DIR_NAME = 'Db/'
BA = 'doctor'
BOT_START_REPLY = 'Добрый день! Я - Добродоктор, Ваш виртуальный консультант. Чем могу помочь?'
DATA_FILES = 'local'
DATA_REGISTRATION_FILE = 'Reg_data/data_registration_file.csv'