import os
import sys
import time
import requests
import logging
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import telegram
from dotenv import load_dotenv

from exceptions import RequestApiError

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


class TelegramErrorHandler(logging.Handler):
    """Обработчик для логера отправки сообщения в Telegram."""

    def emit(self, record):
        """Отправляет сообщение об ошибке в Telegram, если уровень записи.
        превышает или равен уровню ERROR.
        Принимает объект записи лога (record) и
        отправляет соответствующее сообщение.
        """
        if record.levelno >= logging.ERROR:
            log_entry = self.format(record)
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            bot.send_message(TELEGRAM_CHAT_ID, log_entry)


logging.basicConfig(
    level=logging.INFO,
    format=_format)
logger = logging.getLogger(__name__)
telegram_handler = TelegramErrorHandler()
telegram_handler.setFormatter(logging.Formatter(_format))
telegram_handler.setLevel(logging.ERROR)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(_format))
stream_handler.setLevel(logging.ERROR)

logger.addHandler(stream_handler)
logger.addHandler(telegram_handler)
logger.addHandler(get_file_handler())


def check_tokens():
    """Проверяет доступность переменных окружения.
    которые необходимы для работы программы.
    Возвращает True, если все переменные окружения доступны,
    иначе возвращает False.
    """
    required_tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for token in required_tokens:
        if token is None:
            error_message = f"Отсутствует переменная окружения: {token}"
            logger.critical(error_message)
            sys.exit(1)
    logger.info('Переменные окружения на месте!')


def send_message(bot, message):
    """Отправляет сообщение в Telegram.
    Принимает экземпляр класса Bot и строку с текстом сообщения.
    """
    logger.info('Вызвана send_message().')
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.debug('Сообщение успешно отправлено в Telegram')


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
        if homework_statuses.status_code == HTTPStatus.OK:
            logger.info('Запрос к API практикума вернулся с кодом 200!')
            return homework_statuses.json()
        else:
            logger.error(
                f'Ошибка при запросе к API: '
                f'{homework_statuses.status_code} - '
                f'{homework_statuses.text}'
            )
            raise RequestApiError("Ошибка при запросе к API")
    except Exception as error:
        logger.error(error)
        raise Exception('Неожиданный результат запроса к API')


def check_response(response) -> None:
    """Проверяет ответ API на соответствие документации.
    Возвращает True или False, в зависимости от результата.
    """
    if not isinstance(response, dict):
        raise TypeError('Ответ не является словарём!')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('По ключу "homeworks" возвращается не список')
    logger.info('Ответ прошёл проверку!')
    return True


def parse_status(homework):
    """Извлекает статус проверки работы из ответа API и.
    возвращает строку с описанием статуса.
    Принимает элемент списка статусов работ.
    """
    if 'status' not in homework:
        error_message = 'Отсутствует статус работы в ответе API'
        raise ValueError(error_message)
    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        error_message = f'Неизвестный статус работы: {status}'
        raise ValueError(error_message)
    verdict = HOMEWORK_VERDICTS[status]
    if 'homework_name' not in homework:
        error_message = 'Отсутствует ключ "homework_name"'
        raise ValueError(error_message)
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

            if not check_response(response):
                continue

            homeworks = response.get('homeworks')
            if homeworks is None:
                error_sent = False
                continue

            homework, *_ = homeworks
            message = parse_status(homework)
            if message:
                try:
                    send_message(bot, message)
                    logger.info('Сообщение отправлено!')
                except telegram.error.TelegramError as error:
                    message = f'Сбой в работе программы: {error}'
                    logging.error(message)

            error_sent = False

        except Exception as error:
            if not error_sent:
                logger.error('Произошла ошибка', error)
                error_sent = True

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
