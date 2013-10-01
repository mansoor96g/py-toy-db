## Py-Toy-DB - Python Toy DataBase

Pure-Python "игрушечная" *документо-ориентированная СУБД*.

[Подробнее в Wiki](https://github.com/astynax/py-toy-db/wiki)

Работа с Depository
===================

    >>> from pytoydb.depository import Depository

Пример наших данных которые мы собираемся хранить.
Их может быть много и разных:

    >>> class MyDataCls(object):
    ...     a=1

Данные

    >>> my_data = {'my_awesome_record':{'first_field':1, 'last_field':'1'}}

создадим хранилище

    >>> dep = Depository()

добавление

    >>> dict_id = dep.add(my_data)

Получение

    >>> dep.get(dict_id)
    {'my_awesome_record': {'first_field': 1, 'last_field': '1'}}

удаление

    >>> dep.remove(dict_id)

    >>> dep.get(dict_id)
    Traceback (most recent call last):
        ...
    DepositoryException: запись с идентификатором 4 не найдена
