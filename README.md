﻿# SMTP-client

Версия 1.0

Автор: Старостина Виктория (victory13.99@gmail.com)

## Описание
Приложение реализует передачу исходящей почты по протоколу SMTP с возможностью отправки писем нескольким адресатам (cc, bcc). Также в приложении можно указать тип содержимого письма (plain/html), добавить вложения, поменять их названия и отправить их архивом. Приложение автоматически реализует отправку большого файла(>8 Мб) по частям в отдельных письмах.
#### Требования
 PyQt версии 5
#### Запуск приложения
Графическая версия: python GUI.py

## Состав
#### Модули приложения
- smtp.py - реализация соединения с SMTP-сервером
- mail.py - создание письма
- GUI.py - графическая версия приложения
- /tests - тесты
