import os
import time
import requests
import logging
import sys

import telegram
from dotenv import load_dotenv

from logging.handlers import RotatingFileHandler
from telegram_handler import TelegramLoggingHandler

load_dotenv()

PRACTICUM_TOKEN: str = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: dict = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

_format = ('%(asctime)s - '
           '[%(levelname)s]- '
           '%(name)s - '
           '(%(filename)s).%(funcName)s(%(lineno)d) - '
           '%(message)s')


def get_file_handler():
    """Возвращает обработчик файлового лога."""
    file_handler = RotatingFileHandler(
        'main.log',
        mode='w',
        maxBytes=50000000,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_format))
    return file_handler


def get_message_handler():
    """Возвращает обработчик сообщений для вывода в stdout."""
    message_handler = logging.StreamHandler(sys.stdout)
    message_handler.setLevel(logging.ERROR)
    message_handler.setFormatter(logging.Formatter(_format))
    return message_handler


def get_telegram_handler():
    """Возвращает обработчик сообщений для отправки в Telegram."""
    telegram_handler = TelegramLoggingHandler(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    telegram_handler.setLevel(logging.ERROR)
    telegram_handler.setFormatter(logging.Formatter(_format))
    return telegram_handler


def get_logger(name=__name__):
    """Возвращает логгер с настроенными обработчиками."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_message_handler())
    logger.addHandler(get_telegram_handler())
    return logger


logger = get_logger()


def check_tokens():
    """Проверяет доступность переменных окружения.
    которые необходимы для работы программы.
    Возвращает True, если все переменные окружения доступны,
    иначе возвращает False.
    """
    required_tokens = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
    for token in required_tokens:
        if not os.getenv(token):
            error_message = f"Отсутствует переменная окружения: {token}"
            logger.critical(error_message)
            raise ValueError(error_message)
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram.
    Принимает экземпляр класса Bot и строку с текстом сообщения.
    """
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Сообщение успешно отправлено в Telegram')
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения в Telegram: {error}')


def get_api_answer(timestamp) -> dict:
    """Делает запрос к API.
    В качестве параметра передается временная метка.
    В случае успешного запроса должна возвращает ответ API,
    приведённый к типам данных Python из формата JSON .
    """
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        if homework_statuses.status_code == 200:
            return homework_statuses.json()
        else:
            logger.error(
                f'Ошибка при запросе к API: '
                f'{homework_statuses.status_code} - '
                f'{homework_statuses.text}'
            )
            raise Exception("Ошибка при запросе к API")
    except Exception as error:
        logger.error(error)
        raise Exception('Неожиданный результат запроса к API')


def check_response(response) -> None:
    """Проверяет ответ API на соответствие документации.
    Возвращает True или False, в зависимости от результата.
    """
    if not isinstance(response, dict):
        logging.error('Ответ не является словарём!')
        raise TypeError('Ответ не является словарём!')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        logging.error('По ключу "homeworks" возвращается не список')
        raise TypeError('По ключу "homeworks" возвращается не список')


def parse_status(homework):
    """Извлекает статус проверки работы из ответа API и.
    возвращает строку с описанием статуса.
    Принимает элемент списка статусов работ.
    """
    if 'homework_name' not in homework:
        error_message = 'Отсутствует ключ `homework_name` в ответе API'
        logger.error(error_message)
        raise ValueError(error_message)
    if 'status' not in homework:
        error_message = 'Отсутствует статус работы в ответе API'
        logger.error(error_message)
        raise ValueError(error_message)
    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        error_message = f'Неизвестный статус работы: {status}'
        logger.error(error_message)
        raise ValueError(error_message)
    verdict = HOMEWORK_VERDICTS[status]
    homework_name = homework.get('homework_name')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    error_sent = False
    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response.get('current_date')
            if check_response(response):
                message = parse_status(response)
                if message:
                    send_message(bot, message)
                    logger.debug('Сообщение отправлено!')
                error_sent = False
            else:
                error_sent = False
        except Exception as error:
            if not error_sent:
                logger.exception('Произошла ошибка', exc_info=error)
                send_message(
                    bot,
                    'Произошла ошибка при получении и '
                    'обработке информации от API'
                )
                error_sent = True
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
