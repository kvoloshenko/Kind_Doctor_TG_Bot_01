import requests
import re
import codecs
import urllib.request
from bs4 import BeautifulSoup
from loguru import logger
import tiktoken

def get_google_url(url: str) -> str:
    """
    Extracting the document ID from the Google Doc URL and
    creating new url for the text document format
    @param url: Source url value
    @return: Result url value
    """

    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    # print (f'math_={match_}')
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)
    # print (f'doc_id={doc_id}')
    new_url = 'https://docs.google.com/document/d/' + doc_id + '/export?format=txt'
    # print(f'new_url={new_url}')
    return new_url


def load_document_g(url):
    """
    Downloading a document from Google Drive
    @param url: The url modified by get_google_url() function
    @return: Text content of the document
    """
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def load_document_text(url: str) -> str:
    """
    Downloading a document from Google Drive with check the public read access
    @param url: The url modified by get_google_url() function
    @return: Text content of the document
    """
    logger.debug(requests.get('https://httpbin.org/ip').json())
    text = ''
    try:
        # Download the document as plain text
        response = requests.get(url)
        response.raise_for_status()
        if 'text/plain' in response.headers['Content-Type']:
            logger.debug('Правильный доступ к документу!')
            text = response.text
        else:
            raise ValueError('Invalid Google Docs URL')
            logger.error('Нет доступа к документу анонимным пользователям')
            logger.error(f'!!! No access to the document by anonymous users !!!')

    except Exception as e:  # обработка ошибок requests.exceptions.HTTPError: 404 Client Error: Not Found for url
        logger.error(f'!!! load_document_text error: {str(e)}')
        return 'No access to the document by anonymous users'
        # sys.exit(1)

    return text


def load_text(file_path):
    """
    Loading text from the local file
    @param file_path:
    @return: Text content of the file
    """
    # Открытие файла для чтения
    with codecs.open(file_path, "r", encoding="utf-8", errors="ignore") as input_file:
        # Чтение содержимого файла
        content = input_file.read()
    return content

# Функции для работы с файлом
def write_to_file(file_data, file_name):
    """
    Writing data to a file
    @param file_data:
    @param file_name:
    @return:
    """
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(file_data)

def append_to_file(new_line, file_name):
    """
    Adding data to an existing file
    @param new_line:
    @param file_name:
    @return:
    """
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write('\n' + new_line)


def split_text(text, max_length):
    """
    Splitting a line into parts with a carriage return
    @param text:
    @param max_length:
    @return:
    """
    words = text.split()  # Разделяем строку на слова
    result = []  # Список для результата

    current_line = ""  # Текущая строка
    for word in words:
        if len(current_line) + len(word) <= max_length:  # Если добавление слова не превышает максимальную длину
            current_line += word + " "  # Добавляем слово и пробел к текущей строке
        else:
            result.append(current_line.strip())  # Добавляем текущую строку в результат без лишних пробелов
            current_line = word + " "  # Начинаем новую строку с текущим словом

    if current_line:  # Если осталась незавершенная строка
        result.append(current_line.strip())  # Добавляем незавершенную строку в результат

    return '\n'.join(result)  # Возвращаем результат, объединяя строки символом перевода строки

def num_tokens_from_messages(messages, model):
    """Возвращает количество токенов, используемых списком сообщений."""
    try:
        encoding = tiktoken.encoding_for_model(model) # Пытаемся получить кодировку для выбранной модели
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base") # если не получается, используем кодировку "cl100k_base"
    if model == "gpt-3.5-turbo-0301" or "gpt-3.5-turbo-0613" or "gpt-3.5-turbo-16k" or "gpt-3.5-turbo":
        num_tokens = 0 # начальное значение счетчика токенов
        for message in messages: # Проходимся по каждому сообщению в списке сообщений
            num_tokens += 4  # каждое сообщение следует за <im_start>{role/name}\n{content}<im_end>\n, что равно 4 токенам
            for key, value in message.items(): # итерация по элементам сообщения (роль, имя, контент)
                num_tokens += len(encoding.encode(value)) # подсчет токенов в каждом элементе
                if key == "name":  # если присутствует имя, роль опускается
                    num_tokens += -1  # роль всегда требуется и всегда занимает 1 токен, так что мы вычитаем его, если имя присутствует
        num_tokens += 2  # каждый ответ начинается с <im_start>assistant, что добавляет еще 2 токена
        return num_tokens # возвращаем общее количество токенов
    else:
      # Если выбранная модель не поддерживается, генерируем исключение
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}. # вызываем ошибку, если функция не реализована для конкретной модели""")
