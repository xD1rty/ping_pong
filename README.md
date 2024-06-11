# ping_pong
Игра внутри Telegram бота

Играй в пинг-понг прям в телеграмме

Для установки нужны библиотеки из .txt файла
```
pip install -r requirements.txt
```

После чего в файле app.py вставьте токен бота

```python
19 | bot = Bot(token="ВОТ ТУТ", parse_mode=ParseMode.MARKDOWN) # Сам бот
```

И по желанию в db/__init__.py заменить URL в базу

```python
6 |  db_url='sqlite://db.sqlite3',
```

И после ввести заветную команду
```
python3 app.py # Linux, MacOS
py app.py # Windows
```

