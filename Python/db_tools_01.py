import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
import re
from tools_01 import get_google_url, load_text, write_to_file, load_document_text
from loguru import logger


def get_db_file_name(ba, db_dir_name):
    """
    Getting the index db file name
    @param ba: Billing account name
    @return: The index db file name
    """
    db_file_name = db_dir_name + 'db_file_' + ba
    return db_file_name

def get_knowledge_base_file_name(ba, db_dir_name):
    """
    Getting the knowledge base file name
    @param ba: Billing account name
    @return: The index db file name
    """
    db_file_name = db_dir_name + 'knowledge_base_' + ba + '.txt'
    return db_file_name

def get_prompt_file_name(ba, db_dir_name):
    """
    Getting the prompt file name
    @param ba: Billing account name
    @return: The index db file name
    """
    db_file_name = db_dir_name + 'prompt_' + ba + '.txt'
    return db_file_name

def get_source_chunks(knowledge_base_text, chunk_size):
    """
    Getting all source chunks for the text knowledge base
    @param knowledge_base_text:
    @param chunk_size:
    @return: source_chunks, chunk_num
    """
    source_chunks = []
    splitter = CharacterTextSplitter(separator="\n", chunk_size=chunk_size, chunk_overlap=0)
    for chunk in splitter.split_text(knowledge_base_text):
        source_chunks.append(Document(page_content=chunk, metadata={}))

    chunk_num = len(source_chunks)
    check_source_chunks(source_chunks, chunk_size) #Checking for large chunks
    return source_chunks, chunk_num

def check_source_chunks(source_chunks, chunk_size):
    """
    Checking for large chunks
    @param source_chunks:
    @param chunk_size:
    @return:
    """
    for chunk in source_chunks:  # Поиск слишком больших чанков
        if len(chunk.page_content) > chunk_size:
            logger.error(f'*** Слишком большой кусок! ***')
            logger.error(f'chunk_len ={len(chunk.page_content)}')
            logger.error(f'content ={chunk.page_content}')


def get_knowledge_base_txt(ba, data_files_type, knowledge_base_url, db_dir_name ):
    """
    Getting the knowledge base text
    @param data_files_type:
    @param ba:
    @param knowledge_base_url:
    @return: The prompt text
    """
    logger.error(f'ba ={ba}')
    logger.error(f'data_files_type ={data_files_type}')
    logger.error(f'knowledge_base_url ={knowledge_base_url}')
    logger.error(f'db_dir_name ={db_dir_name}')
    knowledge_base_file_name = get_knowledge_base_file_name(ba, db_dir_name)
    logger.error(f'knowledge_base_file_name ={knowledge_base_file_name}')
    if data_files_type == 'local':
        knowledge_base_text = load_text(knowledge_base_file_name)
        return knowledge_base_text
    else:
        knowledge_base_url = get_google_url(knowledge_base_url)
        knowledge_base_text = load_document_text(knowledge_base_url)  # Загрузка файла с Базой знаний
        write_to_file(knowledge_base_text, knowledge_base_file_name)
        return knowledge_base_text

def create_db(ba, knowledge_base_text, db_dir_name, chunk_size, embeddings):
    """
    Creating the index db and it's db file from the text source
    @param knowledge_base_text:
    @param ba:
    @return:
    """
    # logger.debug(f'knowledge_base_text={knowledge_base_text}')
    db_file_name = get_db_file_name(ba, db_dir_name)
    logger.debug(f'db_file_name={db_file_name}')
    source_chunks, chunk_num = get_source_chunks(knowledge_base_text, chunk_size)
    logger.debug(f'chunk_num={chunk_num}')

    try:
        db = FAISS.from_documents(source_chunks, embeddings) # Создадим индексную базу из разделенных фрагментов текста
        db.save_local(db_file_name)
    except Exception as e: # обработка ошибок openai.error.RateLimitError
        logger.error(f'!!! External error: {str(e)}')

    return db, db_file_name, chunk_num

def load_db(ba, embeddings, db_dir_name, type, chunk_size):
    """
    Loading the index db from it's file
    @param db_file_name:
    @return:
    """
    db_file_name = get_db_file_name(ba, db_dir_name)
    logger.debug(f'db_file_name={db_file_name}')
    # Инициализирум модель эмбеддингов
    if not os.path.exists(db_file_name):
        db_file = db_file_name + '.txt'
        knowledge_base_text = get_knowledge_base_txt(ba, type, db_file, db_dir_name)
        new_db, db_file_name, chunk_num = create_db(ba, knowledge_base_text, db_dir_name, chunk_size, embeddings)
    else:
        new_db = FAISS.load_local(db_file_name, embeddings, allow_dangerous_deserialization=True)
    return new_db

def get_message_content(topic, index_db, NUMBER_RELEVANT_CHUNKS):
    """
    Getting relevant chunks for the topic from the index db
    @param topic:
    @param index_db:
    @param NUMBER_RELEVANT_CHUNKS:
    @return:
    """
    docs = index_db.similarity_search(topic, k = NUMBER_RELEVANT_CHUNKS)
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\n#### Document excerpt №{i+1}####\n' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    return message_content


# Функция получения релевантных чанков (фрагметов) по теме из индексной базы данных с оценкой
def get_message_content_with_score(topic, score_level, index_db, k):
    docs = index_db.similarity_search_with_score(topic, k = k)
    message_content = ''
    i = 0
    for d in docs:
      score = d[1]
      if score > score_level:
        i += 1
        message_content = message_content + f'\n#### Document excerpt №{i}####\n' + d[0].page_content + '\n'

    print(f'i={i}')
    if i > 0:
      return message_content
    else:
      return 'Данные на найдены в Базе Знаний'