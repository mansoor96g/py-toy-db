## Py-Toy-DB - Python Toy DataBase

Pure-Python "игрушечная" *документо-ориентированная СУБД*.[eng](*document-oriention DB*)

[Подробнее в Wiki](https://github.com/astynax/py-toy-db/wiki)

## Примеры использования[eng](Examples of using)

### Работа с Depository

    >>> from pytoydb.depository import Depository
    >>> from pytoydb.config import configure

Пример наших данных которые мы собираемся хранить.
Их может быть много и разных:[eng](An example of our data that we are going to store.
There can be many and different:)
    >>> class MyDataCls(object):
    ...     a=1

Данные[eng](Data)

    >>> my_data = {'my_awesome_record':{'first_field':1, 'last_field':'1'}}

создадим хранилище[eng](create storage)

    >>> dep = Depository(configure())

добавление[eng](adding)

    >>> dict_id = dep.add(my_data)

Получение[eng](Getting)

    >>> dep.get(dict_id)
    {'my_awesome_record': {'first_field': 1, 'last_field': '1'}}

удаление[eng](removing)

    >>> dep.remove(dict_id)

    >>> dep.get(dict_id)
    Traceback (most recent call last):
        ...
    IndexError: Запись с идентификатором 1 не найдена


### Работа с IndexedDepository[eng](Working with Indexed Depository)

Импорты:[eng](import)

    >>> from pytoydb.depository import IndexedDepository
    >>> from pytoydb.index import HashIndex
    >>> from pytoydb.config import configure
    >>> from pprint import pprint

Создаем хранилище:[eng](Create a repository:)

    >>> dep = IndexedDepository(
    ...     configure(
    ...         indexes=(
    ...             ('a', HashIndex, (lambda x: x.get('a'),)),
    ...             ('b', HashIndex, (lambda x: x.get('b'),))
    ...         )
    ...     ))

Добавляем записи (возвращаются *id* записей):[eng](Add records (* id * records are returned):)

    >>> dep.add({'a': 1, 'b': 101})
    1
    >>> dep.add({'a': 2, 'b': 102, 'c': 456, 2: 4})
    2
    >>> dep.add({'a': 1, 'b': 103})
    3
    >>> dep.add({'a': 3})
    4
    >>> dep.add({'a': 2, 'b': 101, 101: 'b'})
    5

Теперь можно делать выборки по запросам:

    >>> show = lambda x: pprint(list(x))
    >>> show( dep.query )
    [(1, {'a': 1, 'b': 101}),
     (2, {2: 4, 'a': 2, 'b': 102, 'c': 456}),
     (3, {'a': 1, 'b': 103}),
     (4, {'a': 3}),
     (5, {101: 'b', 'a': 2, 'b': 101})]

    >>> show( dep.query('a', 1) )
    [(1, {'a': 1, 'b': 101}), (3, {'a': 1, 'b': 103})]

    >>> show( dep.query('a', 2) )
    [(2, {2: 4, 'a': 2, 'b': 102, 'c': 456}), (5, {101: 'b', 'a': 2, 'b': 101})]

    >>> show( dep.query('b', 101) )
    [(1, {'a': 1, 'b': 101}), (5, {101: 'b', 'a': 2, 'b': 101})]

Запросы можно сохранять, но нужно помнить, что они *ленивые*, и выполняются только при итерации по объекту запроса:

    >>> q = dep.query('a', 2)('b', 101)
    >>> show(q)
    [(5, {101: 'b', 'a': 2, 'b': 101})]
    >>> dep.remove(5)
    >>> show(q)
    []

### Работа с ThreadsafeDepository

    >>> from pytoydb.depository import ThreadsafeDepository
    >>> from pytoydb.config import configure

Создаем экземпляр хранилища и запускаем его. По-умолчанию будем работать в памяти.

    >>> dep = ThreadsafeDepository(configure())
    >>> dep.start()

Определим клиента (поток), который будет работать с хранилицем.

    >>> import threading
    >>> class Client(threading.Thread):
    ...     def __init__(self, depository):
    ...         threading.Thread.__init__(self)
    ...         self.dep = depository
    ...     def run(self):
    ...         while True:
    ...             print self.dep.add({'test':'test'}, wait=True)
    ...             print self.dep.add({'test':'test'})

Запуск нескольких экземпляров

    >>> for i in range(5):
    ...    Client(dep).start()

