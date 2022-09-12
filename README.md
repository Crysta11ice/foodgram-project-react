# FOODGRAM

[![Django-app workflow](https://github.com/Crysta11ice/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/Crysta11ice/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Описание проекта
Foodgram — это продуктовый помощник: сайт, на котором пользователи могут ознакомиться с чужими рецептами приготовления блюд или поделиться собственными. Кроме того, при помощи сервиса «Список покупок» у пользователей есть возможность создавать списки продуктов, необходимых для приготовления выбранных блюд.

### Функционал
Онлайн-сервис с API позволяет пользователям:
- публиковать собственные рецепты
- подписываться на публикации других пользователей
- добавлять понравившиеся рецепты в список «Избранное»
- создавать и скачивать сводный список продуктов, соответствующих выбранным рецептам.

## Сайт
[![Foodgram](http://foodgramhelper.ddnsking.com/)](http://foodgramhelper.ddnsking.com/)

## Самостоятельный запуск проекта
1. Скачать проект на локальный пк
```
git clone https://github.com/Crysta11ice/foodgram-project-react
```
2. Скачать и установить Docker:
https://www.docker.com/
3. Запустить docker-compose:
```
cd foodgram-project-react/infra
docker-compose up -d --build
```
4. Применить миграции:
```
docker-compose exec backend python manage.py migrate
```
5. Создать суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
6. Загрузить ингредиенты и файлы статики:
```
sudo docker-compose exec backend python manage.py ingr_import
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
7. Готово!

## Автор проекта
[Crysta11ice](https://github.com/Crysta11ice) — Backend разработка, деплой.