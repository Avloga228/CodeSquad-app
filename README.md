# CinemaTicket — Сайт для продажу квитків у кінотеатр
Наш проєкт — це вебдодаток, що дозволяє користувачам переглядати розклад фільмів та купувати квитки онлайн.

## Технолії 
- HTML5, JavaScript 
- Фреймворк: Django (бекенд і шаблони)
- Фронтенд: Django templates + Vanilla JavaScript
- Бекенд: Python
- База даних: SQLite
- GitHub для контролю версій

## Структура проєкту
(поки не визначена)

## Як запустити локально
1. Клонуйте репозиторій:
```bash
git clone https://github.com/Avloga228/CodeSquad-app.git
cd CodeSquad-app
```

2. Створіть віртуальне середовище python та активуйте його
```bash
python -m venv env
```
Активація середовища (для Windows):
```bash
.\env\Scripts\activate
```
Активація середовища (для Unix та MacOS систем):
```bash
env/bin/activate 
```

3. Встановіть залежності
```bash
pip install -r requirements.txt
```

4. Проведіть міграцію
```bash
python manage.py migrate
```

## Використання
1. Запустіть сервер розробника
```bash
python manage.py runserver
```
2. Вебсайт буде доступним за посиланням:
```bash
http://localhost:8000
```

## Як вносити зміни? (Для розробників)
1. Створити нову гілку (git checkout -b feature/improvement)
2. Зробити зміни
3. Закомітити їх ( git commit -am 'Add new feature')
4. Занести у гілку (git push origin feature/improvement)
5. Створити новий Pull Request.

## Розробники
- Avloga228 (Павло Чабанов)
- SviatoslavPylyshchyshyn (Святослав Пилищишин)
- 6NTRC6 (Тимків Назар)
