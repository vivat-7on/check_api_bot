# Бот-ассистент для Практикум.Домашка
Этот Telegram-бот поможет вам узнать статус вашей домашней работы на сайте Практикум.Домашка. Он будет автоматически запрашивать информацию о вашей работе и оповещать вас о её статусе.
## Установка и запуск
1. Клонируйте репозиторий на свой компьютер.
2. Создайте бота в Telegram и получите его токен.
3. Создайте файл `.env` в корне проекта и добавьте в него следующие строки:
```
TELEGRAM_TOKEN=<ваш токен>
PRAKTIKUM_TOKEN=<токен API Практикум.Домашка>
PRAKTIKUM_HW_ID=<ID вашей домашней работы>
```
4. Установите необходимые зависимости, введя команду `pip install -r requirements.txt`.
5. Запустите бота командой `python bot.py`.
## Использование
Бот раз в 10 минут опрашивает API сервис Практикум.Домашка и проверят статус отправленной на ревью домашней работы.
При обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram.
## Автор
яндекс.практикум, Валерчик