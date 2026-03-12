### Hexlet tests and linter status:
[![Actions Status](https://github.com/ddanillu/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/ddanillu/python-project-52/actions)

### Quality Status
[![Python CI](https://github.com/ddanillu/python-project-52/actions/workflows/build.yml/badge.svg)](https://github.com/ddanillu/python-project-52/actions/workflows/build.yml)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ddanillu_python-project-52&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ddanillu_python-project-52)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=ddanillu_python-project-52&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ddanillu_python-project-52)

### Available Application
Здесь вы можете посмотреть результат:
[Link to the application](https://python-project-52-yx53.onrender.com)

### Описание проекта

Task Manager — учебное Django‑приложение в стиле классического таск‑трекера.  
Пользователь может регистрироваться, создавать задачи, назначать им статусы и метки, а также фильтровать задачи по различным параметрам.

### Основной стек

- **Backend**: Django 6
- **База данных**: SQLite (по умолчанию), PostgreSQL на проде
- **Frontend**: Django templates + `django-bootstrap5`
- **Инфраструктура**: Render, GitHub Actions, SonarQube, Rollbar, WhiteNoise

### Локальный запуск

```bash
uv sync              # установка зависимостей
cp .env.example .env # при наличии шаблона, либо создайте .env вручную
uv run manage.py migrate
uv run manage.py runserver
```

Минимальный набор переменных окружения (файл `.env`):

```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ROLLBAR_ACCESS_TOKEN=your-rollbar-token  # опционально
```

### Полезные команды Makefile

- **Установка зависимостей**: `make install`
- **Проверка стиля (ruff)**: `make lint`
- **Запуск тестов**: `make test`
- **Покрытие тестами + отчёт**: `make test-coverage`


### Доступные функции

- Регистрация и аутентификация пользователей.
- Создание, редактирование и удаление задач.
- Назначение статусов и меток задачам.
- Фильтрация задач по параметрам, таким как статус и метки.
- Интеграция с Rollbar для отслеживания ошибок.

### Тестирование

Тестирование приложения обеспечивается с помощью встроенных тестов Django:

- Для запуска тестов используйте команду:
  ```bash
  make test

- Вы также можете увидеть отчёт о покрытии, используя:
  ```bash
  make test-coverage