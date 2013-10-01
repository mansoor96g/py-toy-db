# -*- coding: utf-8 -*-

import abc

from functools import wraps

from storage import Storage
from config import IO_BACKEND, IO_PURPOSE_INDEX


class Index(object):
    """
    Базовый класс для конструирования индексов
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, config, name):
        self.config = config
        self.name = name

    def _make_buffer(self, suffix=None):
        # Возвращает новый буфер ввода-вывода, запрашивая его у IO-backend`а.
        # :suffix - опциональный суффикс для дополнительных буферов
        return self.config[IO_BACKEND](
            self.config,
            IO_PURPOSE_INDEX, # назначение - индекс
            '%s%s.idx' % (
                self.name,
                ('-%s' % suffix) if suffix else ''
            ))

    @abc.abstractmethod
    def query(self, *args, **kwargs):
        """
        Метод возвращает [id] объектов, подходящих по параметрам выборки
        """
        return set()

    @abc.abstractmethod
    def indexate(self, obj, id_):
        """
        Метод дополняет индекс данными по объекту
        """
        pass

    @abc.abstractmethod
    def forget(self, id_):
        """
        Метод очищает от данных по объекту
        """
        pass

    def vacuum(self):
        """
        Метод запускает оптимизацию хранилища индекса
        """
        pass


def _lazy(meth):
    # Декоратор, перестраивающий индекс перед вызовом
    # оборачиваемого метода, если индекс ещё не построен
    @wraps(meth)
    def inner(self, *args, **kwargs):
        if self._index is None:
            self._build()
        return meth(self, *args, **kwargs)
    return inner


class HashIndex(Index):
    """
    Индекс, опирающийся на результаты работы функции hash
    совместно с функцией-селектором.
    """

    def __init__(self, config, name, selector=lambda x: x):
        super(HashIndex, self).__init__(config, name)
        self._selector = selector
        self._storage = Storage('LL', self._make_buffer())

        # словарь для получения позиции в буфере по id объекта
        self._id_to_pos = None
        # словарь списков id обхектов,
        # ключи которого - результаты вычисления hash(selector(x))
        self._index = None

    def _build(self):
        # построение индекса из буфера
        self._id_to_pos = {}
        self._index = {}
        for pos, (id_, hash_) in enumerate(self._storage):
            self._id_to_pos[id_] = pos
            self._index.setdefault(hash_, []).append(id_)

    @_lazy
    def indexate(self, data, id_):
        if id_ in self._id_to_pos:
            raise ValueError('Object with id="%s" already indexed!' % id_)

        hash_ = hash(self._selector(data)) # ключ индекса
        self._index.setdefault(hash_, []).append(id_)
        self._id_to_pos[id_] = self._storage.add((id_, hash_))

    @_lazy
    def forget(self, id_):
        if id_ not in self._id_to_pos:
            raise ValueError('Object with id="%s" is not indexed!' % id_)

        for l in self._index.values():
            try:
                l.remove(id_)
            except ValueError:
                pass

        self._storage.remove(self._id_to_pos[id_])
        del self._id_to_pos[id_]

    @_lazy
    def query(self, val):
        return self._index.get(hash(val), [])
