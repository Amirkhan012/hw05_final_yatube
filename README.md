# Yatube социальна сеть для блогеров
### Описание
Yatube - это социальная сеть, предоставляющая платформу для обмена мнениями и взаимодействия с другими пользователями. С помощью Yatube вы можете подписываться на интересных вам пользователей, оставлять комментарии под их публикациями, а также вступать в группы с общими интересами.
### Технологии
Python 3.6
Django 2.2.19
### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- В папке с файлом manage.py выполните команду для создания файлов миграции:
```
python manage.py makemigrations
``` 
- В папке с файлом manage.py выполните команду для миграции базы данных:
```
python manage.py migrate
``` 
- В папке с файлом manage.py выполните команду для запуска сервера:
```
python manage.py runserver
```
