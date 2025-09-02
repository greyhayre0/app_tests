# Полный способ.
> [!CAUTION]
> Все команды нужно выполнять из корня проекта.

### Установите Docker и Docker Compose или Docker.desktop.
- <https://docs.docker.com/compose/install/>

### Среда разработки - последовательно выполни команды:
- 'python -m venv venv'
- 'source venv/Scripts/activate'

### Установи зависимости.
- 'pip install -r requirements.txt.'

### Выполни команду
- 'docker-compose up --build'

# Быстрый старт.
### Установите Docker и Docker Compose или Docker.desktop.
- <https://docs.docker.com/compose/install/>
### В корне выполни команду
- 'docker-compose up --build'


* Фронтэнд адрес <http://localhost:8000>
* API <http://localhost:8000/docs>
* Хост пример <https://app-tests-1.onrender.com/>

> [!CAUTION]
> По умолчанию версия для локального запуска. При необходимости зайди в database.py и раскометируй деплой. Где SQLALCHEMY_DATABASE_URL прячет твои контакты на сервере.