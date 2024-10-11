Telegram-бот для автоматизированного мониторинга статусов

Этот Telegram-бот автоматически отслеживает статусы задач, делая запросы к внешнему API, и отправляет обновления пользователю в реальном времени через Telegram. Бот регулярно проверяет статусы, ведет логи и уведомляет о критических ошибках, чтобы пользователь был всегда в курсе изменений.

 Основные функции

	•	 Автоматическая проверка статусов: Регулярно отправляет запросы к API для мониторинга статусов с настраиваемым интервалом.
	•	 Уведомления в реальном времени: Отправляет обновления в Telegram при изменении статуса.
	•	 Обработка ошибок и логирование: Детализированное логирование с уведомлением о критических ошибках.
	•	 Ротация логов: Эффективное управление журналами для предотвращения переполнения.



## 🛠️ Стек технологий

[![Python3.10](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Telegram API](https://img.shields.io/badge/-Telegram%20API-2CA5E0?style=flat-square&logo=telegram)](https://core.telegram.org/bots/api)
[![Requests](https://img.shields.io/badge/-Requests-FF9900?style=flat-square&logo=python&logoColor=white)](https://docs.python-requests.org/)
[![dotenv](https://img.shields.io/badge/-dotenv-00C851?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/python-dotenv/)
[![Logging](https://img.shields.io/badge/-Logging-4682B4?style=flat-square&logo=python)](https://docs.python.org/3/library/logging.html)

Скопируй этот блок в свой README.md для отображения стека технологий.

📦 Установка

	1.	Клонируйте репозиторий:

git clone https://github.com/yourusername/telegram-bot-status-monitor.git


	2.	Создайте файл .env в корне проекта и добавьте в него следующие переменные:

TELEGRAM_TOKEN=<ваш-токен-бота>
PRACTICUM_TOKEN=<ваш-API-токен>
TELEGRAM_CHAT_ID=<ID-чата-в-Telegram>


	3.	Установите зависимости:

pip install -r requirements.txt



▶️ Запуск

Запустите бота командой:

python bot.py

Бот будет автоматически проверять API каждые 10 минут (по умолчанию) и уведомлять о любых изменениях статуса задачи.

Логирование

Логи сохраняются в файл main.log, с поддержкой ротации для предотвращения переполнения. Критические ошибки также отправляются в указанный чат Telegram.

Как это работает

	•	Бот отправляет запросы к внешнему API для проверки статусов задач.
	•	При изменении статуса формирует сообщение и отправляет его в Telegram.
	•	Обрабатываются исключения, ведется логирование как информационных сообщений, так и ошибок.

💡 Вклад

Приветствуются любые предложения и улучшения! Вы можете форкнуть репозиторий, создать новую ветку и отправить pull request.
